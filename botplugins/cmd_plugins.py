from botplugin import BotPlugin

class PluginOperations(BotPlugin):

    def command_unload(self, bot, e, command, args, channel, nick):
        if args == 'plugins':
            bot.reply('Unloading all plugins.', channel, nick)
            for plugin in list(bot.plugins):
                if plugin != self:
                    bot.unload_plugin(plugin)
            #bot.unload_plugin(self)

    def command_reload(self, bot, e, command, args, channel, nick):
        if args == 'plugins':
            self.command_unload(bot, e, command, args, channel, nick)
            bot.unload_plugin(self)
            bot.reply('Loading all plugins.', channel, nick)
            bot.load_modules()
