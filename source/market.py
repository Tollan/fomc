import pandas as pd

market = pd.read_csv('http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip',
                      index_col=0, usecols=[0, 1], engine='python', skiprows=4, skipfooter=2, 
                      parse_dates=True, infer_datetime_format=True).asfreq(freq='B', fill_value=0)['1936':]
market = market.rename(columns = {'Mkt-RF':'premium'})
market.index.name = 'date'
market.to_csv('market.csv')