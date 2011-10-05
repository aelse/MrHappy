from botplugin import BotPlugin
import time

class CommandTime(BotPlugin):

    def command_time(self, bot, e, command, args, channel, nick):
        bot.reply(time.asctime(), channel, nick)
