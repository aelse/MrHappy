import os
from botplugin import BotPlugin

gifs = []


def get_doggif():
    import random
    global gifs
    if not len(gifs):
        fname = os.path.join(os.path.dirname(__file__), 'doggif.txt')
        f = open(fname, 'r')
        gifs = f.read().split()
        f.close()
        random.shuffle(gifs)
    return gifs.pop()


class DogGif(BotPlugin):

    def command_doggif(self, bot, command, args, nick):
        bot.speak(get_doggif())


def page_generator():
    import requests
    url = 'http://fuckyeahdoggifs.tumblr.com/page/%d'
    page_num = 1
    finished = False
    while not finished:
        r = requests.get(url % page_num)
        if r.ok:
            yield r.text
        else:
            finished = True
        page_num += 1

def generate_gif_list():
    from BeautifulSoup import BeautifulSoup
    import re
    doggif_urls = []
    pages = page_generator()
    for page in pages:
        s = BeautifulSoup(page)
        images = s.findAll('img')
        for image in images:
            url = image.get('src')
            if re.search('\.gif$', url):
                doggif_urls.append(url)
        if len(images) < 5:  # beyond final page
            break
    return doggif_urls

if __name__ == '__main__':
    doggif_urls = generate_gif_list()
    f = open('botplugins/doggif.txt', 'w')
    f.write('\n'.join(doggif_urls))
    f.close()
