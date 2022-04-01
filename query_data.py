import tushare as ts
import pandas as pd
import datetime
import os

#保存文件路径
path = 'output.csv'
#初始化ts参数
ts.set_token('df8ba8bf0035f774d5d15c760a7bdf864bd22c45887e9fc7097769f4')
pro = ts.pro_api()
#获取日线参数
time = datetime.datetime
endtime = time.strftime(time.now(), '%Y%m%d')

print(endtime)
df = pro.daily(**{
    "ts_code": "002349.SZ",
    "trade_date": "",
    "start_date": 20220101,
    "end_date": endtime,
    "offset": "",
    "limit": ""
}, fields=[
    "trade_date",
    "close"
])
#df = pro.daily(ts_code = '002349.SZ', start_date='20220113', end_date='20220331')
df = ts.pro_bar(ts_code='002349.SZ', start_date='20210331', end_date= endtime, ma=[50])
df.to_csv(path)
os.system(path)