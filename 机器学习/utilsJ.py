# 数据接口
import akshare as ak
import baostock as bs
import tushare as ts

# 基础模块
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import threading
import os


# 内部函数
## 以Backtrader为准调整Dataframe样式
def bt_mod(data):
    data.index=pd.to_datetime(data.trade_date)
    data.drop('trade_date', axis=1, inplace = True)
    data = data.astype('float')
    data.rename(columns = {'vol':'volume'}, inplace = True)
    data['openinterest'] = 0
    return data.iloc[::-1]


# 外部函数
def future_tushare(token, future_index,
                   start=datetime.datetime.now() - datetime.timedelta(days = 365),
                   end=datetime.datetime.now()):
    pro = ts.pro_api(token)
    df = pro.fut_daily(ts_code=future_index, 
                       fields='trade_date,open,high,low,close,vol',
                       start_date=start.strftime('%Y%m%d'), 
                       end_date=end.strftime('%Y%m%d'))
    return bt_mod(df)


def index_tushare(token, stock_code,
                  start=datetime.datetime.now()-datetime.timedelta(days=365),
                  end=datetime.datetime.now()):
    ts.set_token(token)
    pro = ts.pro_api()
    df = pro.index_daily(ts_code=stock_code,
                         fields='trade_date,open,high,low,close,vol',
                         start_date=start.strftime('%Y%m%d'),
                         end_date=end.strftime('%Y%m%d'))
    return bt_mod(df)


def stock_tushare(token, stock_code,
                  start=datetime.datetime.now()-datetime.timedelta(days=365),
                  end=datetime.datetime.now()):
    ts.set_token(token)
    pro = ts.pro_api()
    df = ts.pro_bar(ts_code=stock_code,
                    adj='qfq',
                    start_date=start.strftime('%Y%m%d'),
                    end_date=end.strftime('%Y%m%d'))[['trade_date','open','high','low','close','vol']]
    return bt_mod(df)


def index_to_csv_tushare(token, stock_index, time_sleep=0.5,
                         start=datetime.datetime.now()-datetime.timedelta(days=365),
                         end=datetime.datetime.now(), fpath='.\\Data\\'):
    if not os.path.exists(fpath.rstrip('\\')):
        os.mkdir(fpath.rstrip('\\'))
    pro = ts.pro_api(token)
    index_list = np.unique(pro.index_weight(index_code=stock_index,
                                            start_date=start.strftime('%Y%m%d'),
                                            end_date=end.strftime('%Y%m%d')).con_code).tolist()
    for s_code in index_list:
        df = stock_tushare(token, s_code, start, end)
        time.sleep(time_sleep)
        df.to_csv(fpath + s_code + '.csv')
    return


class MyThread(threading.Thread):
    def __init__(self, func, args):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.result = None

    def run(self):
        self.result = self.func(*self.args)

    def getResult(self):
        return self.result