import pandas as pd
import numpy as np
market = pd.read_csv('market.csv', index_col=0, parse_dates=True, infer_datetime_format=True)
t = market['premium'].values/100+1
def multiday_returns(days):
	a = np.copy(t[:1-days])
	for day in range(days-2):
		a *= t[day+1:day-(days-2)]
	a *= t[days-1:]
	market.loc[:1-days,"{0}d".format(days)] = (a-1)*100
for i in range(9):
	multiday_returns(i+2)
fomc_calendar = pd.read_csv('fomc_calendar.csv', index_col=0, parse_dates=True, infer_datetime_format=True)
fomc_final = fomc_calendar.join(market, how='inner')
fomc_final.to_csv('fomc_final.csv')