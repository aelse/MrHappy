from botplugin import BotPlugin

class Speak(BotPlugin):

    def command_say(self, bot, command, args, nick):
        bot.speak(args)
