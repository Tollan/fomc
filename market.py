import pandas as pd
import numpy as np

fomc_dates = pd.read_csv('fomc_dates.csv', index_col=0, parse_dates=True, infer_datetime_format=True).index.values
calendar = pd.bdate_range(fomc_dates[0], fomc_dates[-1])
last_fomc = fomc_dates[np.searchsorted(fomc_dates, calendar.values, side='right')-1]
next_fomc = fomc_dates[np.searchsorted(fomc_dates, calendar.values)]
days_since = np.busday_count(last_fomc.astype('datetime64[D]'), calendar.values.astype('datetime64[D]'))
days_before = -np.busday_count(calendar.values.astype('datetime64[D]'), next_fomc.astype('datetime64[D]'))
fomc_calendar = pd.DataFrame(data={'days_since': days_since, 'days_before': days_before}, index=calendar)
fomc_calendar.index.name = 'date'
fomc_calendar.to_csv('fomc_calendar')

market = pd.read_csv('http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip',
                      index_col=0, usecols=[0, 1], engine='python', skiprows=4, skipfooter=2, 
                      parse_dates=True, infer_datetime_format=True).asfreq(freq='B', fill_value=0)['1936':]
market.to_csv('market')