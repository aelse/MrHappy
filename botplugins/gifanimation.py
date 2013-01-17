import re
from botplugin import BotPlugin

all_gifs = {
    'antelope': [
        'http://www.datgif.com/wp-content/uploads/2012/07/biker-hit-by-antelope.gif',
    ],
    'camel': [
        'http://i.minus.com/iNN3m7EHPMNWl.gif',
    ],
    'duck': [
        'http://i.imgur.com/ZCpaZ.jpg'
    ],
    'gorilla': [
        'http://24.media.tumblr.com/tumblr_m4s9fzX57L1rwcc6bo1_250.gif',
    ],
    'pigeon': [
        'http://gifs.gifbin.com/1601003555.gif',
    ],
}
gifs = {}


def get_gif(which):
    import random
    global gifs
    if which not in gifs or not len(gifs[which]):
        gifs[which] = list(all_gifs[which])
        random.shuffle(gifs[which])
    return gifs[which].pop()


class GifAnimation(BotPlugin):

    def listen(self, bot, message):
        if message[u'type'] != u'TextMessage':
            return

        # Attempt to strip out URLs
        msg = re.sub('(https?|ftp)://\S+', '', message['body'])

        m = re.search('([a-zA-Z]+)gif', msg)
        if m:
            which = m.groups()[0]
            global all_gifs
            if which in all_gifs:
                bot.speak(get_gif(which))
