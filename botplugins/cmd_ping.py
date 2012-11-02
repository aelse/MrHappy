from botplugin import BotPlugin


class CommandPing(BotPlugin):

    def command_ping(self, bot, command, args, nick):
        bot.speak('Pong!', paste=True)
