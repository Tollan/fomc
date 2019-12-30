# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 09:07:18 2019

@author: trenner
"""

fomcDates = np.loadtxt('FOMCdates.csv', dtype='datetime64[D]', delimiter=',')

def vCalcFOMCday(fomcDates, dates, lookback = -6):
    idx = fomcDates.searchsorted(dates)
    daysTo = np.busday_count(fomcDates[idx], dates)
    idx[idx>0] -= 1
    daysSince = np.busday_count(fomcDates[idx], dates)
    return np.where(daysTo >= lookback, daysTo, daysSince)

def vCalcFOMCweek(fomcDays):
    return (fomcDays+1)//5

fomcDays = vCalcFOMCday(fomcDates, dates)
fomcWeeks = vCalcFOMCweek(fomcDays)

(fomcDates, fomcDays, fomcWeeks)

np.datetime64(datetime.now().date())

###

import numpy as np, scipy.stats as st
st.t.interval(0.95, len(a)-1, loc=np.mean(a), scale=st.sem(a))

# vectorize
# https://stackoverflow.com/questions/15033511/compute-a-confidence-interval-from-sample-data

np.mean(np.split(fomcDays, np.where(fomcDays == -6)[0]))

np.vstack(np.split(fomcDays, np.where(fomcDays == -6)[0][:35]))

np.vstack(np.split(fomcDays, np.where(fomcDays == -6)[0])[:35])
np.split(fomcDays, np.where(fomcDays == -6)[0])[:,0:35]

fomcDays == np.arange(-6, 35)
np.equal(fomcDays, np.arange(-6, 35))

np.meshgrid(fomcDays,np.arange(-6, 35))
np.logical_and(fomcDays,np.arange(-6, 35))

np.split(fomcDays, np.digitize(fomcDays,np.arange(-6, 35)))

arr1inds = arr1.argsort()
sorted_arr1 = arr1[arr1inds[::-1]]
sorted_arr2 = arr2[arr1inds[::-1]]

record.mean(axis=0)
np.average(record, axis=0)