import os
from botplugin import BotPlugin

gifs = []


def get_catgif():
    import random
    global gifs
    if not len(gifs):
        f = open(os.path.join(os.path.dirname(__file__), 'catgif.txt'), 'r')
        gifs = f.read().split()
        f.close()
        random.shuffle(gifs)
    return gifs.pop()


class CatGif(BotPlugin):

    def command_catgif(self, bot, command, args, nick):
        bot.speak(get_catgif())


def page_generator():
    import requests
    url = 'http://www.catgifpage.com/page/%d/'
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
    catgif_urls = []
    pages = page_generator()
    for page in pages:
        s = BeautifulSoup(page)
        images = s.findAll('img')
        for image in images:
            url = image.get('src')
            if re.search('\.gif$', url):
                catgif_urls.append(url)
    return catgif_urls

if __name__ == '__main__':
    urls = generate_gif_list()
    f = open(file_name, 'w')
    f.write('\n'.join(catgif_urls))
    f.close()
