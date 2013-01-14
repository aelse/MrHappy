from botplugin import BotPlugin

all_gifs = [
    'http://gifs.gifbin.com/1601003555.gif',
]
gifs = []


def get_pigeongif():
    import random
    global gifs
    if not len(gifs):
        gifs = list(all_gifs)
        random.shuffle(gifs)
    return gifs.pop()


class PigeonGif(BotPlugin):

    def command_pigeongif(self, bot, command, args, nick):
        bot.speak(get_pigeongif())
