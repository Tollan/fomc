market = pd.read_csv('http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip',
                      index_col=0, usecols=[0, 1], engine='python', skiprows=4, skipfooter=2, 
                      parse_dates=True, infer_datetime_format=True).asfreq(freq='B', fill_value=0)
#1936 onwards
# 
fomc_load = pd.read_csv('fomc_dates.csv', parse_dates=[0], infer_datetime_format=True)
fomc_dates = fomc_load['fomc_date'].values
# one line

last_fomc = fomc_dates[np.searchsorted(fomc_dates, market.index.values, side='right')-1]
next_fomc = fomc_dates[np.searchsorted(fomc_dates, market.index.values)] 
days_since = np.busday_count(last_fomc.astype('datetime64[D]'), market.index.values.astype('datetime64[D]'))
days_before = -np.busday_count(market.index.values.astype('datetime64[D]'), next_fomc.astype('datetime64[D]'))
fomc_day = np.where(days_before >= -6, days_before, days_since)
fomc_week = (fomc_day+1)//5
market['fomc_day'] = fomc_day
market['fomc_week'] = fomc_week
market = market[market['fomc_week'] > -2]
