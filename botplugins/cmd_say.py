from botplugin import BotPlugin

class Speak(BotPlugin):

    def command_say(self, bot, command, args, channel, nick):
        bot.speak(args)
