# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 09:07:18 2019

@author: trenner
"""

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



plotFOMC(100, fomcReturns, FOMCcalendarDf)

plotFOMC(10000, fomcReturns, FOMCcalendarDf)

getFOMCreturns(FOMCcalendarDf, dailyReturns, 4)

for days in np.arange(1, 6):
    plotFOMC(100, getFOMCreturns(FOMCcalendarDf, dailyReturns, days), FOMCcalendarDf)

getFOMCreturns(FOMCcalendarDf, dailyReturns, 1)

    # band = Band(base='mean', lower=np.arange(-6,35)[(np.arange(-6,35)+1)//10 == 0], upper=np.arange(-6,35)[(np.arange(-6,35)+1)//5 == 0], source=source, level='underlay', fill_alpha=1.0, line_width=1, line_color='black')
    # fig1.add_layout(band)

    # current_fomc_day = BoxAnnotation(left=tomorrow_fomc.fomc_day, right=tomorrow_fomc.fomc_day+1, fill_alpha=0.1, fill_color='navy')
    # fig1.add_layout(current_fomc_day)

    # fomcArr = fomcReturns.drop(['Mkt-RF', 'fomc_week'], 1).values
    # # fomcArr = fomcReturns.drop(['bus_week', 'fomc_week'], 1).values  # daily returns alternate
    # df = pd.DataFrame(map(lambda day: confidenceInterval(fomcArr[:, 1][fomcArr[:, 0] == day]), fomcDayRange), index=fomcDayRange, columns=['low', 'mean', 'high'])
    # df.index.name = 'fomc_day'
    # fig1.xgrid.band_fill_alpha = 0.1
    # fig1.xgrid.band_fill_color = "red"
    # band = Band(base='mean', lower=np.arange(-6,35)[(np.arange(-6,35)+1)//10 == 0], upper=np.arange(-6,35)[(np.arange(-6,35)+1)//5 == 0], source=source, level='underlay', fill_alpha=1.0, line_width=1, line_color='black')
    # fig1.add_layout(band)