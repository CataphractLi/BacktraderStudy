# 数据接口
import akshare as ak
import baostock as bs
import tushare as ts

# 基础模块
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import os

# 回测框架
import backtrader as bt


# 数据调整
def ts_fit(data):
    '''
    对Tushare上获得的数据进行统一整理，使符合Backtrader的要求。
    主要步骤有：设定日期索引，规范列名，从小到大排列
    输入：调整之前的DataFrame
    输出：调整过后的DataFrame
    '''
    data.set_index(pd.to_datetime(data[data.columns[0]]), inplace=True)
    data.index.name = 'datetime'
    data.drop(columns=[data.columns[0]], axis=1, inplace = True)
    data.rename(columns={'vol':'volume'}, inplace=True)
    data = data.astype('float')
    return data.iloc[::-1]


# 数据下载
def future_ts(token, future_index,
              start=dt.datetime.now()-dt.timedelta(days=365),
              end=dt.datetime.now(),
              flds='trade_date,open,high,low,close,vol'):
    '''
    从Tushare下载期货日线行情数据。
    输入：Tushare token, 期货合约代码，开始日期，结束日期，数据字段
    输出：期货日线行情数据(DataFrame)
    '''
    pro = ts.pro_api(token)
    df = pro.fut_daily(ts_code=future_index, 
                       fields=flds,
                       start_date=start.strftime('%Y%m%d'), 
                       end_date=end.strftime('%Y%m%d'))
    return ts_fit(df)


def index_ts(token, index_code,
             start=dt.datetime.now()-dt.timedelta(days=365),
             end=dt.datetime.now(),
             flds='trade_date,open,high,low,close,vol'):
    '''
    从Tushare下载指数日线数据。
    输入：Tushare token, 指数代码，开始日期，结束日期，数据字段
    输出：指数日线行情数据(DataFrame)
    '''
    ts.set_token(token)
    pro = ts.pro_api()
    df = pro.index_daily(ts_code=index_code,
                         fields=flds,
                         start_date=start.strftime('%Y%m%d'),
                         end_date=end.strftime('%Y%m%d'))
    return ts_fit(df)


def stock_ts(token, stock_code,fq='D',
             start=dt.datetime.now()-dt.timedelta(days=365),
             end=dt.datetime.now(),
             flds='trade_time,open,high,low,close,vol'):
    '''
    从Tushare下载股票行情数据。
    输入：Tushare token, 股票代码，数据频次，开始日期，结束日期, 数据字段
    输出：股票行情数据(DataFrame)
    注：默认前复权，可在'adj'项中调整。
    '''
    ts.set_token(token)
    pro = ts.pro_api()
    try:
        df = ts.pro_bar(ts_code=stock_code,
                        adj='qfq',
                        freq=fq,
                        start_date=start.strftime('%Y%m%d'),
                        end_date=end.strftime('%Y%m%d'))[flds.split(',')]
        return ts_fit(df)
    except TypeError:
        print(stock_code + ' TypeError, returing empty dataframe.')
        return pd.DataFrame()


def index_comp_ts(token, stock_index, time_sleep=0.5,
                  start=dt.datetime.now()-dt.timedelta(days=365),
                  end=dt.datetime.now(), download=False, fpath='.\\Data\\'):
    '''
    从Tushare下载指数成分股的行情数据。
    输入：Tushare token, 指数代码，数据频次，查询间隔，开始日期，结束日期，是否下载，存储路径
    输出：包含成分股数据的字典(或本地数据文件）
    '''
    if download and not os.path.exists(fpath.rstrip('\\')):
        os.mkdir(fpath.rstrip('\\'))
    pro = ts.pro_api(token)
    index_list = np.unique(pro.index_weight(index_code=stock_index,
                                            start_date=start.strftime('%Y%m%d'),
                                            end_date=end.strftime('%Y%m%d')).con_code).tolist()
    result = dict()
    for s_code in index_list:
        df = stock_ts(token, s_code, start, end)
        result[s_code] = df
        if download:
            df.to_csv(fpath + s_code + '.csv')
        time.sleep(time_sleep)
    return result


def stock_finance(token, stock_code,
                  start=dt.datetime.now()-dt.timedelta(days=365),
                  end=dt.datetime.now()):
    ts.set_token(token)
    pro = ts.pro_api()
    df = pro.fina_indicator(ts_code=stock_code, 
                            start_date=start.strftime('%Y%m%d'),
                            end_date=end.strftime('%Y%m%d'))[['end_date', 'eps', 'netprofit_margin', 'roe_dt']].dropna().drop_duplicates()
    df.rename(columns = {'end_date':'trade_date'}, inplace = True)
    df['trade_date'] = pd.to_datetime(df.trade_date)
    df.index=pd.to_datetime(df.trade_date)
    df.drop('trade_date', axis=1, inplace = True)
    df = df.astype('float')
    return df[::-1]


def stock_finace_full(token, stock_code,
                  fields=['end_date', 'eps', 'netprofit_margin', 'roe_dt'],
                  start=dt.datetime.now()-dt.timedelta(days=365),
                  end=dt.datetime.now()):
    ts.set_token(token)
    pro = ts.pro_api()
    df = pro.fina_indicator(ts_code=stock_code, 
                            start_date=start.strftime('%Y%m%d'),
                            end_date=end.strftime('%Y%m%d'))[fields].dropna().drop_duplicates()
    df.rename(columns = {'end_date':'trade_date'}, inplace = True)
    df['trade_date'] = pd.to_datetime(df.trade_date)
    df.index=pd.to_datetime(df.trade_date)
    df.drop('trade_date', axis=1, inplace = True)
#    df = df.astype('float')
    return df[::-1]


#
class Data_Base(bt.feeds.PandasData):
    '''

    '''

    params = (
        # Possible values for datetime (must always be present)
        #  None : datetime is the "index" in the Pandas Dataframe
        #  -1 : autodetect position or case-wise equal name
        #  >= 0 : numeric index to the colum in the pandas dataframe
        #  string : column name (as index) in the pandas dataframe
        ('datetime', None),

        # Possible values below:
        #  None : column not present
        #  -1 : autodetect position or case-wise equal name
        #  >= 0 : numeric index to the colum in the pandas dataframe
        #  string : column name (as index) in the pandas dataframe
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', None),
    )