import requests
from lxml import html
from datetime import *
import pandas as pd

url = 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'
fomccalendars = html.fromstring(requests.get(url).content)
fomc_dates = []
for panel in fomccalendars.xpath(".//div[@class='panel panel-default']"):
	year = int(panel.xpath(".//div[@class='panel-heading']//text()")[0][0:4])
	months = panel.xpath(".//div[contains(@class, 'month')]//text()")
	dates = panel.xpath(".//div[contains(@class, 'date')]/text()")
	m = [ datetime.strptime(month.split('/')[-1][0:3], '%b').month for month in months ]
	d = [ int(day.split('-')[-1].rstrip('*')) for day in dates if not "unscheduled" in day ]
	fomc_dates += [ datetime(year, m, d).date() for m,d in zip(m, d) ] 
	
url = 'https://www.federalreserve.gov/monetarypolicy/fomc_historical_year.htm'
fomc_historical_year = html.fromstring(requests.get(url).content)
fomchistorical = [ 'https://www.federalreserve.gov'+href for href in fomc_historical_year.xpath(".//div[@id='article']//a/@href") ]
dates = []
for url in fomchistorical:
    dates += html.fromstring(requests.get(url).content).xpath(".//h5/text()")
meetings = [ meeting.split() for meeting in dates if "Meeting" in meeting ]
years = [ int(meeting[-1]) for meeting in meetings]
months = [ datetime.strptime(date[0], '%B').month if len(date)==5 else datetime.strptime(date[0], '%B').month+1 for date in meetings ]
days = [ int(date[1].split('-')[-1]) if len(date)==5 else 1 for date in meetings ]
fomc_dates += [ datetime(y, m, d).date() for y,m,d in zip(years, months, days) ]
fomc_dates.sort()
fomc_dates.remove(datetime(2003, 9, 15).date())
fomc_df = pd.DataFrame(fomc_dates, columns=['fomc_date'], dtype='datetime64[ns]')
fomc_df.to_csv('fomc_dates.csv', index=False)
