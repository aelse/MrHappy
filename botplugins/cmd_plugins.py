from botplugin import BotPlugin

class PluginOperations(BotPlugin):

    def command_unload(self, bot, command, args, channel, nick):
        if args == 'plugins':
            bot.speak('Unloading all plugins.')
            for plugin in list(bot.plugins):
                if plugin != self:
                    bot.unload_plugin(plugin)
            #bot.unload_plugin(self)

    def command_reload(self, bot, command, args, channel, nick):
        if args == 'plugins':
            self.command_unload(bot, command, args, channel, nick)
            bot.unload_plugin(self)
            bot.speak('Loading all plugins.')
            bot.load_modules()
