# 数据接口
from math import floor
import akshare as ak
import baostock as bs
import tushare as ts

# 基础模块
import datetime
import numpy as np
import pandas as pd
import time
import os

# 基础函数
import utilsJ

token = '74f1379591c9d810854fa5891fffcacaba514b82bf17ec2e239025b6'
token2 = '904ff4752522814dca00e032a709fdfc26d8744913500ef204e02157'
stock_filelist = os.listdir('.\\Data\\17-21_30min\\Int\\')

short = 12
long = 26
period = 9

if __name__ == '__main__':
    pro = ts.pro_api(token)
    stock_list = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,list_date')
    added = False
    for index, stock in stock_list.iterrows():
        if stock.ts_code == '603396.SH':
            added = True
        if 'BJ' not in stock.ts_code and added:
            for i in [2017, 2018, 2019, 2020, 2021]:
                file_name = '.\\Data\\17-21_30min\\'+stock.ts_code+str(i)+'.csv'
                if not os.path.exists(file_name):
                    print(file_name)
                    s_date = datetime.date(i,1,1)
                    e_date = datetime.date(i,12,31)
                    df = utilsJ.stock_tushare(token, stock.ts_code, s_date, e_date)
                    if len(df) != 0:
                        df.to_csv(file_name)
                    time.sleep(0.4)

    pro = ts.pro_api(token)
    stock_list = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,list_date')
    for index, stock in stock_list.iterrows():
        df = pd.DataFrame()
        for i in [2017, 2018, 2019, 2020, 2021]:
            file_name = '.\\Data\\17-21_30min\\'+stock.ts_code+str(i)+'.csv'
            if os.path.exists(file_name):
                if len(df) == 0:
                    df = pd.read_csv(file_name)
                else:
                    df_new = pd.read_csv(file_name)
                    df = pd.concat([df, df_new])
        if len(df) != 0:       
            df.to_csv('.\\Data\\17-21_30min\\Int\\'+stock.ts_code+'.csv')

    stock_filelist = os.listdir('.\\Data\\17-21_30min\\Int\\')
    for stock_file in stock_filelist:
        stock_code = stock_file[:9]
        try:
            df = pd.read_csv('.\\Data\\17-21_30min\\Int\\'+stock_file, 
                            converters={'trade_date':lambda x:pd.to_datetime(x)}).set_index('trade_date')
            df.drop(columns=df.columns[[0, -1]], inplace=True)
            df['MA5'] = df.close.rolling(5).mean()
            EMA_short = np.full(len(df), np.nan)
            EMA_long = np.full(len(df), np.nan)
            DEA = np.full(len(df), np.nan)
            EMA_short[short-1] = df.close[short-1]
            EMA_long[long-1] = df.close[long-1]
            for i in range(short, len(df)):
                EMA_short[i] = 2 * df.close[i] / 13 + EMA_short[i-1] * (1 - 2 / 13)
                if i == long - 1:
                    DEA[i] = EMA_short[i] - EMA_long[i]
                else:
                    EMA_long[i] = 2 * df.close[i] / 27 + EMA_long[i-1] * (1 - 2 / 27)
                    DEA[i] = 2 * (EMA_short[i] - EMA_long[i]) / 10 + DEA[i-1] * (1 - 2/10)
            df['DIFF'] = EMA_short - EMA_long
            df['DEA'] = DEA
            df['MACD'] = 2 * (df.DIFF - df.DEA)
            df.to_csv('.\\Data\\17-21_30min\\Int\\MA5MACD\\' + stock_file)
        except:
            print(stock_file)
