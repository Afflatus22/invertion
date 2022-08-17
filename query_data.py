# -*- coding : UTF-8-*-
import tushare as ts
import pandas as pd
import time
import sys
if(sys.version[:1] == "3"):
    import _thread as thread
else:
    import thread 

myfav = []
show = []

def slave(code):
    global show
    global myfav
    # while 1:
    # for i in myfav:
    data = ts.get_realtime_quotes(code)
    show.append(list(data.loc[0,['code','name','price']]))
    # show = [str(data['name']),str(data['price'])]
    # print(data['price'])
    # time.sleep(5)
        # print('work good!')
    # print('work failed!')
    

def GetOnedata(code):
    global myfav
    #df = pro.daily(ts_code = '002349.SZ', start_date='20220113', end_date='20220331')
    #df = ts.pro_bar(trade_date= '20220401', start_date='20210131', end_date= endtime, ma=[50])  获取单个股票信息
    #初始化ts参数
    ts.set_token('df8ba8bf0035f774d5d15c760a7bdf864bd22c45887e9fc7097769f4')
    myfav.append(code)
    t = thread.start_new_thread(slave, (code,))
    time.sleep(1)
    # data.to_csv(path, encoding = 'gbk')

def GetLikeData(time):
    print('like')
    ts.set_token('df8ba8bf0035f774d5d15c760a7bdf864bd22c45887e9fc7097769f4')
    pro = ts.pro_api()
    df = pro.daily(**{"ts_code": "","trade_date": time,"start_date": 20220101,"end_date": endtime,"offset": "","limit": ""}, fields=["ts_code","close"])
    df = pro.stock_basic(market = '主板')
    print(df)
    
    #data = df[['name', 'ts_code']]
    data = {'股票名称':df['name'], '股票代码':df['ts_code']}
    data = pd.DataFrame(data)
    #print(data)
    
    #剔除ST股票
    for i in data['股票名称']:          
        if 'ST' in i:
            data = data.drop(index = (data.loc[i == data['股票名称']].index))
            
    #获取北向资金持股%5以上的股票
    north = pro.hk_hold('trade_date' == '20220412')
    north = north.loc[north['exchange'] == ('SH' or 'SZ')]
    north = north.loc[ north['ratio'] >= 5.0]
    for i in data['股票代码']:
        if  i not in list(north['ts_code']):
            data = data.drop(index = (data.loc[data['股票代码'] == i].index))
    print(data)
    