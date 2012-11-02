from botplugin import BotPlugin


class CommandPing(BotPlugin):

    def command_ping(self, bot, command, args, channel, nick):
        bot.reply('Pong!', channel, nick, paste=True)
