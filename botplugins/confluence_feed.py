from botplugin import BotPlugin
import re, requests, feedparser
import logging, subprocess, threading

from datetime import datetime
from dateutil import parser, tz
from BeautifulSoup import BeautifulSoup

time_save_file = 'confluence_save_time'
last_date = None


class ConfluenceFeed(BotPlugin):

    timer = None
    git_repos = None
    notify_channel = None
    fetch_interval = 60
    username = ''
    password = ''

    config_options = {
        'confluence_feed_url': '',
        'username': '',
        'password': '',
        'fetch_interval': str(fetch_interval),
        'notify_channel': '',
    }

    def setup(self, bot, options):
        self.bot = bot
        if options.has_key('confluence_feed_url'):
            self.confluence_feed_url = options['confluence_feed_url']
            logging.info('Monitoring Confluence feed %s' % self.confluence_feed_url)
        if options.has_key('fetch_interval'):
            try:
                fetch_interval = int(options['fetch_interval'])
                self.fetch_interval = fetch_interval
                logging.info('Checking at %d second intervals.' % self.fetch_interval)
            except:
                pass
        if options.has_key('notify_channel'):
            self.notify_channel = options['notify_channel']
            logging.info('Sending notifications to %s' % self.notify_channel)
        if options.has_key('username'):
            self.username = options['username']
        if options.has_key('password'):
            self.password = options['password']

        global last_date
        last_date = load_time(time_save_file)

        if not self.timer and self.fetch_interval:
            logging.info('Setting feed monitor timer to %d seconds.' % self.fetch_interval)
            self.timer = threading.Timer(self.fetch_interval, self.notify_channel_of_changes)
            self.timer.start()
        else:
            logging.warning('Not setting a feed monitor timer.')

    def teardown(self):
        if self.timer:
            if self.timer.isAlive():
                self.timer.cancel()
            self.timer = None

    def notify_channel_of_changes(self):
        if self.confluence_feed_url:
            logging.info('Looking for Confluence updates.')
            confluence_updates = check_feed(self.confluence_feed_url, self.username, self.password)
            for update in confluence_updates:
                logging.debug('Confluence update: %s' % update)
                self.bot.say_public(self.notify_channel, update)
        else:
            logging.info('Skipping Confluence feed checks.')

        # start a new timer if existing timer wasn't cancelled,
        # which may have happened while we were polling repos.
        if self.timer and self.fetch_interval:
            self.timer = threading.Timer(self.fetch_interval, self.notify_channel_of_changes)
            self.timer.start()
        else:
            logging.warning('Not setting a new feed monitor timer.')

def save_time(tstamp_file, time):
    """Save time to file"""

    try:
        fh = open(tstamp_file, 'w')
        fh.write(str(time))
        fh.close()
    except:
        pass

def load_time(tstamp_file):
    """Load time from file, or if not possible then
    return current time in UTC timezone"""

    date = None
    try:
        fh = open(tstamp_file, 'r')
        t = fh.read()
        date = parser.parse(t)
    except:
        utc = tz.gettz('UTC')
        date = datetime.now(utc)
        # Save the current time as the timestamp
        save_time(tstamp_file, date)
    return date

# timezone conversion
def as_local_time(t):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Australia/Sydney')
    local = t.replace(tzinfo=from_zone).astimezone(to_zone)
    return local

# best effort guesses at converting soup to strings
def stringify_soup(x):
    if x.string:
        return x.string.strip()
    elif x.text:
        return x.text
    else:
        return ''


def feed_entry_string(entry):
    sum_txt = ''
    try:
        soup = BeautifulSoup(entry.summary)
        m = re.search('"(.+)"', soup.find('p').text)
        if m:
            sum_txt = m.groups()[0]
    except:
        pass
    s = '%s edited %s: %s : %s' % (entry.author, entry.title, sum_txt, entry.link)
    return s

def check_feed(url, username, password):
    global last_date
    r = requests.get(url, auth=(username, password))
    confluence_updates = []
    if r.status_code == 200:

        new_date = last_date
        f = feedparser.parse(r.text)
        for entry in f.entries:
            published = parser.parse(entry.published)
            if published > last_date:
                if published > new_date:
                    new_date = published
                # Append the update to the list
                confluence_updates.append(feed_entry_string(entry))
        if new_date > last_date:
            save_time(time_save_file, new_date)
            last_date = new_date
    return confluence_updates

if __name__ == "__main__":
    import sys
    last_date = load_time(time_save_file)

    # url, username, password
    confluence_updates = check_feed(sys.argv[1], sys.argv[2], sys.argv[3])
    for update in confluence_updates:
        print update