from datetime import *
import pandas as pd
from bisect import *
import numpy as np
from pandas.tseries.offsets import BDay

from bokeh.layouts import column, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, CrosshairTool, LabelSet, DateRangeSlider, Slider, Label, BoxAnnotation, Span
from bokeh.plotting import figure, curdoc

fomc_calendar = pd.read_csv('fomc_calendar', index_col=0, parse_dates=True, infer_datetime_format=True)
market = pd.read_csv('market', index_col=0, parse_dates=True, infer_datetime_format=True)

t = market['Mkt-RF'].values/100+1

def multiday_returns(days):
    a = np.copy(t[:1-days])
    for day in range(days-2):        
        a *= t[day+1:day-(days-2)] 
    a *= t[days-1:] 
    market.loc[:1-days,'returns'] = (a-1)*100
	
multiday_returns(5)

fomc = fomc_calendar.join(market, how='inner')
fomc['fomc_day'] = np.where(fomc['days_before'].values >= -6, fomc['days_before'].values, fomc['days_since'].values)

data = fomc[datetime(1994,1,1):datetime(2016,12,31)].groupby('fomc_day').filter(lambda x: 
		len(x) / len(fomc[datetime(1994,1,1):datetime(2016,12,31)]) > 0.0025).groupby('fomc_day').mean()
source = ColumnDataSource(data)

fig1 = figure(plot_width=1000, title='Stock returns of the FOMC cycle, 1994-2016')
fig1.line(x='fomc_day', y='returns', source=source)
fig1.circle(x='fomc_day', y='returns', source=source)
fig1.xaxis.axis_label = 'Days since FOMC meeting (weekends excluded)'
fig1.yaxis.axis_label = 'Avg. 5-day stock return, t to t+4'
labels = LabelSet(x='fomc_day', y='returns', text='fomc_day', x_offset=5, y_offset=-10, source=source, text_font_size='10pt')
fig1.add_layout(labels)
zero_returns = Span(location=0, dimension='width')
fig1.add_layout(zero_returns)

hover = HoverTool(tooltips=[("FOMC Day", "@fomc_day, μ = $y%)")], mode='vline')
fig1.add_tools(hover)
fig1.add_tools(CrosshairTool())

def date_range_slider_update(attrname, old, new):
	fig1.title.text = 'Stock returns of the FOMC cycle'
	date_range = date_range_slider.value_as_datetime
	fomc_range = fomc[date_range[0]:date_range[-1]]
	source.data = ColumnDataSource(fomc_range.groupby('fomc_day').filter(lambda x: len(x) / len(fomc_range) > 0.0025).groupby('fomc_day').mean()).data

date_range_slider = DateRangeSlider(start=fomc.index[0], end=fomc.index[-1], step=1, value=(datetime(1994,1,1), datetime(2016,12,31)))
date_range_slider.on_change('value', date_range_slider_update)

def days_slider_update(attrname, old, new):
	days = days_slider.value
	multiday_returns(days)
	fig1.yaxis.axis_label = 'Avg. '+str(days)+'-day stock return, t to t+'+str(days-1)
	fomc = fomc_calendar.join(market, how='inner')
	fomc['fomc_day'] = np.where(fomc['days_before'].values >= start_slider.value, fomc['days_before'].values, fomc['days_since'].values)
	date_range = date_range_slider.value_as_datetime
	fomc_range = fomc[date_range[0]:date_range[-1]]
	source.data = ColumnDataSource(fomc_range.groupby('fomc_day').filter(lambda x: len(x) / len(fomc_range) > 0.0025).groupby('fomc_day').mean()).data
	
days_slider = Slider(start=1, end=10, step=1, value=5, title='Multiday Returns')
days_slider.on_change('value', days_slider_update)

def start_slider_update(attrname, old, new):
	start = start_slider.value
	fomc['fomc_day'] = np.where(fomc['days_before'].values >= start, fomc['days_before'].values, fomc['days_since'].values)
	date_range = date_range_slider.value_as_datetime
	fomc_range = fomc[date_range[0]:date_range[-1]]
	source.data = ColumnDataSource(fomc_range.groupby('fomc_day').filter(lambda x: len(x) / len(fomc_range) > 0.0025).groupby('fomc_day').mean()).data
	
start_slider = Slider(start=-10, end=0, step=1, value=-6, title='Start FOMC Day')
start_slider.on_change('value', start_slider_update)

current_fomc = fomc_calendar.loc[(datetime.now() + pd.tseries.offsets.BDay(1)).date()]
tomorrow_fomc = current_fomc.days_before if current_fomc.days_before >= start_slider.value else current_fomc.days_since
label = Label(x=10, y=10, x_units='screen', y_units='screen', text='Upcoming FOMC Week: ' + str((tomorrow_fomc+1)//5)) 
fig1.add_layout(label)
current_fomc_day = BoxAnnotation(left=tomorrow_fomc-1, right=tomorrow_fomc, fill_alpha=0.1, fill_color='green')
fig1.add_layout(current_fomc_day)

curdoc().add_root(column(fig1, widgetbox(date_range_slider, days_slider, start_slider)))
curdoc().title = "FOMC"

# bokeh serve --show fomc_bokeh.py