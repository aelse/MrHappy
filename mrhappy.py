#!/usr/bin/python
#
# MrHappy is a Campfire bot.
# Copyright Alexander Else, 2011-2012.
#
# This file is part of MrHappy.
#
# MrHappy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MrHappy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MrHappy.  If not, see <http://www.gnu.org/licenses/>.
#
# This project uses code from ircbot-collection which is also released
# under a GPL licence.

import os
import sys
import string
import logging
from logging import debug, info, warn, error
from threading import Thread, Event
import multiprocessing
import re

from pinder import Campfire

version = "0.1"

# Defaults for bot configuration. Only contains entries where a default
# value is needed. Anything else must come from configuration file, and
# anything in the configuration file will override these defaults.
conf = {
    'General': {
        'nick': 'MrHappy',
        'name': 'MrHappy, the python bot.',
    },
    'Server': {
        'campfire_prefix': 'mrhappy',
        'token': 'your token here',
        'room': 'MrHappy',
    },
}


class CampfireConnection():
    connection = None
    subdomain = None
    token = None
    room_name = None
    room = None

    def connect(self):
        self.connection = Campfire(self.subdomain, self.token)
        self.room = self.connection.find_room_by_name(self.room_name)
        self.room.join()

    def __init__(self, subdomain, token, room_name):
        self.subdomain = subdomain
        self.token = token
        self.room_name = room_name
        self.connect()

    def send(self, msg, paste):
        try:
            if paste:
                self.room.paste(msg)
            else:
                self.room.speak(msg)
        except:
            print 'Oh no, caught an exception talking to the room'

    def quit(self, reason):
        if reason:
            try:
                self.room.speak('Quitting: %s' % reason)
            except:
                print 'Oh no, caught an exception talking to the room'
        self.room.leave()


class OutputManager(Thread):

    def __init__(self, connection, delay=.5):
        Thread.__init__(self)
        self.setDaemon(1)
        self.connection = connection
        self.delay = delay
        self.event = Event()
        self.queue = []

    def run(self):
        import time
        while 1:
            self.event.wait()
            while self.queue:
                msg, paste = self.queue.pop(0)
                self.connection.send(msg, paste)
                time.sleep(self.delay)
            self.event.clear()

    def send(self, msg, paste):
        self.queue.append((msg.strip(), paste))
        self.event.set()


class MrHappyBot(object):
    def __init__(self, token, campfire_prefix, room, nick, name):
        self.connection = CampfireConnection(campfire_prefix, token, room)
        self.queue = OutputManager(self.connection, .2)
        self.queue.start()
        self.nickname = nick
        self.name = name
        self.plugins = []

        self.cfusers = {}

    def start(self):
        self.connection.room.listen(self.handle_msg, self.ex_handler)

    def handle_msg(self, msg):
        if msg['body'] is None:
            return
        uid = msg['user_id']
        if not uid in self.cfusers:
            try:
                u = self.connection.connection.user(uid)
                self.cfusers[uid] = u['user']['name']
            except:
                pass

        try:
            from_nick = self.cfusers[uid]
        except:
            print 'Could not get nick'
            from_nick = 'Oops'

        info('Received from %s: %s' % (from_nick, msg['body']))
        m = re.match('%s[:,](.*)' % self.nickname, msg['body'], re.IGNORECASE)
        if m:
            cmd = m.groups()[0]
            info('Command: %s' % cmd)
            self.do_command(string.strip(cmd), string.strip(from_nick))

        # Pass the message to all listeners
        self.do_listeners(msg)

    def ex_handler(self, ex):
        #self.shutdown('Exception %s' % ex)
        info('Exception %s' % ex)
        self.connection.connect()
        try:
            self.room.speak('Exception: %s' % ex)
            self.room.speak('Please let me live!')
            self.room.join()
        except:
            print 'Oh no, caught an exception talking to the room'
        try:
            self.room.join()
        except:
            print 'Oh no, caught an exception joining the room'
        return

    def shutdown(self, reason=None):
        plugins = list(self.plugins)
        for p in plugins:
            self.unload_plugin(p)
        self.connection.quit(reason)

    def load_modules(self):
        modules = discover_modules(self.conf['plugindir'])
        for m in modules:
            mpath = self.conf['plugindir'].replace('/', '.')
            modname = string.join((mpath, m), '.')
            self.load_plugin(modname)

    def setup_plugins(self):
        for p in self.plugins:
            plugin_config = {}
            section_name = 'plugin_' + p.module_barename
            try:
                plugin_config = self.conf[section_name]
            except KeyError:
                debug('No configuration section \'%s\' for %s' % (
                      section_name, p.module_barename))
            p.setup(self, plugin_config)

    def load_plugin(self, modname):
        from botplugins.botplugin import BotPlugin
        debug('Inspecting %s' % modname)
        plugin = __import__(modname)
        d = plugin.__dict__
        barename = modname[modname.rfind('.') + 1:]
        d = d[barename].__dict__

        discovered = []
        for key, entry in d.items():
            if key.startswith('__'):
                continue
            t = str(type(entry)).split("'")[1]
            if t == 'classobj' and issubclass(entry, BotPlugin):
                if key != BotPlugin.__name__:
                    info('Loading plugin %s' % key)
                    discovered.append(entry())

        for p in discovered:
            p.module_barename = barename
            self.plugins.append(p)

    def unload_plugin(self, plugin):
        plugin.teardown()
        try:
            self.plugins.remove(plugin)
        except ValueError:
            warning('Attempted to remove unregistered plugin')

    def speak(self, text, paste=False):
        """
        Send text to channel
        """
        self.queue.send(text, paste)

    def do_command(self, cmd, nick):
        """
        Receive command messages.
        """
        debug('Received a command')

        # Guarantee plugins a single space between args
        cmd = re.sub('\s\s+', ' ', cmd.strip())

        if(cmd.find(' ') > -1):
            command, args = cmd.split(' ', 1)
        else:
            command, args = cmd, ''
        command = command.lower()

        # must operate on copy of list in case self.plugins changes
        # in the course of handling commands (ie. plugins reload).
        plugins = list(self.plugins)
        for plugin in plugins:
            f = None
            try:
                f = getattr(plugin, 'command_' + command.lower())
            except AttributeError:
                pass

            if f:
                f(self, command, args, nick)

    def do_listeners(self, msg):
        """
        Listeners receive all messages.
        """
        plugins = list(self.plugins)
        for plugin in plugins:
            f = None
            try:
                f = getattr(plugin, 'listen')
            except AttributeError:
                pass

            if f:
                f(self, msg)


