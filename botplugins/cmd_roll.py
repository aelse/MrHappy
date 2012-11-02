from botplugin import BotPlugin
import logging
import threading
import random

class RollForIt(BotPlugin):

    config_options = {
        'roll_delay': '30',
        'max_roll': '100',
    }

    def setup(self, bot, options):
        self.timer = None
        self.channel = ''
        self.rollers = []
        self.bot = bot
        try:
            self.roll_delay = int(options['roll_delay'])
        except:
            self.roll_delay = 30
        try:
            self.max_roll = int(options['max_roll'])
        except:
            self.max_roll = 100

    def teardown(self):
        if self.timer:
            self.timer.cancel()
            if self.timer.isActive():
                logging.warning('Could not cancel roll timer')
            self.timer = None

    def command_roll(self, bot, command, args, channel, nick):
        # Private request for a new roll is invalid
        if not channel and not self.timer:
            bot.speak('Roll in a channel')
            return

        # Request for a roll while a roll is going
        if self.timer and channel != self.channel:
            bot.speak('Resolving current roll. Try again in %d seconds.' % self.roll_delay)
            return

        # Start a new roll
        if not self.timer:
            logging.debug('%s started a roll.' % nick)
            bot.speak('Starting a new roll. Do \'/msg %s roll\' to join.' % bot.nickname)
            bot.speak('Roll resolves in %d seconds.' % self.roll_delay)
            self.channel = channel
            self.rollers = [nick]
            self.timer = threading.Timer(self.roll_delay, self.perform_roll)
            self.timer.start()
        else:
            if nick in self.rollers:
                bot.speak('%s is already in the roll.' % nick)
            else:
                logging.debug('added %s to the roll.' % nick)
                bot.speak('Adding %s to the roll.' % nick)
                self.rollers.append(nick)

    def perform_roll(self):
        self.timer = None
        big_roll = 0
        big_roller = ''
        tie_breaker = False
        for roller in self.rollers:
            my_roll = random.randint(1, self.max_roll)
            self.bot.speak(self.channel, '%s rolls %d.' % (roller, my_roll))
            if my_roll > big_roll:
                big_roll = my_roll
                big_roller = roller
                tie_breaker = False
            elif my_roll == big_roll:
                # tie breaker
                if random.randint(0, 1):
                    big_roller = roller
                    tie_breaker = True
        if tie_breaker:
            self.bot.speak('Winner by tiebreaker is %s.' % big_roller)
        else:
            self.bot.speak('Winner is %s.' % big_roller)
