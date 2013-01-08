from botplugin import BotPlugin

all_gifs = [
    'http://www.datgif.com/wp-content/uploads/2012/07/biker-hit-by-antelope.gif',
]
gifs = []


def get_antelopegif():
    import random
    global gifs
    if not len(gifs):
        gifs = list(all_gifs)
        random.shuffle(gifs)
    return gifs.pop()


class AntelopeGif(BotPlugin):

    def command_antelopegif(self, bot, command, args, nick):
        bot.speak(get_antelopegif())
