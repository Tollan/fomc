# -*- coding: utf-8 -*-

from FOMCdates import *
from bokeh.io import show
from bokeh.layouts import column, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, CrosshairTool, LabelSet, DateRangeSlider, Label, BoxAnnotation, Span
from bokeh.plotting import figure
from bokeh.models.glyphs import Patch
from scipy.stats import sem, t

def calcFOMCstats(fomcReturns=getFOMCreturns()):
    a = fomcReturns.drop(['Mkt-RF', 'fomc_week'], 1).dropna().values
    u, c = np.unique(a[:, 0], return_counts=True)
    u = u[c/len(a) > 0.0025]
    df = pd.DataFrame(map(lambda x: a[:, 1][np.where(a[:, 0] == x)].mean(), u), index=u, columns=['bus_week'])
    df.index.name = 'fomc_day'
    return df

def plotFOMC(lookback=1000):
    if 'FOMCcalendarDf' not in locals():
        FOMCcalendarDf = getFOMCcalendar()
    if 'fomcReturns' not in locals():
        fomcReturns = getFOMCreturns(FOMCcalendarDf)
    fomcData = calcFOMCstats(fomcReturns[:-lookback])
    source = ColumnDataSource(fomcData)

    fig1 = figure(plot_width=1000)
    fig1.title.text = "Stock returns of the FOMC cycle, {} onwards".format(fomcReturns.index[-lookback].date())
    fig1.line(x='fomc_day', y='bus_week', source=source)
    fig1.circle(x='fomc_day', y='bus_week', source=source)
    fig1.xaxis.axis_label = 'Days since FOMC meeting (weekends excluded)'
    fig1.yaxis.axis_label = 'Avg. 5-day stock return, t to t+4'
    labels = LabelSet(x='fomc_day', y='bus_week', text='fomc_day', x_offset=5, y_offset=-10, source=source, text_font_size='10pt')
    fig1.add_layout(labels)
    zero_returns = Span(location=0, dimension='width')
    fig1.add_layout(zero_returns)
    tomorrow_fomc = getFOMCday(FOMCcalendarDf)
    label = Label(x=10, y=10, x_units='screen', y_units='screen', text='Coming FOMC Week: ' + str(tomorrow_fomc.fomc_week)) 
    fig1.add_layout(label)
    current_fomc_day = BoxAnnotation(left=tomorrow_fomc.fomc_day-1, right=tomorrow_fomc.fomc_day, fill_alpha=0.1, fill_color='green')
    fig1.add_layout(current_fomc_day)

    hover = HoverTool(tooltips=[("FOMC Day", "@fomc_day, μ = $y%)")], mode='vline')
    fig1.add_tools(hover)
    fig1.add_tools(CrosshairTool())
    show(fig1)

    # def slider_update(attrname, old, new):
    #     fig1.title.text = 'Stock returns of the FOMC cycle'
    #     date_range = slider.value_as_datetime
    #     fomc_range = fomcReturns[date_range[0]:date_range[-1]]
    #     newFOMCdata = calcFOMCstats(fomc_range)
    #     source.data = ColumnDataSource(newFOMCdata).data

    # slider = DateRangeSlider(start=fomcReturns.index[0], end=fomcReturns.index[-1], step=1, value=(datetime(1994,1,1), datetime(2016,12,31)))
    # slider.on_change('value', slider_update)

    # show(column(fig1, widgetbox(slider)))

plotFOMC()

def confidenceInterval(arr, confidence=0.95):
    n = len(arr)
    m = arr.mean()
    std_err = sem(arr)
    h = std_err * t.ppf((1 + confidence) / 2, n - 1)
    return (m - h, m, m + h)

def calcFOMCstats2(fomcReturns=getFOMCreturns()):
    a = fomcReturns.drop(['Mkt-RF', 'fomc_week'], 1).dropna().values
    u, c = np.unique(a[:, 0], return_counts=True)
    u = u[c/len(a) > 0.0025]
    df = pd.DataFrame(map(lambda x: confidenceInterval(a[:, 1][np.where(a[:, 0] == x)]), u), index=u, columns=['low', 'mean', 'high'])
    df.index.name = 'fomc_day'
    return df

def plotFOMC2(lookback=1000):
    if 'FOMCcalendarDf' not in locals():
        FOMCcalendarDf = getFOMCcalendar()
    if 'fomcReturns' not in locals():
        fomcReturns = getFOMCreturns(FOMCcalendarDf)
    fomcData = calcFOMCstats2(fomcReturns[:-lookback])
    source = ColumnDataSource(fomcData)

    fig1 = figure(plot_width=1000)
    fig1.title.text = "Stock returns over the FOMC cycle, {} onwards".format(fomcReturns.index[-lookback].date())
    fig1.patch(x=np.hstack((fomcData.index, fomcData.index[::-1])),y=np.hstack((fomcData['low'], fomcData['high'][::-1])), fill_color="#a6cee3")
    fig1.line(x='fomc_day', y='mean', line_color='black', source=source)
    fig1.circle(x='fomc_day', y='mean', color='black', source=source)
    fig1.line(x='fomc_day', y='low', source=source)
    fig1.line(x='fomc_day', y='high', source=source)
    fig1.xaxis.axis_label = 'Days since FOMC meeting (weekends excluded)'
    fig1.yaxis.axis_label = 'Avg. 5-day stock return, t to t+4'
    labels = LabelSet(x='fomc_day', y='mean', text='fomc_day', x_offset=5, y_offset=-10, source=source, text_font_size='10pt')
    fig1.add_layout(labels)
    zero_returns = Span(location=0, dimension='width')
    fig1.add_layout(zero_returns)
    tomorrow_fomc = getFOMCday(FOMCcalendarDf)
    current_fomc_day = BoxAnnotation(left=tomorrow_fomc.fomc_day-1, right=tomorrow_fomc.fomc_day, fill_alpha=0.1, fill_color='green')
    fig1.add_layout(current_fomc_day)
    show(fig1)

plotFOMC2(500)

getFOMCday(FOMCcalendarDf)

