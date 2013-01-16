from botplugin import BotPlugin

all_gifs = [
    'http://i.minus.com/iNN3m7EHPMNWl.gif',
]
gifs = []


def get_camelgif():
    import random
    global gifs
    if not len(gifs):
        gifs = list(all_gifs)
        random.shuffle(gifs)
    return gifs.pop()


class CamelGif(BotPlugin):

    def command_camelgif(self, bot, command, args, nick):
        bot.speak(get_camelgif())
