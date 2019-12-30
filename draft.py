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
