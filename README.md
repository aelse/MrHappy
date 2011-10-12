MrHappy
=======

Synopsis
--------

MrHappy is an IRC bot written in python. It is intended to be a
useful tool to software developers and devops.

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

The simplest plugin to add is a simple command that MrHappy will run
when asked privately or in channel. An exchange may look like:

    (ircuser) MrHappy: say hello
    (MrHappy) hello

The code for this is in botplugins/cmd_say.py
