# -*- coding: utf-8 -*-

import requests
from lxml import html
from datetime import datetime, timedelta
import itertools
from os import path
import pandas as pd
from bisect import bisect
import numpy as np

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
    if path.exists("FOMCdates.csv"):
        fomcDF = pd.read_csv('FOMCdates.csv', names=['fomc_date'], parse_dates=['fomc_date'], infer_datetime_format=True)
        return [ fomcTimestamp.date() for fomcTimestamp in fomcDF['fomc_date'] ]
    FOMCdates = parseRecentFOMCtext() + parseHistFOMCtext()
    [ FOMCdates.remove(date) for date in FOMCdates if date+timedelta(days=1) in FOMCdates ]
    FOMCdates.sort()
    FOMCdf = pd.DataFrame(FOMCdates, columns=['fomc_date'], dtype='datetime64[ns]')
    FOMCdf.to_csv('FOMCdates.csv', header=False, index=False)
    return FOMCdates

def calcFOMCday(FOMCdates = getFOMCdates(), lookback = -6):
    FOMCcalendar = []
    busDateRange = [ busTimestamp.date() for busTimestamp in pd.bdate_range(FOMCdates[0], FOMCdates[-1]) ]
    for busDate in busDateRange:
        fomcIndex = bisect(FOMCdates, busDate)
        if FOMCdates[fomcIndex-1] == busDate:
            fomcDay = np.busday_count(FOMCdates[fomcIndex-1], busDate)
        else:
            daysTo = np.busday_count(FOMCdates[fomcIndex], busDate)
            if daysTo >= lookback:
                fomcDay = daysTo
            else:
                fomcDay = np.busday_count(FOMCdates[fomcIndex-1], busDate)
        fomcWeek = (fomcDay+1)//5
        FOMCcalendar += [(busDate, fomcDay, fomcWeek)]
    return FOMCcalendar

def getFOMCcalendar():
    if path.exists("FOMCcalendar.csv"):
        return pd.read_csv('FOMCcalendar.csv', index_col=[0], parse_dates=['date'], infer_datetime_format=True)
    FOMCcalendarDf = pd.DataFrame(calcFOMCday(), columns =['date', 'fomc_day', 'fomc_week']).set_index('date')
    FOMCcalendarDf.to_csv('FOMCcalendar.csv')
    return FOMCcalendarDf

def updateFOMCdates():
    recentFOMCdates = parseRecentFOMCtext(getRecentFOMCtext())
    recentFOMCdf = pd.DataFrame(recentFOMCdates, columns=['fomc_date'], dtype='datetime64[ns]')
    FOMCdf = getFOMCdates().join(recentFOMCdf, on=['fomc_date'], how='outer')
    return FOMCdf.sort_values(by=['fomc_date'])

def getFOMCday(FOMCcalendarDf=getFOMCcalendar(), day = datetime.now().date()):
    return FOMCcalendarDf.iloc[bisect(FOMCcalendarDf.index, day)-1]  # may not be a business day

def getReturns():
    # http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html
    if path.exists("F-F_Research_Data_Factors_daily_CSV.zip"):
        filename = "F-F_Research_Data_Factors_daily_CSV.zip"
    else:
        filename = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip"
    dailyReturns = pd.read_csv(filename, index_col=0, usecols=[0, 1], engine='python', skiprows=4, skipfooter=2,
        parse_dates=True, infer_datetime_format=True, compression='zip')
    return dailyReturns.asfreq(freq='B', fill_value=0)

def calcCumReturns(dailyReturns = getReturns(), days=5):
    cumReturns = dailyReturns['Mkt-RF'].values/100+1
    nextReturns = cumReturns[:]
    for i in range(days-1):
        nextReturns = nextReturns[1:]
        cumReturns = cumReturns[:-1]*nextReturns
    return (cumReturns-1)*100

def getFOMCreturns(FOMCcalendarDf=getFOMCcalendar(), dailyReturns = getReturns(), days=5):
    if path.exists("FOMCreturns.csv"):
        return pd.read_csv('FOMCreturns.csv', index_col=[0], parse_dates=['date'], infer_datetime_format=True)
    cumReturns = calcCumReturns(dailyReturns, days)
    dailyReturns = dailyReturns[:-days+1]
    dailyReturns['bus_week'] = cumReturns
    fomcReturns = FOMCcalendarDf.join(dailyReturns, how='inner')
    fomcReturns.index.name = 'date'
    fomcReturns.to_csv('FOMCreturns.csv')
    return fomcReturns
