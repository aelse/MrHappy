#!/usr/bin/python
#
# MrHappy is an IRC bot.
# Copyright Alexander Else, 2011.
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
import re

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, irc_lower
import botcommon
from botplugins.botplugin import BotPlugin
from pprint import PrettyPrinter

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
        'retry_interval': '60',
        'host': 'localhost',
        'port': '6667',
    },
    'Channel': {
    }
}

class MrHappyBot(SingleServerIRCBot):
    def __init__(self, server, channels, nick, name, nickpass=None, recon=60):
        SingleServerIRCBot.__init__(self, [server], nick, name, recon)
        self.queue = botcommon.OutputManager(self.connection, .2)
        self.queue.start()
        self.nickname = nick
        self.name = name
        self.join_channels = channels
        self.plugins = []

    def shutdown(self, reason):
        plugins = list(self.plugins)
        for p in plugins:
            self.unload_plugin(p)
        self.connection.quit(reason)

    def load_modules(self):
        modules = discover_modules(self.conf['plugindir'])
        for m in modules:
            modname = string.join((self.conf['plugindir'].replace('/', '.'), m), '.')
            self.load_plugin(modname)

    def setup_plugins(self):
        for p in self.plugins:
            plugin_config = {}
            section_name = 'plugin_' + p.module_barename
            try:
                plugin_config = self.conf[section_name]
            except KeyError:
                debug('No configuration section \'%s\' for %s' % (section_name, p.module_barename))
            p.setup(self, plugin_config)

    def load_plugin(self, modname):
        debug('Inspecting %s' % modname)
        plugin = __import__(modname)
        d = plugin.__dict__
        barename = modname[modname.rfind('.')+1:]
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

    def on_privmsg(self, c, e):
        debug('Received private message')
        from_nick = nm_to_n(e.source())
        self.do_command(e, string.strip(e.arguments()[0]), string.strip(from_nick))

    def on_pubmsg(self, c, e):
        debug('Received public message')
        from_nick = nm_to_n(e.source())
        m = re.match('%s[:,](.*)' % self.nickname, e.arguments()[0], re.IGNORECASE)
        if m:
            cmd = m.groups()[0]
            self.do_command(e, string.strip(cmd), string.strip(from_nick))

    def say_public(self, channel, text):
        "Print TEXT into public channel, for all to see."
        debug('Sending public: %s' % text)
        self.queue.send(text, channel)

    def say_private(self, nick, text):
        "Send private message of TEXT to NICK."
        debug('Sending private to %s: %s' % (nick, text))
        self.queue.send(text, nick)

    def reply(self, text, to_channel, to_private=None):
        "Send TEXT to either public channel or TO_PRIVATE nick (if defined)."
        if to_channel is not None:
            self.say_public(to_channel, text)
        elif to_private is not None:
            self.say_private(to_private, text)
        else:
            warn('Trying to send a message without channel or nick')

    def get_version(self):
        global version
        return "MrHappy v" + version

    def on_welcome(self, c, e):
        info('Joining channels')
        for channel in self.join_channels:
            info('Joining %s' % channel)
            c.join(channel)

    def do_command(self, e, cmd, nick):
        debug('Received a command')
        channel = None
        if e.eventtype() == "pubmsg":
            channel = e.target()

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
                f(self, e, command, args, channel, nick)
        #self.reply('Responding to direct request.', channel, nick)

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
        default="mrhappy.cfg",
        help="bot configuration file")
    parser.add_option("-g", "--gen-config", dest="gen_config", default=False,
        action="store_true",
        help="generate a bot configuration file")
    parser.add_option("-p", "--plugins", dest="load_plugins", default=False,
        action="store_true",
        help="load plugins (or include plugin options in --gen-config)")
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
            if not conf.has_key(section):
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
    config.set('General', 'nickpass', 'mypass')
    config.add_section('Server')
    config.set('Server', 'host', 'localhost')
    config.set('Server', 'port', '6667')
    config.set('Server', 'retry_interval', '60')
    config.add_section('Channel')
    config.set('Channel', 'a', '#MrHappy\'s_Wild_Ride')
    config.set('Channel', 'b', '#testchan')

    if load_plugins:
        # bot not yet created as we have not read its configuration.
        # Instantiate a bot with skeleton config and load plugins
        global conf
        server = (conf['Server']['host'], int(conf['Server']['port']))
        bot = MrHappyBot(server, [], conf['General']['nick'], conf['General']['name'])
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
        logging.basicConfig(filename=options.log_file, level=loglevel, format=logformat)
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

    server = (conf['Server']['host'], int(conf['Server']['port']))
    channels = conf['Channel'].values()
    bot = MrHappyBot(server, channels, conf['General']['nick'], conf['General']['name'])
    bot.conf = conf

    if options.load_plugins:
        bot.load_modules()
        bot.setup_plugins()

    try:
        info('Starting Bot')
        bot.start()
    except KeyboardInterrupt:
        info('Received ctrl-c')
        bot.shutdown("Terminating")
    except Exception, e:
        logging.exception(e)
        bot.shutdown("Exception")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
