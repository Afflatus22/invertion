# --coding: utf-8 --
import datetime
import tushare as ts
import time
import sys
import os
import numpy as np
import efinance as ef
if(sys.version[:1] == "3"):
    import _thread as thread
else:
    import thread 

token = 'df8ba8bf0035f774d5d15c760a7bdf864bd22c45887e9fc7097769f4'
nums = 0
myfav = []
show = []
flash = 0
lock = thread.allocate_lock()
ts.set_token(token) #初始化ts参数

# 期货代码 期货名称 涨跌幅 最新价 最高 最低 今开 涨跌额 换手率 量比 动态市盈率 成交量 成交额  昨日收盘 总市值 流通市值  行情ID 市场类型
# 获取一段时间的期货日K 线数据
# df = ef.futures.get_quote_history(secid, beg=beg, end=end)

def getTimeData(code):
    df = ef.futures.get_realtime_quotes()
    index = df.loc[df['期货代码'] == code].index.tolist()[0]    
    return list(df.loc[index, ['期货代码','期货名称', '最新价','今开']])

def ItemHandle(code, torr):
    global myfav
    global nums
    for i in myfav:
        if code == i:
            if torr == 1:
                myfav.remove(i)
                myfav.append(i)
            elif torr == 0:
                myfav.remove(i)
                myfav.insert(0, i)
            elif torr == 2:
                myfav.remove(i)
                nums -=1
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
    time1 = datetime.datetime.now().strftime('%H%M%S')
    print(time1)
    while 1:       
        flash = getflash()
        if flash == 1:
            # print('接到消息时')
            global show
            global myfav
            global nums
            for i in myfav:
                if i[0].isalpha() == True:
                    code = getTimeData(i)
                    show.append(code)
                else:
                    try:
                        data = ts.get_realtime_quotes(i)
                        codelist = list(data.loc[0,['code','name','price','pre_close']])
                        show.append(codelist)
                    except Exception as e:
                        print(str(e) + '股票代码不存在!')
                        myfav.remove(i)
                        f = open('./myfavlist.txt', 'w', encoding='utf-8')
                        for j in myfav:
                            f.write(j + '\n')
                        nums -= 1
                        f.close()
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
    if code not in myfav:
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
        f = open(path, 'r', encoding='utf-8')
        items = f.readlines()
        for i in items:
            if i.strip('\n') != '':
                myfav.append(i.strip('\n'))
                nums += 1
        f.close()
    else:
        f = open(path, 'w', encoding='utf-8')
        f.close()

def GetDvRatioFromtushare():
    pro = ts.pro_api(token=token)
    df1 = pro.daily_basic(trade_date = '202201010')
    df1.set_index(['ts_code'], inplace = True)
    df1 = df1[['dv_ratio']]
    df1 = df1.sort_values('dv_ratio', ascending=False)
    print(df1)