def parse_options():
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-v", "--verbose", dest="verbose", default=False,
                      action="store_true",
                      help="print verbose status information")
    parser.add_option("-d", "--debug", dest="debug", default=False,
                      action="store_true",
                      help="print debugging information")
    parser.add_option("-l", "--logfile", dest="log_file", metavar="FILE",
                      help="log to file")
    parser.add_option("-c", "--config", dest="config_file", metavar="FILE",
                      default="mrhappy.cfg", help="bot configuration file")
    parser.add_option("-g", "--gen-config", dest="gen_config", default=False,
                      action="store_true",
                      help="generate a bot configuration file")
    parser.add_option("-p", "--plugins", dest="load_plugins", default=False,
                      action="store_true",
                      help="load plugins (or include plugin options in "
                      "--gen-config)")
    (options, args) = parser.parse_args()
    return options


def process_config(filename):
    from ConfigParser import SafeConfigParser
    global conf
    debug('Using configuration file %s' % filename)
    parser = SafeConfigParser()
    parser.read(filename)

    for section in parser.sections():
        for (name, value) in parser.items(section):
            debug('%s => %s = %s' % (section, name, value))
            if section not in conf:
                conf[section] = {}
            conf[section][name] = value


def gen_config(load_plugins):
    """
    Generate a sample configuration object.
    """
    info('Generating sample configuration')
    from ConfigParser import SafeConfigParser
    config = SafeConfigParser()
    config.add_section('General')
    config.set('General', 'nick', 'MrHappy')
    config.set('General', 'name', 'MrHappy, the Python bot.')
    config.add_section('Server')
    config.set('Server', 'campfire_prefix', 'mrhappy')
    config.set('Server', 'token', 'your token here')
    config.set('Server', 'room', 'MrHappy')

    if load_plugins:
        # bot not yet created as we have not read its configuration.
        # Instantiate a bot with skeleton config and load plugins
        global conf
        bot = MrHappyBot(conf['Server']['token'],
                         conf['Server']['campfire_prefix'],
                         conf['Server']['room'],
                         conf['General']['nick'],
                         conf['General']['name'])
        bot.conf = conf

        bot.load_modules()
        for p in bot.plugins:
            options = {}
            try:
                options = p.config_options
            except AttributeError:
                continue
            section_name = 'plugin_' + p.module_barename
            for o, v in options.items():
                if not config.has_section(section_name):
                    config.add_section(section_name)
                config.set(section_name, o, v)
    return config


def discover_modules(directory):
    modules = []
    for _, _, files in os.walk(directory):
        for f in files:
            if f.endswith('.py') and not f.startswith('__'):
                modname = f[:f.find('.')]
                modules.append(modname)
    return modules


def run_bot(conf, options):
    bot = MrHappyBot(conf['Server']['token'],
                     conf['Server']['campfire_prefix'],
                     conf['Server']['room'],
                     conf['General']['nick'],
                     conf['General']['name'])
    bot.conf = conf

    if options.load_plugins:
        bot.load_modules()
        bot.setup_plugins()

    try:
        info('Starting Bot')
        bot.start()
    except KeyboardInterrupt:
        info('Received ctrl-c')
        bot.shutdown()
        return 0
    except Exception, e:
        logging.exception(e)
        bot.shutdown()
        return 1

    return 0


def main():
    global conf
    loglevel = getattr(logging, 'WARNING')
    logformat = '%(asctime)s - %(levelname)s - %(message)s'
    conf['plugindir'] = 'botplugins'

    options = parse_options()
    conf['verbose'] = options.verbose
    if options.verbose:
        loglevel = getattr(logging, 'INFO')

    conf['debug'] = options.debug
    if options.debug:
        conf['verbose'] = True
        loglevel = getattr(logging, 'DEBUG')

    if options.log_file:
        logging.basicConfig(filename=options.log_file,
                            level=loglevel, format=logformat)
    else:
        logging.basicConfig(level=loglevel, format=logformat)

    if options.gen_config:
        config = gen_config(options.load_plugins)
        config.write(sys.stdout)
        return 0

    if not os.path.exists(options.config_file):
        error('No such configuration file: %s' % options.config_file)
        return 1
    process_config(options.config_file)

    keep_running = True
    while keep_running:
        print 'Starting campfire process'
        p = multiprocessing.Process(target=run_bot, args=(conf, options,))
        p.start()
        p.join()
        if p.exitcode == 1:
            keep_running = False
            print 'Not restarting campfire process'
        else:
            import time
            time.sleep(3)
    print 'Terminating'

    return 0


if __name__ == "__main__":
    sys.exit(main())
