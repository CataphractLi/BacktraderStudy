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
e_date = datetime.datetime.now()

if __name__ == '__main__':
    pro = ts.pro_api(token)
    stock_list = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,list_date')
    for index, stock in stock_list.iterrows():
        utilsJ.stock_tushare(token, stock.ts_code, datetime.datetime.strptime(stock.list_date, '%Y%m%d'), e_date).to_csv('.\\Data\\'+stock.ts_code+'.csv')
        time.sleep(0.5)