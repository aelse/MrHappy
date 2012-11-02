import re
from botplugin import BotPlugin


class ShouldOf(BotPlugin):

    def listen(self, bot, e, message):
        if message[u'type'] != u'TextMessage':
            return

        # Attempt to strip out URLs
        msg = re.sub('(https?|ftp)://\S+', '', message['body'])

        pattern = "(should|would|could|might)(n't)? of(?! course)"
        m = re.search(pattern, msg, re.IGNORECASE)
        if m:
            (a, b) = m.groups()
            if b is None:
                b = ''
            correction = '*' + a + b + " have"
            bot.reply(correction, '', '')
