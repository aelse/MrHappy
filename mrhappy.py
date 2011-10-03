import os
import sys
import logging

from ircbot import SingleServerIRCBot

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
    },
    'Channel': {
    }
}

class MrHappyBot(SingleServerIRCBot):
    def __init__(self, server, channels, nick, name, nickpass=None, recon=60):
        SingleServerIRCBot.__init__(self, [server], nick, name, recon)
        global conf
        self.nick = nick
        self.name = name
        self.join_channels = channels

    def get_version(self):
        global version
        return "MrHappy v" + version

    def on_welcome(self, c, e):
        log_info('Joining channels')
        for channel in self.join_channels:
            log_debug('Joining %s' % channel)
            c.join(channel)

def log_msg(msg, log_level=logging.INFO):
    logging.log(log_level, msg)

def log_info(msg):
    global conf
    if conf['verbose']:
        log_msg(msg, logging.INFO)

def log_debug(msg):
    global conf
    if conf['debug']:
        log_msg(msg, logging.DEBUG)

def log_error(msg):
        log_msg(msg, logging.ERROR)

def parse_options():
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-v", "--verbose", dest="verbose", default=False,
        action="store_true",
        help="print verbose status information")
    parser.add_option("-d", "--debug", dest="debug", default=False,
        action="store_true",
        help="print debugging information")
    parser.add_option("-c", "--config", dest="config_file", metavar="FILE",
        default="mrhappy.cfg",
        help="bot configuration file")
    parser.add_option("-g", "--gen-config", dest="gen_config", default=False,
        action="store_true",
        help="generate a bot configuration file")
    (options, args) = parser.parse_args()
    return options

def process_config(filename):
    from ConfigParser import SafeConfigParser
    global conf
    log_debug('Using configuration file %s' % filename)

    parser = SafeConfigParser()
    parser.read(filename)

    for section in parser.sections():
        for (name, value) in parser.items(section):
            log_debug('%s => %s = %s' % (section, name, value))
            conf[section][name] = value

def gen_config():
    """
    Generate a sample configuration object.
    """
    global conf
    log_info('Generating sample configuration')
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
    return config

def main():
    global conf
    options = parse_options()
    conf['debug'] = options.debug
    if options.debug:
        options.verbose = True
    conf['verbose'] = options.verbose

    if options.gen_config:
        config = gen_config()
        config.write(sys.stdout)
        return 0

    if not os.path.exists(options.config_file):
        log_error('No such configuration file: %s' % options.config_file)
        return 1
    process_config(options.config_file)

    server = (conf['Server']['host'], int(conf['Server']['port']))
    channels = conf['Channel'].values()
    bot = MrHappyBot(server, channels, conf['General']['nick'], conf['General']['name'])
    try:
        log_info('Starting Bot')
        bot.start()
    except KeyboardInterrupt:
        log_info('Received ctrl-c')
        bot.connection.quit("Terminating")
    except Exception, e:
        logging.exception(e)
        bot.connection.quit("Exception")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
