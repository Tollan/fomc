# -*- coding: utf-8 -*-

# from FOMCdates import getFOMCreturns, getFOMCday, getFOMCcalendar
import pandas as pd
import numpy as np
from os import path
from datetime import datetime
from bokeh.io import show
from bokeh.layouts import column, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, CrosshairTool, LabelSet, DateRangeSlider, Label, BoxAnnotation, Span, Band
from bokeh.plotting import figure, curdoc
from bokeh.models.glyphs import Patch
from bokeh.models.tickers import FixedTicker
from scipy.stats import sem, t

fomcDates = np.loadtxt('FOMCdates.csv', dtype='datetime64[D]', delimiter=',')

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

def getFOMCweeks(mini = -6, maxi = 35):
    weekRange = np.arange(mini, maxi)
    return weekRange[(weekRange+1)%5 == 0]

getFOMCweeks()

np.arange(-6,35)[(np.arange(-6,35)+1)%5 == 0]

def loadReturns():
    # http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html
    if path.exists("F-F_Research_Data_Factors_daily_CSV.zip"):
        filename = "F-F_Research_Data_Factors_daily_CSV.zip"
    else:
        filename = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip"
    return pd.read_csv(filename, index_col=0, usecols=[0, 1], engine='python', skiprows=4, skipfooter=2,
        parse_dates=True, infer_datetime_format=True, compression='zip')

dailyReturns = loadReturns()

def calcCumReturns(dailyReturns, days):
    perReturns = dailyReturns/100+1
    nextReturns = perReturns[:]
    for i in range(days-1):
        nextReturns = nextReturns[1:]
        perReturns = perReturns[:-1]*nextReturns
    return (perReturns-1)*100

def confidenceInterval(arr, confidence=0.95):
    n = arr.size
    mu = arr.sum()/n
    std_err = arr.std()/n**0.5
    h = std_err * t.ppf((1 + confidence) / 2, n - 1)
    return mu - h, mu, mu + h

def getFOMCstats(fomcDates, dailyReturns = loadReturns(), days = 5, fomcDayRange = range(-6,35)):
    returnsDates = dailyReturns.index.values.astype('datetime64[D]')
    fomcDays = vCalcFOMCday(fomcDates, returnsDates)
    if days > 1:
        returns = calcCumReturns(dailyReturns.values, days)
        fomcDays = fomcDays[:-days+1]
    elif days == 1:
        returns = dailyReturns.values
    else:
        return
    df = pd.DataFrame(map(lambda day: confidenceInterval(returns[fomcDays == day]), fomcDayRange), index=fomcDayRange, columns=['low', 'mean', 'high'])
    df.index.name = 'fomc_day'
    return df

def getPlot(fomcDates, dailyReturns):
    fomcData = getFOMCstats(fomcDates, dailyReturns)
    source = ColumnDataSource(fomcData)

    fig1 = figure(plot_width=1000)
    fig1.title.text = "Stock returns over the FOMC cycle, {} onwards".format(dailyReturns.index[0].date())
    fig1.patch(x=np.hstack((fomcData.index, fomcData.index[::-1])),y=np.hstack((fomcData['low'], fomcData['high'][::-1])), fill_color="#a6cee3")
    fig1.line(x='fomc_day', y='mean', line_color='black', source=source)
    fig1.circle(x='fomc_day', y='mean', color='black', source=source)
    fig1.line(x='fomc_day', y='low', source=source)
    fig1.line(x='fomc_day', y='high', source=source)
    fig1.xaxis.axis_label = 'Days since FOMC meeting (weekends excluded)'
    fig1.yaxis.axis_label = 'Avg. 5-day stock return, t to t+4'
    labels = LabelSet(x='fomc_day', y='mean', text='fomc_day', x_offset=5, y_offset=-10, source=source, text_font_size='10pt')
    fig1.add_layout(labels)
    
    popMeanSpan = Span(location=dailyReturns.values.mean(), dimension='width', line_color='black', line_dash='dashed')
    fig1.add_layout(popMeanSpan)
    zeroReturnSpan = Span(location=0, dimension='width')
    fig1.add_layout(zeroReturnSpan)
    fomcTodaySpan = Span(location=int(getFOMCtoday(fomcDates)[2]), dimension='height', line_color='black', line_dash='dashed')
    fig1.add_layout(fomcTodaySpan)
    
    fig1.xgrid.ticker = FixedTicker(ticks=getFOMCweeks())
    return fig1

def plotFOMC(fomcDates, dailyReturns = loadReturns(), lookback = 1000):
    p = getPlot(fomcDates, dailyReturns[-lookback:])
    show(p)

plotFOMC(fomcDates, dailyReturns)
plotFOMC(fomcDates, dailyReturns, 10000)

