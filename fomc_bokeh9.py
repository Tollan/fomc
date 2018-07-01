#bokeh serve --show fomc_bokeh.py
#Tools Missing!

from datetime import *
import pandas as pd
from bisect import *
import numpy as np
from pandas.tseries.offsets import BDay
from bokeh.server.server import Server
from bokeh.plotting import figure, curdoc
from bokeh.layouts import *
from bokeh.models import *
# from bokeh.models import ColumnDataSource, HoverTool, CrosshairTool, LabelSet, DateRangeSlider, Slider, Label, BoxAnnotation, Span, TableColumn, DataTable
# from bokeh.themes import Theme

def modify_doc(doc):
	fomc_calendar = pd.read_csv('fomc_calendar.csv', index_col=0, parse_dates=True, infer_datetime_format=True)
	market = pd.read_csv('market.csv', index_col=0, parse_dates=True, infer_datetime_format=True)

	significance = 0.0025
	days = 5
	start_fomc_day = -6
	start_date = datetime(1994,1,1)
	end_date = datetime(2016,12,31)
	date_range = (start_date, end_date)

	t = market['premium'].values/100+1
	def multiday_returns(days):
		a = np.copy(t[:1-days])
		for day in range(days-2):
			a *= t[day+1:day-(days-2)]
		a *= t[days-1:]
		market.loc[:1-days,'returns'] = (a-1)*100
	multiday_returns(days)

	#global fomc 
	fomc = fomc_calendar.join(market, how='inner') # move outside
	fomc['fomc_day'] = np.where(fomc['days_prior'].values >= start_fomc_day, fomc['days_prior'].values, fomc['days_since'].values)
	#ranged = fomc[start_date:end_date]
	#grouped = ranged.groupby('fomc_day').filter(lambda x: len(x) / len(ranged) > significance).groupby('fomc_day')
	#data = grouped.mean()['returns']
	def calc_fomc(date):
		current_fomc = fomc_calendar.loc[(date + pd.tseries.offsets.BDay(1)).date()]
		return current_fomc['days_prior'] if current_fomc['days_prior'] >= start_fomc_day else current_fomc['days_since']
	date_picker = DatePicker(title="Date:", value=datetime.now())
	def fomc_day():
		return calc_fomc(date_picker.value)
	def fomc_week():
		return (fomc_day_slider.value+1)//5
	date_range_slider = DateRangeSlider(start=fomc.index[0], end=fomc.index[-1], step=1, value=date_range, title="Date Range")
	def range_group_data():
		date_range = date_range_slider.value_as_datetime
		fomc_range = fomc[date_range[0]:date_range[-1]]
		return fomc_range.groupby('fomc_day').filter(lambda x: len(x) / len(fomc_range) > significance).groupby('fomc_day')
	def mean_data():
		return range_group_data().mean()['returns']
	data = mean_data()
	fomc_day_slider = Slider(start=data.index.values.min(), end=data.index.values.max(), step=1, value=fomc_day(), title="FOMC Day")
	def select_fomc(fomc_day):
		selected_index = np.where(data.index.values==fomc_day)[0][0]
		return {'0d': {'glyph': None, 'get_view': {}, 'indices': []}, '1d': {'indices': [selected_index]}, '2d': {'indices': {}}}
	def mu():
		days_data = range_group_data().get_group(fomc_day_slider.value)['returns'].values
		return days_data.mean()
	def sigma():
		days_data = range_group_data().get_group(fomc_day_slider.value)['returns'].values
		return days_data.std()
	
	def daily_data():
		days_data = range_group_data().get_group(fomc_day_slider.value)['returns'].values
		mu, sigma = days_data.mean(), days_data.std()
		#fig2.title.text = "Day {0}, Week {1}: Normal Distribution (μ={2:.2}, σ={3:.2})".format(fomc_day_slider.value, fomc_week(), mu, sigma)
		hist, edges = np.histogram(days_data, density=True, bins='auto')
		x = np.linspace(days_data.min(), days_data.max(), hist.size)
		pdf = 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-(x-mu)**2 / (2*sigma**2))
		return dict(zip(['top', 'bottom', 'left', 'right', 'x', 'pdf'], [hist, hist*0, edges[:-1], edges[1:], x, pdf]))
	
	def fomc_day_data():
		data = mean_data()
		return dict(zip(['fomc_day','returns'], [data.index.values, data.values]))
	
	source = ColumnDataSource(fomc_day_data())
	source.selected = select_fomc(fomc_day())
	daily_source = ColumnDataSource(daily_data())
	
	start_slider = Slider(start=-10, end=0, step=1, value=start_fomc_day, title="Start FOMC Day")
	days_slider = Slider(start=1, end=10, step=1, value=days, title='Multiday Returns')
	reset_button = Button(label="Reset Defaults")
	play_button = Button(label='► Play')
	
	def animate_update():
		next_day = fomc_day_slider.value + 1
		if next_day <= data.index.values.max():
			fomc_day_slider.value = next_day
		else:
			fomc_day_slider.value = start_fomc_day	
	callback_id = None
	def animate():
		global callback_id
		if play_button.label == '► Play':
			play_button.label = '❚❚ Pause'
			callback_id = curdoc().add_periodic_callback(animate_update, 1000)
		else:
			play_button.label = '► Play'
			curdoc().remove_periodic_callback(callback_id)
	play_button.on_click(animate)
	
	def reset_defaults():
		date_picker.value=datetime.now()
		days_slider.value = 5
		start_slider.value = -6
		fomc_day_slider.value = fomc_day()
		date_range_slider.value = date_range
	reset_button.on_click(reset_defaults)
	
	def update_sliders():
		source.data = fomc_day_data()
	
	def date_picker_change(attrname, old, new):
		source.selected = select_fomc(calc_fomc(date_picker.value))
	date_picker.on_change('value', date_picker_change)
	
	def fomc_day_slider_change(attrname, old, new):
		source.selected = select_fomc(fomc_day_slider.value)
		daily_fig.title.text = "Day {0}, Week {1}: Normal Distribution (μ={2:.2}, σ={3:.2})".format(fomc_day_slider.value, fomc_week(), mu(), sigma())
		daily_source.data = daily_data()
	fomc_day_slider.on_change('value', fomc_day_slider_change)
	
	def date_range_slider_update(attrname, old, new):
		date_range = date_range_slider.value_as_datetime
		main_fig.title.text = "Stock returns over the FOMC cycle, {0}-{1}".format(date_range[0].year, date_range[-1].year)
		source.data = fomc_day_data()
	date_range_slider.on_change('value', date_range_slider_update)

	def days_slider_update(attrname, old, new):
		days = days_slider.value
		main_fig.yaxis.axis_label = "Avg. {0}-day stock return, t to t+{1}".format(days, days-1)
		multiday_returns(days)
		fomc = fomc_calendar.join(market, how='inner')
		fomc['fomc_day'] = np.where(fomc['days_prior'].values >= start_slider.value, fomc['days_prior'].values, fomc['days_since'].values)
		date_range = date_range_slider.value_as_datetime
		fomc_range = fomc[date_range[0]:date_range[-1]]
		grouped = fomc_range.groupby('fomc_day').filter(lambda x: len(x) / len(fomc_range) > significance).groupby('fomc_day')
		data = grouped.mean()['returns']
		source.data = dict(zip(['fomc_day','returns'], [data.index.values, data.values]))
		#source.data = fomc_day_data()
	days_slider.on_change('value', days_slider_update)

	def start_slider_update(attrname, old, new):
		fomc['fomc_day'] = np.where(fomc['days_prior'].values >= start_slider.value, fomc['days_prior'].values, fomc['days_since'].values)
		source.data = fomc_day_data()
	start_slider.on_change('value', start_slider_update)
	
	def selected_change(attrname, old, new):
		fomc_day_slider.value = source.data['fomc_day'][source.selected['1d']['indices'][0]]
	source.on_change('selected', selected_change)

	main_fig = figure(plot_width=1000, toolbar_location="below")
	main_fig.title.text = "Stock returns over the FOMC cycle, {0}-{1}".format(date_range[0].year, date_range[-1].year)
	main_fig.line(x='fomc_day', y='returns', source=source)
	main_fig.circle(x='fomc_day', y='returns', source=source)
	main_fig.xaxis.axis_label = "Days since FOMC meeting (weekends excluded)"
	main_fig.yaxis.axis_label = "Avg. {0}-day stock return, t to t+{1}".format(days_slider.value, days_slider.value-1)
	labels = LabelSet(x='fomc_day', y='returns', text='fomc_day', x_offset=5, y_offset=-10, source=source, text_font_size='10pt')
	main_fig.add_layout(labels)
	zero_returns = Span(location=0, dimension='width')
	main_fig.add_layout(zero_returns)
	hover = HoverTool(tooltips=[("FOMC Day", "@fomc_day, μ = $y%)")], mode='vline')
	main_fig.add_tools(hover)
	main_fig.add_tools(CrosshairTool())
	label = Label(x=10, y=10, x_units='screen', y_units='screen', text="Upcoming FOMC Week: {0}".format(fomc_week()))
	main_fig.add_layout(label)
	#current_fomc_day = BoxAnnotation(left=fomc_day_slider.value-1, right=fomc_day_slider.value, fill_alpha=0.1, fill_color='green')
	#main_fig.add_layout(current_fomc_day)

	daily_fig = figure(tools="save", background_fill_color="#E8DDCB")
	daily_fig.title.text = "Day {0}, Week {1}: Normal Distribution (μ={2:.2}, σ={3:.2})".format(fomc_day_slider.value, fomc_week(), mu(), sigma())
	daily_fig.xaxis.axis_label = "returns"
	daily_fig.yaxis.axis_label = "Probility of returns"
	daily_fig.x_range = Range1d(-10, 10)
	daily_fig.quad(top='top', bottom='bottom', left='left', right='right', source=daily_source, fill_color="#036564", line_color="#033649")
	daily_fig.line(x='x', y='pdf', source=daily_source, line_color="#D95B43", line_width=8, alpha=0.7, legend="PDF")
	zero_returns = Span(location=0, dimension='height')
	daily_fig.add_layout(zero_returns)
	daily_fig.legend.location = "center_right"
	daily_fig.legend.background_fill_color = "darkgrey"
	
	columns = [
		TableColumn(field="date", title="date", formatter=DateFormatter()),
		TableColumn(field='fomc_day', title='fomc_day'),
		TableColumn(field='returns', title='returns')
	]
	raw_source = ColumnDataSource(fomc)
	data_table = DataTable(source=raw_source, columns=columns)
	
	def selected_date():
		selected_index = np.where(fomc.index.values==date_picker.value)[0]
		return {'0d': {'glyph': None, 'get_view': {}, 'indices': []}, '1d': {'indices': [selected_index]}, '2d': {'indices': {}}}
	#raw_source.selected = selected_date()

	sliders_group = widgetbox(date_picker, date_range_slider, fomc_day_slider, start_slider, days_slider, reset_button, play_button)
	grid = gridplot([[main_fig, None], [daily_fig, sliders_group], [data_table, None]])
	doc.add_root(grid)
	#doc.add_root(fig1)
	doc.title = "FOMC"
	
server = Server({'/': modify_doc}, num_procs=1)
server.start()

if __name__ == '__main__':
	print('Opening Bokeh application on http://localhost:5006/')
	
	server.io_loop.add_callback(server.show, "/")
	server.io_loop.start()