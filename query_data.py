# -*- coding : UTF-8-*-
from asyncio import Semaphore
import tushare as ts
import pandas as pd
import time
import sys
import os
import threading
if(sys.version[:1] == "3"):
    import _thread as thread
else:
    import thread 

nums = 0
myfav = []
show = []
flash = 0
sem = threading.Semaphore(1)
lock = thread.allocate_lock()

def MoveTopOrRoot(code, torr):
    global myfav
    for i in myfav:
        if code == i:
            if torr == 1:
                myfav.remove(i)
                myfav.append(i)
            else:
                myfav.remove(i)
                myfav.insert(0, i)
    f = open('./myfavlist.txt', 'w', encoding='utf-8')
    for i in myfav:
        f.write(i + '\n')
    f.close()

def getnums():
    global nums
    return nums

def getflash():
    lock.acquire()
    global flash
    return flash

def setflash(set, islock):
    if islock == 1:
        lock.acquire()
    global flash
    flash = set
    lock.release()

def slave():
    while 1:
        flash = getflash()
        if flash == 1:
            # print('接到消息时')
            global show
            global myfav
            for i in myfav:
                data = ts.get_realtime_quotes(i)
                show.append(list(data.loc[0,['code','name','price','pre_close']]))
            setflash(0,0)
            time.sleep(0.3)
            # print('完成工作')
        else:
            # print('空闲中')
            lock.release()
            time.sleep(0.2)
    print('work failed!')

def GetOnedata(code):
    global myfav
    global nums
    #初始化ts参数
    ts.set_token('df8ba8bf0035f774d5d15c760a7bdf864bd22c45887e9fc7097769f4')
    myfav.append(code)
    f = open('./myfavlist.txt', 'a', encoding='utf-8')
    f.write(code + '\n')
    nums += 1
    f.close()

def GetItemsFromFile():
    global myfav
    global nums
    nums = 0
    path = './myfavlist.txt'
    if os.access(path, os.F_OK):
        f = open(path, 'r', encoding= 'utf-8')
        items = f.readlines()
        for i in items:
            if i.strip('\n') != '':
                myfav.append(i.strip('\n'))
                nums += 1
        f.close()
    else:
        f = open(path, 'w', encoding='utf-8')
        f.close()

def GetLikeData(time):
     #df = pro.daily(ts_code = '002349.SZ', start_date='20220113', end_date='20220331')
    #df = ts.pro_bar(trade_date= '20220401', start_date='20210131', end_date= endtime, ma=[50])  获取单个股票信息
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
    # data.to_csv(path, encoding = 'gbk')