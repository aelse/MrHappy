import re
from botplugin import BotPlugin


class Applause(BotPlugin):

    def listen(self, bot, message):
        if message[u'type'] != u'TextMessage':
            return

        # Attempt to strip out URLs
        msg = re.sub('(https?|ftp)://\S+', '', message['body'])

        pattern = "applau(d|se)|bravo|slow clap"
        m = re.search(pattern, msg, re.IGNORECASE)
        if m:
            image = 'http://i.imgur.com/9Zv4V.gif'
            bot.speak(image)
