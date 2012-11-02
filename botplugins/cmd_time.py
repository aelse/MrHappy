from botplugin import BotPlugin
import time

class CommandTime(BotPlugin):

    def command_time(self, bot, command, args, nick):
        bot.speak(time.asctime())
