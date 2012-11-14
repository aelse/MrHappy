import re
import time
from botplugin import BotPlugin

words = [
    'arse',
    'bastard',
    'bitch',
    'bugger',
    'bollocks',
    'bullshit',
    'cock',
    'crap',
    'cunt',
    'damn',
    'damnit',
    'dick',
    'douche',
    'fag',
    'fuck',
    'fucked',
    'fucking',
    'piss',
    'shit',
    'wank',
    'minge',
]


class VerbalMorality(BotPlugin):
    last_fined = 0

    # Throttle rate at which it can issue fines
    delay_before_fine = 1800

    config_options = {
        'delay_before_fine': '1800',
    }

    def setup(self, bot, options):
        try:
            self.delay_before_fine = int(options['delay_before_fine'])
        except:
            self.delay_before_fine = 1800  # seconds

    def listen(self, bot, message):
        if message[u'type'] != u'TextMessage':
            return

        # Attempt to strip out URLs
        msg = re.sub('(https?|ftp)://\S+', '', message['body'])

        fine = False
        for match_phrase in words:
            if re.search(match_phrase, msg, re.IGNORECASE):
                fine = True
        if fine:
            catch_phrase = ('You have been fined one credit for a '
                            'violation of the verbal morality statute.')
            img_url = 'http://img.gawkerassets.com/img/17pgz0g1jmd2jjpg/original.jpg'
            global last_fined
            now = time.time()
            if self.last_fined < now - self.delay_before_fine:
                # Instead of speaking to the room trigger the
                # soundcamp action
                #room.speak(catch_phrase)
                #room.speak(img_url)
                bot.speak(':soundcamp verbal')
                self.last_fined = now
