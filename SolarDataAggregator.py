
import pandas as pd
import numpy as np
import os.path
import xlsxwriter
import math
import glob
import time
import statsmodels.api as sm
print("--------------------------------")

#-----------------DESCRIPTION---------------------
#This code merely aggregates the data from SMA inverters. 
#I did other parts of my data handling on Excel. 
#This is very specific to my project so alot of editing has to be made

start = time.time()
pypath = r"C:\Users\MarkYap\Desktop\CSV_files2\2011"
writer = pd.ExcelWriter('pandas_simple.xlsx', engine='xlsxwriter')
#writer2 = pd.ExcelWriter('excelyear.xlsx', engine='xlsxwriter')

def filemake(df):
    print("saving....")
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    print("saved")

#----------------------------------------------------------------------------

def hsplit(dfstamp):
    df = dfstamp
    while True:
        try:
            dfhour = df.loc[:,"TimeStamp"].str.split(' ').str.get(1).str.split(':').str.get(0)
            break
        except AttributeError:
            dfhour = df.loc[:,"TimeStamp"].str.split(':').str.get(0)
            break
    return dfhour

def datesplit(fpath):
    base = os.path.basename(fpath)
    date = os.path.splitext(base)[0]
    yearfirst = True
    while True:
        try:
            int(date[0:4])
            break
        except ValueError:
            yearfirst = False
            break  
    if yearfirst == False:
        day = int(date[0:2])
        month = int(date[3:5])
        year = int(date[6:10])  
        rawdf = pd.read_csv(fpath, encoding='cp1252', skiprows=2, header=None, sep=',', error_bad_lines=False)
    elif yearfirst == True:
        year = int(date[0:4])
        month = int(date[5:7])
        day = int(date[8:10])
    return year, month, day


def filename_scan(fpath):
    rawdf = pd.read_csv(fpath, encoding='cp1252', skiprows=2, header=None, error_bad_lines=False)
    x = rawdf.iloc[2]
    x = x[0]
    if ';' in x:
        rawdf = pd.read_csv(fpath, encoding='cp1252', skiprows=2, header=None, sep=';', error_bad_lines=False)
    elif ';' not in x:
        rawdf = pd.read_csv(fpath, encoding='cp1252', skiprows=2, header=None, error_bad_lines=False)
    return rawdf

#---------------------------------------------------------------------------

def rename(df):
    df.rename(columns={
            '2110183843':'Inverter-1','2110018240':'Inverter-2',
            '2110183895':'Inverter-3','2110180932':'Inverter-4',
            '2110192931':'Inverter-5','2110144662':'Inverter-6',
            '2110180596':'Inverter-7','2110192909':'Inverter-8',
            '2110192945':'Inverter-9','2110183847':'Inverter-10',
            '2110180969':'Inverter-11'},inplace = True)
    return df

#inv7,8,9,10: 45.07 deg, inv11:2deg, inv3:26.04deg


def col_pick(raw, df):
    datatype = raw.iloc[2]
    #choices - 'Pac','B.Ms.Amp'
    picker = ['TimeStamp','IntSolIrr','TmpAmb C','TmpMdul C','WindVel km/h']
    picker2 = ['Pac']
    picker = picker + picker2

    col_count = pd.Series.count(df.columns)
    il = pd.Series()  
    i = 0
    while i<col_count:
        if datatype[i] not in picker:
            #print(x, ":",datatype[x])
            il = il.append(pd.Series(i))
        i+=1
    df = df.drop(df.columns[il], axis=1)
    v = raw.iloc[1] 
    df.columns = v.drop(v.index[il])
    df = rename(df)    
    
    #-----name combiner----
    col_count = pd.Series.count(df.columns)
    i = 0
    while i < col_count:
        if df.iloc[1][i] in picker2:
            df.iloc[1][i] = df.columns[i]+':'+df.iloc[1][i] 
        i += 1
        df.iloc[1][i] = df.columns[i]+':'+df.iloc[1][i] 
    
    df2 = df[2:]
    df2.columns = df.iloc[1]
    #print(df.iloc[1])
    return df2

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def cleaner(fpath):
    raw = filename_scan(fpath)
    headers = raw.iloc[1:3]
    values = raw.iloc[4:]
    df = headers.append(values)
    #----- Choosing which labels to keep or delete -------------
    df = col_pick(raw, df)
    hourdf = hsplit(df)
    del df['TimeStamp']
    df.insert(0, 'Hour', hourdf)
    i = 0 
    while i < pd.Series.count(df.columns):
        col = (df.columns[i])
        df[col] = pd.to_numeric(df[col], errors='ignore')
        i += 1
    
    df2 = pd.pivot_table(df, index=['Hour'], aggfunc='mean')
    timeframes = datesplit(fpath)
    #df2.insert(0, 'Hour', df2.index)
    df2.insert(0, 'Day', timeframes[2])
    df2.insert(0, 'Month', timeframes[1])
    df2.insert(0, 'Year', timeframes[0])
    return df2



def csv2(pyfolder):
    maindf = pd.DataFrame()
    for root, dirs, files in os.walk(pyfolder, topdown='True'):
        for name in files:
            fpath = os.path.join(root,name)
            print(fpath)
            df = cleaner(fpath)
            maindf = maindf.append(df)
    return maindf


def csvfolders():
    i = 0
    #year = ["1","2","3","4","5","6","7"]
    year = ["1","2","3","4","5","6","7"]
    maindf = pd.DataFrame()
    while i<len(year):
        pyfolder = r"C:\Users\MarkYap\Desktop\CSV_files2\201"
        pyfolder = pyfolder + year[i]
        df = csv2(pyfolder)
        maindf = maindf.append(df)
        i+=1
    filemake(maindf)

csvfolders()

def single():
    maindf = pd.DataFrame()
    pyth = r"C:\Users\MarkYap\Desktop\CSV_files2\2012\01-11-2012.csv"
    df = cleaner(pyth)
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()

    

def csv():
    maindf = pd.DataFrame()
    pyfolder = r"C:\Users\MarkYap\Desktop\CSV_files2\2011"
    print("processing....")
    for root, dirs, files in os.walk(pyfolder, topdown='True'):
        for name in files:
            fpath = os.path.join(root,name)
            print(fpath)
            df = cleaner(fpath)
            maindf = maindf.append(df)
    print("saving....")
    maindf.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    print("Finished")


end = time.time()
print(end-start)

