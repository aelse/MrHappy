from botplugin import BotPlugin
import logging
import xml.dom.minidom
import requests
import urllib
import re

class Jenkins(BotPlugin):

    config_options = {
        'jenkins_url': 'http://jenkins',
        'status_msg_limit': '-1',
        'username': '',
        'password': '',
    }

    def setup(self, bot, options):
        self.jenkins_url = None
        try:
            self.jenkins_url = options['jenkins_url']
        except KeyError:
            logging.warning('Must provide a jenkins url like http://jenkins')
        self.proj_matcher = re.compile('[\w\d\-_\.]+')
        # limit lines of information to be reported for a request
        self.status_msg_limit = -1
        try:
            self.status_msg_limit = int(options['status_msg_limit'])
        except:
            logging.warning('Invalid status_msg_limit')

        if 'username' in options:
            self.username = options['username']

        if 'password' in options:
            self.password = options['password']

    def command_jenkins(self, bot, command, arguments, nick):
        arguments = arguments.strip()

        # Provide help information if no sub-command given
        if len(arguments) == 0:
            arguments = 'help'

        # work out the given sub-command and arguments
        if arguments.find(' ') > -1:
            cmd, args = arguments.split(' ', 1)
        else:
            cmd, args = arguments, ''

        if self.jenkins_url is None and cmd != 'help':
            bot.speak('No configured jenkins server')
            return

        f = None
        try:
            f = getattr(self, 'cmd_' + cmd)
        except AttributeError:
            pass

        if f:
            message = f(args)
            bot.speak(message, paste=True)
        else:
            bot.speak('Bad arguments \'%s\'' % (arguments))

    def cmd_help(self, args):
        help = {
            'help': 'Print this message',
            'buildstatus <project>': 'Report on project build',
        }
        msg = ''
        for cmd, info in help.items():
            msg += '{:<25} - {}\n'.format(cmd, info)
        return msg

    def cmd_buildstatus(self, proj_name):
        if not self.proj_matcher.match(proj_name):
            return 'Badly formatted project %s' % proj_name
        return gen_build_info(self.jenkins_url, self.username, self.password, proj_name, self.status_msg_limit)


def fetch_url(url, username, password):
    try:
        response = requests.get(url, auth=(username, password))
        if response.ok:
            return response.text
    except:
        pass
    return None

def gen_build_info(jenkins_url, username, password, proj_name, limit=-1):
    url = '%s/job/%s/rssAll' % (jenkins_url, proj_name)
    rss = fetch_url(url, username, password)
    if not rss:
        return ['Unable to fetch build information']

    xml_data = xml.dom.minidom.parseString(rss)

    # locate build entries
    entries = xml_data.getElementsByTagName('entry')

    count = 0
    buildstatus = 'Builds for %s\n' % proj_name
    for e in entries:
        updated = e.getElementsByTagName('updated')[0].lastChild.nodeValue
        title = e.getElementsByTagName('title')[0].lastChild.nodeValue
        buildstatus += '{}: {}\n'.format(updated, title)
        count += 1
        if count == limit:
            break
    return buildstatus

if __name__ == '__main__':
    import sys
    jenkins_url = sys.argv[1]
    proj_name = sys.argv[2]
    for line in gen_build_info(jenkins_url, proj_name):
        print line
