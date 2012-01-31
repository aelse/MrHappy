from botplugin import BotPlugin
import urllib
from BeautifulSoup import BeautifulSoup

class CommandTime(BotPlugin):

    def command_weather(self, bot, e, command, args, channel, nick):
        bot.reply(forecast('sydney'), channel, nick, paste=True)

def forecast(city):
    url = 'http://www.bom.gov.au/nsw/forecasts/%s.shtml' % city
    w = urllib.urlopen(url)
    html = w.read()
    w.close()

    output = ''
    soup = BeautifulSoup(html)
    days = soup.findAll('div', {'class': 'day'})

    for day in days:
        day_of_week = day.find('h2').getString()
        mintemp = day.find('em', {'class': 'min'}).getString()
        maxtemp = day.find('em', {'class': 'max'}).getString()
        fc = day.find('p').getString()
        output = output + '%s: (min %s max %s)\n%s\n\n' % (day_of_week, mintemp, maxtemp, fc)

    return output
