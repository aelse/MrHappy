MrHappy
=======

Synopsis
--------

MrHappy is a Campfire bot written in python. It is intended to be a
useful tool to software developers and devops. It started life as
an IRC bot, and this still shows in some of the code, but the
advantages of Campfire for group work lead to the switch.

Bot functionality can be extended with plugins. Plugins exist
to perform such tasks as notification of changes to git repositories
and report on build results from a jenkins build server.

Usage
-----
    $ ./mrhappy.py -h
    Usage: mrhappy.py [options]
    
    Options:
      -h, --help            show this help message and exit
      -v, --verbose         print verbose status information
      -d, --debug           print debugging information
      -l FILE, --logfile=FILE
                            log to file
      -c FILE, --config=FILE
                            bot configuration file
      -g, --gen-config      generate a bot configuration file
      -p, --plugins         load plugins (or include plugin options in --gen-
                            config)


You may generate an initial configuration file by running:

    $ ./mrhappy.py -p -g

The -p is suggested as MrHappy's functionality largely comes from plugins,
and many plugins provide suggested defaults or example configuration values.

The default configuration file is mrhappy.cfg, though you may specify
an alternate file by using the -c flag.

To actually run MrHappy:

    $ ./mrhappy.py -p -c mrhappy.cfg

Plugins
-------

Most of MrHappy's functionality comes from plugins in the botplugins
directory. Further plugins may be created by extending the BotPlugin
class found in botplugins/botplugin.py

These plugins may process commands directed at the bot or can listen
to all traffic in the channel.

Listeners
=========

A listener should implement the listen method which will receive
any campfire events containing a message body.

Example

    import re
    from botplugin import BotPlugin


    class MyListener(BotPlugin):

        def listen(self, bot, e, message):
            if message[u'type'] != u'TextMessage':
                return

            bot.reply('Received: ' + message['body'], '', '')

Commands
========

The simplest plugin to add is a simple command that MrHappy will run
when asked privately or in channel. An exchange may look like:

    (Campfire user) MrHappy: say hello
    (MrHappy) You told me to say: hello

The command plugin should implement a method named command_<cmd> where
cmd is the in-chat text that should invoke the command.

An implementation of the exchange above might look like:

    from botplugin import BotPlugin


    class Speak(BotPlugin):

        def command_say(self, bot, e, command, args, channel, nick):
            bot.reply('You told me to say: ' + args, '', '')

