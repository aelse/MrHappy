from botplugin import BotPlugin
import time

class Speak(BotPlugin):

    def command_say(self, bot, e, command, args, channel, nick):
        bot.reply(args, channel, nick)
