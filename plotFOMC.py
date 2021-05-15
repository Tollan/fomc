# ref FOMCcalendar.py

from bokeh.io import show
from bokeh.layouts import column, widgetbox
from bokeh.models import *
from bokeh.plotting import figure, curdoc
from bokeh.models.glyphs import Patch
from bokeh.models.tickers import FixedTicker
from scipy.stats import sem, t

def confidenceInterval(arr, confidence=0.95):
    n = arr.size
    if n <= 0: return
    mu = arr.sum()/n
    std_err = arr.std()/n**0.5
    h = std_err * t.ppf((1 + confidence) / 2, n - 1)
    return mu - h, mu, mu + h

def getFOMCstats(fomcDates, dailyReturns = loadReturns(), days = 5, fomcDayRange = range(-6,34)):
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

def getPlot(fomcDates, dailyReturns, days = 5):
    fomcData = getFOMCstats(fomcDates, dailyReturns, days)
    source = ColumnDataSource(fomcData)

    p = figure(plot_width=1000)
    p.title.text = "Stock returns over the FOMC cycle, {} onwards".format(dailyReturns.index[0].date())
    p.xaxis.axis_label = 'Days since FOMC meeting (weekends excluded)'
    p.yaxis.axis_label = 'Avg. 5-day stock return, t to t+4'
    labels = LabelSet(x='fomc_day', y='mean', text='fomc_day', x_offset=5, y_offset=-10, source=source, text_font_size='10pt')
    p.add_layout(labels)
    
    p.line(x='fomc_day', y='mean', line_color='black', source=source)
    p.circle(x='fomc_day', y='mean', color='black', source=source)
    confidenceBands = Band(base='fomc_day', lower='low', upper='high', source=source, level='underlay',
      fill_alpha=1.0, line_width=1, line_color='black')
    p.add_layout(confidenceBands)
    
    popMeanSpan = Span(location=dailyReturns.values.mean(), dimension='width', line_color='black', line_dash='dashed')
    p.add_layout(popMeanSpan)
    zeroReturnSpan = Span(location=0, dimension='width')
    p.add_layout(zeroReturnSpan)
    fomcTodaySpan = Span(location=int(getFOMCtoday(fomcDates)[2]), dimension='height', line_color='black', line_dash='dashed')
    p.add_layout(fomcTodaySpan)
    
    p.xgrid.ticker = FixedTicker(ticks=getFOMCweeks())
    return p

def plotFOMC(fomcDates, dailyReturns = loadReturns(), lookback = 10000, days = 5):
    p = getPlot(fomcDates, dailyReturns[-lookback:], days)
    show(p)

plotFOMC(fomcDates, dailyReturns)
plotFOMC(fomcDates, dailyReturns, 10000, 1)
plotFOMC(fomcDates, dailyReturns, 500)

def plotDates(fomcDates, dailyReturns, days = 5):
    fomcData = getFOMCstats2(fomcDates, dailyReturns, days)
    # fomcData = pd.DataFrame(calcCumReturns(dailyReturns.values, days), index=dailyReturns.index.values.astype('datetime64[D]')[:-days+1], columns=['returns'])
    source = ColumnDataSource(fomcData)

    p = figure(plot_width=1000)
    # p.title.text = "Stock returns over the FOMC cycle, {} onwards".format(dailyReturns.index[0].date())
    # p.xaxis.axis_label = 'Days since FOMC meeting (weekends excluded)'
    # p.yaxis.axis_label = 'Avg. 5-day stock return, t to t+4'
    # labels = LabelSet(x='fomc_day', y='mean', text='fomc_day', x_offset=5, y_offset=-10, source=source, text_font_size='10pt')
    # p.add_layout(labels)
    p.xaxis.formatter=DatetimeTickFormatter(
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %B %Y"],
    )
    p.line(x='index', y='returns', line_color='black', source=source)
    p.circle(x=fomcData.index[fomcData['fomc_day']==0], y=0, color='blue')
    # p.line(x='fomc_day', y='mean', line_color='black', source=source)
    # p.circle(x=fomcDates, y=0, color='blue')
    # confidenceBands = Band(base='fomc_day', lower='low', upper='high', source=source, level='underlay',
    #   fill_alpha=1.0, line_width=1, line_color='black')
    # p.add_layout(confidenceBands)
    
    # popMeanSpan = Span(location=dailyReturns.values.mean(), dimension='width', line_color='black', line_dash='dashed')
    # p.add_layout(popMeanSpan)
    zeroReturnSpan = Span(location=0, dimension='width')
    p.add_layout(zeroReturnSpan)
    # fomcTodaySpan = Span(location=fomcDates, dimension='height', line_color='black', line_dash='dashed')
    # p.add_layout(fomcTodaySpan)
    
    hover = HoverTool(tooltips=[('date', '@index{%F}'), ( 'return', '@returns')], formatters={ 'index' : 'datetime' }, mode='vline')
    p.add_tools(hover)
    p.add_tools(CrosshairTool())
    return p

def plotFOMCdates(fomcDates, dailyReturns = loadReturns(), lookback = 10000, days = 5):
    p = plotDates(fomcDates, dailyReturns[-lookback:], days)
    show(p)
    
plotFOMCdates(fomcDates, dailyReturns, 500)

fomcData['2018-03']
getFOMCweeks()