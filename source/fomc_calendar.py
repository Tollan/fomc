import pandas as pd
import numpy as np

fomc_dates = pd.read_csv('fomc_dates.csv', index_col=0, parse_dates=True, infer_datetime_format=True).index.values
calendar = pd.bdate_range(fomc_dates[0], fomc_dates[-1])
last_fomc = fomc_dates[np.searchsorted(fomc_dates, calendar.values, side='right')-1]
next_fomc = fomc_dates[np.searchsorted(fomc_dates, calendar.values)]
days_since = np.busday_count(last_fomc.astype('datetime64[D]'), calendar.values.astype('datetime64[D]'))
days_prior = -np.busday_count(calendar.values.astype('datetime64[D]'), next_fomc.astype('datetime64[D]'))
fomc_calendar = pd.DataFrame(data={'days_since': days_since, 'days_prior': days_prior}, index=calendar)
fomc_calendar.index.name = 'date'
fomc_calendar.to_csv('fomc_calendar.csv')