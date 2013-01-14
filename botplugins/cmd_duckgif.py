from botplugin import BotPlugin

all_gifs = [
    'http://i.imgur.com/ZCpaZ.jpg'
]
gifs = []


def get_duckgif():
    import random
    global gifs
    if not len(gifs):
        gifs = list(all_gifs)
        random.shuffle(gifs)
    return gifs.pop()


class DuckGif(BotPlugin):

    def command_duckgif(self, bot, command, args, nick):
        bot.speak(get_duckgif())
