# 数据接口
from math import floor
import akshare as ak
import baostock as bs
import tushare as ts

# 基础模块
import datetime as dt
import numpy as np
import pandas as pd
import time
import os

# 基础函数
import utilsJ

startdate = dt.datetime(2000,1,1)
enddate = dt.datetime.now()

if __name__ == '__main__':
    stock_list = utilsJ.get_stock_list()
    for stock in stock_list:
        utilsJ.stock_ts(stock,start=startdate,end=enddate).to_csv('.\\Data\\'+stock+'.csv')
        time.sleep(0.5)