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
def ts_fit(data:pd.DataFrame) -> pd.DataFrame:
    '''
    对Tushare上获得的数据进行统一整理,使符合Backtrader的要求.
    主要步骤有：设定日期索引,从小到大排列,浮点数化
    输入:调整之前的DataFrame
    输出:调整过后的DataFrame
    '''
    data.set_index(pd.to_datetime(data[data.columns[0]]), inplace=True)
    data.index.name = 'datetime'
    data.drop(columns=[data.columns[0]], axis=1, inplace=True)
    if 'vol' in data.columns:
        data.rename(columns = {'vol':'volume'}, inplace=True)
    try:
        data = data.astype('float')
        return data.iloc[::-1]
    except:
        return data.iloc[::-1]


# 数据下载
## 行情数据
def future_ts(future_code:str, start:dt.date, end:dt.date,
              flds:str='trade_date,open,high,low,close,vol') -> pd.DataFrame:
    '''
    从Tushare下载期货日线行情数据.
    输入:期货合约代码，开始日期，结束日期，数据字段
    输出:期货日线行情数据(DataFrame)
    '''
    pro = ts.pro_api(load_token())
    df = pro.fut_daily(ts_code=future_code,
                       fields=flds,
                       start_date=start.strftime('%Y%m%d'), 
                       end_date=end.strftime('%Y%m%d'))
    return ts_fit(df)


def index_ts(index_code:str, start:dt.date, end:dt.date,
             flds:str='trade_date,open,high,low,close,vol') -> pd.DataFrame:
    '''
    从Tushare下载指数日线数据.
    输入:指数代码,开始日期,结束日期,数据字段
    输出:指数日线行情数据(DataFrame)
    '''
    pro = ts.pro_api(load_token())
    df = pro.index_daily(ts_code=index_code,
                         fields=flds,
                         start_date=start.strftime('%Y%m%d'),
                         end_date=end.strftime('%Y%m%d'))
    return ts_fit(df)


def index_comp_ts(stock_index:str, start:dt.date, end:dt.date, 
                  time_sleep:float=0.5, download:bool=False, fpath:str='.\\Data\\') -> pd.DataFrame:
    '''
    从Tushare下载指数成分股的行情数据.
    输入:指数代码,数据频次,查询间隔,开始日期,结束日期,是否下载,存储路径
    输出:包含成分股数据的字典(或同时生成本地数据文件）
    '''
    if download and not os.path.exists(fpath.rstrip('\\')):
        os.mkdir(fpath.rstrip('\\'))
    pro = ts.pro_api(load_token())
    index_list = np.unique(pro.index_weight(index_code=stock_index,
                                            start_date=start.strftime('%Y%m%d'),
                                            end_date=end.strftime('%Y%m%d')).con_code).tolist()
    result = dict()
    for s_code in index_list:
        df = stock_ts(s_code, start, end)
        result[s_code] = df
        if download:
            df.to_csv(fpath + s_code + '.csv')
        time.sleep(time_sleep)
    return result


def stock_ts(stock_code:str, start:dt.date, end:dt.date,
             fq:str='D', flds:str='trade_date,open,high,low,close,vol') -> pd.DataFrame:
    '''
    从Tushare下载股票行情数据.
    输入:股票代码,数据频次,开始日期,结束日期,数据字段
    输出:股票行情数据(DataFrame)
    注:默认前复权，可在'adj'项中调整。
    '''
    pro = ts.pro_api(load_token())
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


def get_stock_list() -> list:
    '''
    从Tushare下载当前在交易所交易的股票.
    输入:无
    输出:包含股票代码的列表
    注:剔除北交所交易的股票
    '''
    pro = ts.pro_api(load_token())
    full_list = np.unique(pro.query('stock_basic', exchange='', list_status='L', fields='ts_code')).tolist()
    return [x for x in full_list if 'BJ' not in x]


def get_index_components(index_code:str, start:dt.date, end:dt.date) -> np.array:
    '''
    从Tushare上下载指定区间对应指数的成分表.
    输入：指数代码,开始日期,结束日期
    输出: 对应指数的成分股
    注:由于成分股会调整，该函数无法反映某支成分股被剔除/新加入的影响，从而导致选出比成分股个数稍多的股票.
    例如:选出350支沪深300的成分股.
    可能的解决办法：尽量缩小指定的时间区间
    '''
    pro = ts.pro_api(load_token())
    index_list = np.unique(pro.index_weight(index_code=index_code,
                                            start_date=start.strftime('%Y%m%d'),
                                            end_date=end.strftime('%Y%m%d')).con_code).tolist()
    return index_list


## 基本面数据
def finance_ts(stock_code:str, start:dt.time, end=dt.time,
               flds:str='end_date,eps,netprofit_margin,roe_dt') -> pd.DataFrame:
    '''
    从Tushare下载个股的基本面数据.
    输入:股票代码,数据字段,开始日期,结束日期
    输出:个股的基本面指标
    '''
    pro = ts.pro_api(load_token())
    df = pro.fina_indicator(ts_code=stock_code, 
                            start_date=start.strftime('%Y%m%d'),
                            end_date=end.strftime('%Y%m%d'))[flds.split(',')].dropna().drop_duplicates()
    return ts_fit(df)


# 数据读取
def load_token() -> str:
    '''
    从本地读取Tushare token.
    输入:无
    输出:Tushare token
    '''
    with open('token.txt', 'r') as f:
        token = f.readline()
    return token


def get_stock(stock_code:str,
              start:dt.date, 
              end:dt.date) -> pd.DataFrame:
    '''
    尝试从本地读取股票行情数据.如本地不存在,则从Tushare下载数据.
    输入:股票代码,开始日期,结束日期
    输出:股票行情数据
    '''
    if os.path.exists('.\\Data\\'+stock_code+'.csv'):
        df = pd.read_csv('.\\Data\\'+stock_code+'.csv',
                         converters={'datetime':lambda x:pd.to_datetime(x)}).set_index('datetime')
        return df[(df.index >= start) & (df.index <= end)]
    else:
        return stock_ts(stock_code, start=start, end=end)