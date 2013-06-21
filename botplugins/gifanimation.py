import re
from botplugin import BotPlugin

all_gifs = {
    'antelope': [
        'http://www.datgif.com/wp-content/uploads/2012/07/biker-hit-by-antelope.gif',
    ],
    'bear': [
        'http://i.imgur.com/r6dj1.jpg',
    ],
    'camel': [
        'http://i.minus.com/iNN3m7EHPMNWl.gif',
        'http://25.media.tumblr.com/tumblr_mazpigv9zx1qd74lho1_400.gif',
    ],
    'cyclone': [
        'http://i.imgur.com/9v0QDMr.gif',
    ],
    'duck': [
        'http://i.imgur.com/ZCpaZ.jpg'
    ],
    'gorilla': [
        'http://24.media.tumblr.com/tumblr_m4s9fzX57L1rwcc6bo1_250.gif',
        'http://i.imgur.com/n9f2H.gif',
    ],
    'koala': [
        'http://24.media.tumblr.com/tumblr_lqulix92EQ1r1kcfyo1_400.gif',
    ],
    'lex': [
        'https://bpl.campfirenow.com/room/525308/thumb/3995944/lexogif.gif',
    ],
    'otter': [
        'http://s3-ec.buzzfed.com/static/enhanced/webdr01/2013/2/20/11/anigif_enhanced-buzz-14268-1361377451-5.gif',
    ],
    'pigeon': [
        'http://gifs.gifbin.com/1601003555.gif',
    ],
    'sheep': [
        'http://i.imgur.com/bqR8ksG.gif',
    ],
    'wolf': [
        'http://24.media.tumblr.com/tumblr_m6lmlhq01L1r1rqulo1_500.gif',
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
