import random
import re
from botplugin import BotPlugin


all_images = [
    "http://4.bp.blogspot.com/_D_Z-D2tzi14/S8TRIo4br3I/AAAAAAAACv4/Zh7_GcMlRKo/s400/ALOT.png",
    "http://3.bp.blogspot.com/_D_Z-D2tzi14/S8TTPQCPA6I/AAAAAAAACwA/ZHZH-Bi8OmI/s1600/ALOT2.png",
    "http://2.bp.blogspot.com/_D_Z-D2tzi14/S8TiTtIFjpI/AAAAAAAACxQ/HXLdiZZ0goU/s320/ALOT14.png",
    "http://fc02.deviantart.net/fs70/f/2010/210/1/9/Alot_by_chrispygraphics.jpg"
]
images = []

class Alot(BotPlugin):

    def listen(self, bot, message):
        if message[u'type'] != u'TextMessage':
            return

        # Attempt to strip out URLs
        msg = re.sub('(https?|ftp)://\S+', '', message['body'])

        pattern = "(^|\W)alot(\z|\W|$)"
        m = re.search(pattern, msg, re.IGNORECASE)
        if m:
            global images
            if not len(images):
                global all_images
                images = list(all_images)
                random.shuffle(images)
            bot.speak(images.pop())
