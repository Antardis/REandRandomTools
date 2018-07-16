import pandas as pd
import numpy as np
import os.path
import xlsxwriter
import math
import glob
import time
import statsmodels.api as sm
import matplotlib.pyplot as plt
import datetime as dt
from statsmodels.iolib.summary2 import summary_col
from statsmodels.sandbox.regression.predstd import wls_prediction_std

writer = pd.ExcelWriter('pandas_stat.xlsx', engine='xlsxwriter')
#writer2 = pd.ExcelWriter('excelyear.xlsx', engine='xlsxwriter')

print("--------------------------------")

def filemake(df):
    print("saving....")
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    print("saved")

#For OLS, input trend data with time series. Returns Summary
def OLS(trend):

    y = pd.Series.tolist(trend.iloc[:,0])
    x = list(range(0,len(trend.index)))
    x = sm.add_constant(x)
    ols = sm.OLS(y,x)
    results = ols.fit()
    
    print(trend.columns)
    #=======GRAPH CREATION FROM STACK OVERFLOW 
    prstd, iv_l, iv_u = wls_prediction_std(results)
    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(y, 'o', label="data")
    ax.plot(results.fittedvalues, 'r--.', label="OLS")
    ax.plot(iv_u, 'r--')
    ax.plot(iv_l, 'r--')
    ax.legend(loc='best');
    #==========================================
    
    print(results.summary())  #turn this on to get full results
    print('Parameters: ', results.params)
    print('R2: ', results.rsquared)
    return(results)
   
    
def trend_csd(df):
    csd = sm.tsa.seasonal_decompose(df, model='additive', two_sided=True)
    t = csd.trend
    #s = csd.seasonal
    #e = csd.resid
    #csdplot = csd.plot()
    print(csd)
    t2 = t.dropna()    
    return(t2)

def stats():
    #Part 1: Python needs to create its own time series from your time series
    df = pd.read_csv(r"C:\Users\MarkYap\Desktop\statistical.csv", encoding='cp1252')
    date = df.iloc[:,0:2]
    date.insert(2, 'Day', 1)
    date = pd.to_datetime(date)
    del df['Year']
    del df['Month']
    df.index = date
    
    #Part 2: Create a main DF to aggregate all trend results to.
    dftrend = pd.DataFrame()
    date = date[12:]
    dftrend.insert(0, 'Dummy', date)
    dftrend.index = date

    #Part 3: Process through all trend results
    #d = {}
    inv_count = len(df.iloc[0])-1  #number of inverters in the system
    for i in range(0,inv_count+1): #this counts based on inv_col pos
        inv = df.iloc[:,i:i+1]      #inverter power data
        t = trend_csd(inv)          #turns power column to trend
        OLSresults = OLS(t)
       #t = pd.DataFrame.reset_index(t)
        t.index = dftrend.index    #gives your trends a common index
        dftrend = pd.concat([dftrend,t],axis=1)
        #d["string{0}".format(inv_count)] = OLS(trend_csd(inv))        
    
    del dftrend['Dummy']
    #print(dftrend)
    filemake(dftrend)

stats()


    




