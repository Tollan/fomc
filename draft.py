# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 09:07:18 2019

@author: trenner
"""

import pandas as pd
import numpy as np
from os import path

def loadReturns():
    # http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html
    if path.exists("F-F_Research_Data_Factors_daily_CSV.zip"):
        filename = "F-F_Research_Data_Factors_daily_CSV.zip"
    else:
        filename = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip"
    return pd.read_csv(filename, index_col=0, usecols=[0, 1], engine='python', skiprows=4, skipfooter=2,
        parse_dates=True, infer_datetime_format=True, compression='zip')

dailyReturns = loadReturns()

def test1(dailyReturns):
    return np.min((dailyReturns.values[:-1], dailyReturns.values[1:]), axis=0)

def test2(dailyReturns):
    return np.min(np.stack((dailyReturns.values[:-1], dailyReturns.values[1:])), axis=0)

def test3(dailyReturns):
    return np.min(np.hstack((dailyReturns.values[:-1], dailyReturns.values[1:])), axis=1)

def test4(dailyReturns):
    return np.where(dailyReturns.values[:-1] < dailyReturns.values[1:], dailyReturns.values[:-1], dailyReturns.values[1:])


test2(dailyReturns)
test3(dailyReturns)
%timeit test1(dailyReturns)
%timeit test4(dailyReturns)

returns = dailyReturns.values

def test5(returns, lookback=5):
    for n in range(lookback-1):
        returns = np.where(returns[1:] < returns[:-1], returns[1:], returns[:-1])
    return returns

test5(returns)[:10]

def test6(returns, lookback=5):
    a = np.hstack((returns[:-1], returns[1:]))
    for n in range(lookback-2):
        a = np.hstack((a[:-1], a[1:,-1:]))
    return a.min(axis=1)

test6(returns)[:10]

%timeit test5(returns)
%timeit test6(returns)
%timeit test7(returns)

def test7(returns, lookback=5):
    for n in range(lookback-1):
        trues = (returns[1:] > returns[:-1])[:,0]
        returns[1:][trues] = returns[:-1][trues]
    return returns

test7(returns)[:10]

(returns[1:] > returns[:-1])[:,0].shape
returns[1:].shape
returns

###
# Maximizing returns

returns.shape
returns[returns >= 0].size/returns.size # percent postive returns
np.logical_and(returns[1:] >= 0, returns[:-1] >= 0).sum()/returns[returns >= 0].size # percent postive returns following negative returns
np.logical_and(returns[1:] >= 0, returns[:-1] < 0).sum()/returns[returns >= 0].size # percent postive returns following postive returns

returns[returns < 0].size/returns.size # percent negative returns
np.logical_and(returns[1:] < 0, returns[:-1] < 0).sum()/returns[returns < 0].size # percent negative returns following negative returns
np.logical_and(returns[1:] < 0, returns[:-1] >= 0).sum()/returns[returns < 0].size # percent negative returns following postive returns

prices = (returns/100+1).cumprod()

returns[5:][(prices[4:] > test5(prices))[:-1]].size
returns[5:].size
(returns[5:][(prices[4:] > test5(prices))[:-1]]/100+1).prod()
(returns[5:]/100+1).prod()

(returns[returns >= 0]/100+1).prod()

prices[:10]
test5(prices)[:10]




###
# scipy.stats as st
# st.t.interval(0.95, len(a)-1, loc=np.mean(a), scale=st.sem(a))


# np.mean(np.split(fomcDays, np.where(fomcDays == -6)[0]))

# np.vstack(np.split(fomcDays, np.where(fomcDays == -6)[0][:35]))

# np.vstack(np.split(fomcDays, np.where(fomcDays == -6)[0])[:35])
# np.split(fomcDays, np.where(fomcDays == -6)[0])[:,0:35]

# fomcDays == np.arange(-6, 35)
# np.equal(fomcDays, np.arange(-6, 35))

# np.meshgrid(fomcDays,np.arange(-6, 35))
# np.logical_and(fomcDays,np.arange(-6, 35))

# np.split(fomcDays, np.digitize(fomcDays,np.arange(-6, 35)))

# arr1inds = arr1.argsort()
# sorted_arr1 = arr1[arr1inds[::-1]]
# sorted_arr2 = arr2[arr1inds[::-1]]

# record.mean(axis=0)
# np.average(record, axis=0)

# ###

# fomcReturns = getFOMCreturns()
# fomcReturns
# fomcReturns['bus_week'].values
# dates = fomcReturns.index.values.astype('datetime64[D]')

# fomcDays = vCalcFOMCday(fomcDates, dates)
# sortedDays = fomcDays[fomcDays.argsort()]
# a = np.split(sortedDays, np.unique(sortedDays, return_index=True)[1])
# a

# np.vstack(np.hsplit(sortedDays, np.unique(sortedDays, return_index=True)[1]))
# xmean = np.vectorize(np.mean)
# xmean(a)

# ci = np.vectorize(lambda x: st.t.interval(0.95, len(x)-1, loc=np.mean(x), scale=st.sem(x)))
# ci(a)
# len(a)
# a
# st.t.interval(0.95, len(a)-1, loc=np.mean(a), scale=st.sem(a))

#https://machinelearningmastery.com/how-to-code-the-students-t-test-from-scratch-in-python/

####



# def findMin(returns, lookback = 5):
#     returns[:-1]
