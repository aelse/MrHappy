from botplugin import BotPlugin
import os

class DNS(BotPlugin):

    config_options = {
        'local_git_repo_path': '',
    }

    def setup(self, bot, options):
        try:
            self.repo_path = options['local_git_repo_path']
        except:
            self.repo_path = ''

    def command_dns(self, bot, e, command, args, channel, nick):
        if args == 'update':
            result = os.system('cd {path} && {git} && {cmd}'.format(
                path=self.repo_path, git='git pull',
                cmd='python zone-updater -f'))
            if result == 0:
                bot.reply('Updated dynamic dns.', channel, nick)
            else:
                bot.reply('Got an error updating dynamic dns.',
                    channel, nick)
        else:
            bot.reply('dns update - update the dynamic zone',
                channel, nick)
