from botplugin import BotPlugin

class Speak(BotPlugin):

    def command_say(self, bot, e, command, args, channel, nick):
        bot.reply(args, channel, nick)
