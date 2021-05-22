import pandas as pd
import numpy as np
from os import path
from datetime import datetime

fomcDates = np.loadtxt('FOMCdates.csv', dtype='datetime64[D]', delimiter=',')

def loadReturns():
    # http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html
    if path.exists("F-F_Research_Data_Factors_daily_CSV.zip"):
        filename = "F-F_Research_Data_Factors_daily_CSV.zip"
    else:
        filename = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip"
    return pd.read_csv(filename, index_col=0, usecols=[0, 1], engine='python', skiprows=4, skipfooter=2,
        parse_dates=True, infer_datetime_format=True, compression='zip')

dailyReturns = loadReturns()

def vCalcFOMCday(fomcDates, dates, returnDates = False, lookback = -6):
    idx = fomcDates.searchsorted(dates)
    nextFOMC = fomcDates[idx]
    daysTo = np.busday_count(nextFOMC, dates)
    nIdx = np.where(idx > 0, idx-1, idx)
    lastFOMC = fomcDates[nIdx]
    daysSince = np.busday_count(lastFOMC, dates)
    fomcDays = np.where(daysTo >= lookback, daysTo, daysSince)
    if returnDates:
        return lastFOMC, nextFOMC, fomcDays
    else:
        return fomcDays

def getFOMCtoday(fomcDates):
    return vCalcFOMCday(fomcDates, np.datetime64(datetime.now().date()), returnDates=True)

def vCalcFOMCweek(fomcDays):
    return (fomcDays+1)//5

def getFOMCweeks(mini = -6, maxi = 34):
    weekRange = np.arange(mini, maxi)
    return weekRange[(weekRange+1)%5 == 0]

def calcCumReturns(dailyReturns, days):
    perReturns = dailyReturns/100+1
    nextReturns = perReturns[:]
    for i in range(days-1):
        nextReturns = nextReturns[1:]
        perReturns = perReturns[:-1]*nextReturns
    return (perReturns-1)*100

def getFOMCcal(fomcDates, dailyReturns = loadReturns(), days = 5, fomcDayRange = range(-6,34)):
    dailyReturns = dailyReturns.asfreq(freq='B', fill_value=0)
    dailyReturns.index.names = ['date']
    returnsDates = dailyReturns.index.values.astype('datetime64[D]')
    fomcDays = vCalcFOMCday(fomcDates, returnsDates)
    if days > 1:
        returns = calcCumReturns(dailyReturns.values, days)
        fomcDays = fomcDays[:-days+1]
    elif days == 1:
        returns = dailyReturns.values
    else:
        return
    dailyReturns = dailyReturns[:-days+1]
    dailyReturns['returns'] = returns
    dailyReturns['fomc_day'] = fomcDays
    dailyReturns['fomc_week'] = vCalcFOMCweek(fomcDays)
    return dailyReturns

def printCal():
    fomcCal = getFOMCcal(fomcDates)
    cols = fomcCal.columns.tolist()
    cols = cols[-2:] + cols[:-2]
    df = fomcCal[cols]
    df = df[fomcDates[0]:]
    df.to_csv('FOMCcalendar.csv', float_format='%.2f')
    df['1994-01':].to_csv('FOMCcycle.csv', float_format='%.2f')

printCal()

df = pd.read_csv('FOMCcycle.csv', index_col=0, parse_dates=True, infer_datetime_format=True)
df['price'] = np.cumprod((df['Mkt-RF']/100+1).values)
df['fomc_cycle'] = 0
df.loc[df['fomc_day'] == -6, 'fomc_cycle'] = 1
df['fomc_cycle'] = np.cumsum(df['fomc_cycle'].values)
df = pd.pivot_table(df, index='fomc_cycle', columns='fomc_day', values='price')
df.to_csv('FOMCsparks.csv', index=False, float_format='%.2f')

fomcCycle = pd.read_csv('FOMCcycle.csv', index_col=0, parse_dates=True, infer_datetime_format=True)
fomcCycle['start'] = (fomcCycle['fomc_day']+1)%5
fomcCycle['1994-01':].to_csv('FOMCcycle.csv', float_format='%.2f')
fomcCycle
# fomcCycle.loc[(fomcCycle['fomc_day']+1)%5 == 0, 'start'] = 1

