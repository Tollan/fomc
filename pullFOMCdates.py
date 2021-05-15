import requests
from lxml import html
from datetime import datetime, timedelta
import itertools
import pandas as pd

def getRecentFOMCtext():
    httpGet = requests.get('https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm')
    recentFOMChtml = html.fromstring(httpGet.content)
    return recentFOMChtml.xpath(""".//div[@class='panel panel-default']
        //div[@class='panel-heading' or contains(@class, 'month') or contains(@class, 'date')]//text()""")

def parseRecentFOMCtext(recentText = getRecentFOMCtext()):
    recentFOMCdates = []
    for element in recentText:
        if element[0:2] == '20' and element[0:4].isdigit():
            year = element[0:4]
            continue
        if element[0:3].isalpha():
            month = element.split('/')[-1][0:3]
            continue
        day = element.split('-')[-1].rstrip('*').zfill(2)
        if not day.isdigit():
            day = element.split(' ')[0].zfill(2)    # for unscheduled calls
        if not day.isdigit():
            continue
        recentFOMCdates += [ datetime.strptime(year+month+day, '%Y%b%d').date() ]
    return recentFOMCdates

def getHistFOMCtext():
    httpGet = requests.get('https://www.federalreserve.gov/monetarypolicy/fomc_historical_year.htm')
    histFOMCyearsHTML = html.fromstring(httpGet.content)
    histFOMCurls = [ 'https://www.federalreserve.gov'+href for href in histFOMCyearsHTML.xpath(".//div[@id='article']//a/@href") ]
    return [ html.fromstring(requests.get(url).content).xpath(".//h5/text()") for url in histFOMCurls ]

def parseHistFOMCtext(histText = getHistFOMCtext()):
    histFOMCdates = []
    for element in itertools.chain.from_iterable(histText):
        if 'Meeting' not in element:  # skip conference calls, unscheduled
            continue
        meeting = element.split()[-5:]
        year = meeting[-1]
        month = meeting[0].split('-')[-1].split('/')[-1]
        day = meeting[1].split('-')[-1].zfill(2)
        histFOMCdates += [ datetime.strptime(year+month+day, '%Y%B%d').date() ]
    return histFOMCdates

def getFOMCdates():
    FOMCdates = parseRecentFOMCtext() + parseHistFOMCtext()
    [ FOMCdates.remove(date) for date in FOMCdates if date+timedelta(days=1) in FOMCdates ]
    FOMCdates.sort()
    return FOMCdates

def saveFOMCdates(FOMCdates = getFOMCdates()):
    FOMCdf = pd.DataFrame(FOMCdates, columns=['fomc_date'], dtype='datetime64[ns]')
    FOMCdf.to_csv('FOMCdates.csv', header=False, index=False)

def updateFOMCdates(FOMCdates = getFOMCdates()):
    recentFOMCdates = parseRecentFOMCtext(getRecentFOMCtext())
    recentFOMCdf = pd.DataFrame(recentFOMCdates, columns=['fomc_date'], dtype='datetime64[ns]')
    FOMCdf = FOMCdates.join(recentFOMCdf, on=['fomc_date'], how='outer')
    return FOMCdf.sort_values(by=['fomc_date'])