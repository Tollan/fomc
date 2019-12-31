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

###

fomcReturns = getFOMCreturns()
fomcReturns
fomcReturns['bus_week'].values
dates = fomcReturns.index.values.astype('datetime64[D]')

fomcDays = vCalcFOMCday(fomcDates, dates)
sortedDays = fomcDays[fomcDays.argsort()]
a = np.split(sortedDays, np.unique(sortedDays, return_index=True)[1])
a

np.vstack(np.hsplit(sortedDays, np.unique(sortedDays, return_index=True)[1]))
xmean = np.vectorize(np.mean)
xmean(a)

ci = np.vectorize(lambda x: st.t.interval(0.95, len(x)-1, loc=np.mean(x), scale=st.sem(x)))
ci(a)
len(a)
a
st.t.interval(0.95, len(a)-1, loc=np.mean(a), scale=st.sem(a))
a

fomcArr = np.transpose(np.array((fomcDays, fomcReturns['bus_week'].values)))
fomcArr[:,1]

%timeit pd.DataFrame(map(lambda day: confidenceInterval(fomcArr[:, 1][fomcArr[:, 0] == day]), range(-6,35)))

%timeit [ fomcArr[:, 1][fomcArr[:, 0] == day] for day in range(-6,35) ]
q = np.array([ fomcArr[:, 1][fomcArr[:, 0] == day] for day in range(-6,35) ])
%timeit [ confidenceInterval(x) for x in [ fomcArr[:, 1][fomcArr[:, 0] == day] for day in range(-6,35) ] ]

q[0]

%timeit confidenceInterval(q[0])

import pstats

import cProfile

cProfile.run('[ confidenceInterval(x) for x in [ fomcArr[:, 1][fomcArr[:, 0] == day] for day in range(-6,35) ] ]')

def confidenceInterval(arr, confidence=0.90):
    n = len(arr)
    m = arr.mean()
    std_err = sem(arr)
    h = std_err * t.ppf((1 + confidence) / 2, n - 1)
    return (m - h, m, m + h)

%timeit lengths = list(map(len,q))
%timeit vec = np.vectorize(lambda x: t.ppf((1 + 0.95) / 2, x - 1))
%timeit vec(lengths)

(1 + 0.95) / 2
%timeit t.ppf(0.975,700)
.2*40

confidenceInterval(q[0])
confidenceInterval2(q[0])

%timeit confidenceInterval(q[0])
%timeit confidenceInterval2(q[0])

%timeit q[0].size

%timeit len(q[0])

%timeit q[0].sum()/q[0].size
%timeit q[0].mean()

def confidenceInterval2(arr, confidence=0.95):
    n = arr.size
    mu = arr.sum()/n
    std_err = arr.std()/n**0.5
    h = std_err * t.ppf((1 + confidence) / 2, n - 1)
    return (mu - h, mu, mu + h)

[ confidenceInterval(x) for x in [ fomcArr[:, 1][fomcArr[:, 0] == day] for day in range(-6,35) ] ]

np.array(a)

q[0].std()/np.sqrt(q[0].size)
sem(q[0])
q[0].size

%timeit np.sqrt(777)
%timeit 777**0.5

#https://machinelearningmastery.com/how-to-code-the-students-t-test-from-scratch-in-python/