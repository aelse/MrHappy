from botplugin import BotPlugin
import urllib
from BeautifulSoup import BeautifulSoup

class CommandTime(BotPlugin):

    def command_weather(self, bot, e, command, args, channel, nick):
        city = 'sydney'
        if len(args):
            city = args.lower()
        bot.reply(forecast(city), channel, nick, paste=True)

def get_forecast_url(city):
    urls = {
        'brisbane': 'qld',
        'sydney': 'nsw',
        'melbourne': 'vic',
        'adelaide': 'sa',
    }
    try:
        return 'http://www.bom.gov.au/%s/forecasts/%s.shtml' % (urls[city], city)
    except KeyError:
        return None
    return None

def forecast(city):
    url = get_forecast_url(city)
    if url is None:
        return 'Do not know how to get forecast for %s' % city.capitalize()

    w = urllib.urlopen(url)
    html = w.read()
    w.close()

    soup = BeautifulSoup(html)

    today = soup.find('div', {'class': 'day main'})
    maxtemp = today.find('em', {'class': 'max'}).getString()
    fc = today.find('p').getString()
    output = 'Today: (max %s)\n%s\n\n' % (maxtemp, fc)

    days = soup.findAll('div', {'class': 'day'})

    for day in days:
        day_of_week = day.find('h2').getString()
        mintemp = day.find('em', {'class': 'min'}).getString()
        maxtemp = day.find('em', {'class': 'max'}).getString()
        fc = day.find('p').getString()
        output = output + '%s: (min %s max %s)\n%s\n\n' % (day_of_week, mintemp, maxtemp, fc)

    return output
