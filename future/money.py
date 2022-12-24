import requests
import sys
import os
import json
import numpy as np
import efinance as ef
import time
import threading
from tqsdk import TqApi, TqAuth, TqAccount, TqKq, TargetPosTask

class plan():
    def __init__(self, api, obj, dir, delta, num, step, path):
        self.have = 0
        self.last = 0
        self.now = 0
        self.order = ''
        self.api = api
        self.obj = obj
        self.dir = dir
        self.delta = delta
        self.num = num
        self.step = step
        self.path = path
        self.high = 0
        self.low = 0
    def buyit(self):
        if self.dir == 0:
            self.order = self.api.insert_order(symbol= self.obj, direction="BUY", offset="CLOSETODAY", limit_price= self.now+self.step, volume=self.num)
        elif self.dir == 1:
            self.order = self.api.insert_order(symbol= self.obj, direction="BUY", offset="OPEN", limit_price= self.now+self.step, volume=self.num)
    def sellit(self):
        if self.dir == 0:
            self.order = self.api.insert_order(symbol= self.obj, direction="SELL", offset="OPEN", limit_price= self.now-self.step, volume=self.num)
        elif self.dir == 1:
            self.order = self.api.insert_order(symbol= self.obj, direction="SELL", offset="CLOSETODAY", limit_price= self.now-self.step, volume=self.num)

class wzhplan():
    def __init__(self, api, obj, volume, maxnum, maxloss, path):
        self.api = api
        self.obj = obj
        self.volume = volume
        self.maxnum = maxnum
        self.maxloss = maxloss
        self.path = path

# DCE
# 大连商品交易所
# CZCE
# 郑州商品交易所
def waitMarketopen(show):
    while True:
        timenow = time.strftime('%H%M%S', time.localtime(time.time()))
        if show:
            print(timenow)
        if int(timenow) > 90005 and int(timenow) < 101500:
            print("begin!")
            break
        if int(timenow) > 103005 and int(timenow) < 113000:
            print("begin!")
            break
        if int(timenow) > 133005 and int(timenow) < 150000:
            print("begin!")
            break
        if int(timenow) > 210005 and int(timenow) < 230000:
            print("begin!!")
            break
        time.sleep(5)

#记录上次买卖的价格
def logPrice(path, data, rw):
    price = 0
    if rw == 1:
        f = open(path, 'w', encoding='utf-8')
        f.write(str(data))
        f.close()
    else:
        f = open(path, 'r', encoding='utf-8')
        items = f.readlines()
        for i in items:
            print(i)
            price = float(i)
        f.close()
    return price

def logJson(path, data, rw):
    if rw == 1:
        a = json.dumps(data)
        f = open(path, 'w', encoding='utf-8')
        f.write(a)
        f.close()
    else:
        f = open(path, 'r', encoding='utf-8')
        items = f.read()
        a = json.loads(items)
        f.close()
    return a

#网格交易策略 
def gridTrade(plan):
    if os.access(plan.path, os.F_OK) == 0:
        f = open(plan.path, 'w', encoding='utf-8')
        f.close()
    haveit = 0
    sellorbuy = 0
    
    account =  plan.api.get_account()     #获取账户信息
    quote =  plan.api.get_quote(plan.obj) #淀粉合约
    lev =  plan.api.get_position(plan.obj)    #获取持仓情况
    
    print("品种：%s，空头持仓： %d，多头持仓：%d"%(plan.obj, lev.pos_short, lev.pos_long))
    print("\n")
    print("可用资金：%f，浮动盈亏：%f"%(account.available, account.float_profit))

    #确定是否有持仓
    if plan.dir == 1:
        if lev == {} or lev.volume_long == 0:
            plan.order = plan.api.insert_order(symbol=plan.obj, direction="BUY", offset="OPEN", limit_price = quote.last_price+plan.step, volume=200)
            sellorbuy = 2
        else:
            plan.last = lev.open_price_long
            plan.have = lev.volume_long
            plan.order = lev
            haveit = 1
    else:
        if lev == {} or lev.volume_short == 0:
            if plan.dir == 0:
                plan.order = plan.api.insert_order(symbol=plan.obj, direction="SELL", offset="OPEN", limit_price = quote.last_price+plan.step, volume=200)
            sellorbuy = 2
        else:
            plan.last = lev.open_price_short
            plan.have = lev.volume_short
            plan.order = lev
            haveit = 1
    

    while True:
        # async with plan.api.register_update_notify() as update_chan:
        #     async for _ in update_chan:
        #         if plan.api.is_changing(quote,"last_price"):
        #             print(quote.datetime, quote.last_price)

        waitMarketopen(0)
        plan.api.wait_update()
        print("剩余资金：" + str(account.available))
        print("商品现价：%s"%(quote.last_price))

        if plan.api.is_changing(quote, "last_price"):
            #确定当前价
            plan.now = quote.last_price

            #确定过去成交价
            if haveit == 0:
                while True:
                    if plan.order.status == "FINISHED":
                        print("价格：%s,单状态: %s, 已成交: %d 手, 盈亏：%f" % (plan.order.limit_price,plan.order.status, plan.order.volume_orign - plan.order.volume_left, lev.float_profit))
                        break
                    plan.api.wait_update()
                    print("价格：%s,单状态: %s, 已成交: %d 手, 盈亏：%f" % (plan.order.limit_price,plan.order.status, plan.order.volume_orign - plan.order.volume_left, lev.float_profit))
                    time.sleep(1)
                # print("价格：%s,单状态: %s, 已成交: %d 手, 盈亏：%f" % (plan.order.limit_price,plan.order.status, plan.order.volume_orign - plan.order.volume_left, lev.float_profit))
                if plan.order.volume_orign - plan.order.volume_left != 0 :
                    plan.last = plan.order.limit_price
                    logPrice(plan.path, plan.last, 1)
            elif plan.dir == 1:
                # print("价格：%s, 盈亏：%f" % (plan.order.position_price_long, plan.order.float_profit))
                plan.last = logPrice(plan.path, plan.last, 0)
            elif plan.dir == 0:
                # print("价格：%s, 盈亏：%f" % (plan.order.position_price_short, plan.order.float_profit))
                plan.last = logPrice(plan.path, plan.last, 0)

            #确定持仓量
            if plan.dir == 1:
                if sellorbuy == 2:
                    plan.have = plan.have + plan.order.volume_orign - plan.order.volume_left
                    sellorbuy = 0
                elif sellorbuy == 1:
                    plan.have = plan.have - plan.order.volume_orign + plan.order.volume_left
                    sellorbuy = 0
            else:
                if sellorbuy == 1:
                    plan.have = plan.have + plan.order.volume_orign - plan.order.volume_left
                    sellorbuy = 0
                elif sellorbuy == 2:
                    plan.have = plan.have - plan.order.volume_orign + plan.order.volume_left
                    sellorbuy = 0
            
            print("now:%s,have:%s,last:%s"%(plan.now, plan.have, plan.last))

            if plan.now > plan.last + plan.delta:
                sellorbuy = 1
                print("sell it!")
                plan.sellit()
                haveit = 0
            elif plan.now < plan.last - plan.delta:
                sellorbuy = 2
                print("buy it!")
                plan.buyit()
                haveit = 0
            print("\n")
    # 关闭api,释放资源
    plan.api.close()

#拐点策略
def wzhTrade(plan):

    if os.access(plan.path, os.F_OK) == 0:
        f = open(plan.path, 'w', encoding='utf-8')
        f.close()
    
    account =  plan.api.get_account()     #获取账户信息
    quote =   plan.api.get_quote(plan.obj) #淀粉合约
    lev =   plan.api.get_position(plan.obj)    #获取持仓情况
    target = TargetPosTask(plan.api, plan.obj)
    
    print("品种：%s，空头持仓： %d，多头持仓：%d"%(plan.obj, lev.pos_short, lev.pos_long))
    print("\n")
    print("可用资金：%f，平仓盈亏：%f"%(account.available, account.close_profit))

    #初始化
    last = quote.last_price #上次成交价格
    high = quote.last_price
    low = quote.last_price
    status = 0  #此前趋势
    dir = 0     #当前趋势
    now = quote.last_price
       
    while True:
        
        # async with plan.api.register_update_notify() as update_chan:
        #     async for _ in update_chan:
        #         if plan.api.is_changing(quote,"last_price"):
        #             print(quote.datetime, quote.last_price)
        plan.api.wait_update()
        waitMarketopen(0)
        if plan.api.is_changing(quote,"last_price"):
            print("剩余资金：" + str(account.available))
            print("商品现价：%s"%(quote.last_price))

            #确定最新价
            now = quote.last_price

            #确定趋势
            if status == 0:         #看空持仓
                if now < low:               #继续下跌时
                    low = now
                elif now > low + plan.maxnum or now > last + plan.maxloss:          #趋势相反或超过买入点时时反手
                    target.set_target_volume(plan.volume)
                    last = now

            else:                   #看多持仓
                if now > high:              #继续上涨时
                    high = now
                elif now < high - plan.maxnum or now < last - plan.maxloss: #趋势相反或超过买入点时时反手
                    target.set_target_volume(-plan.volume)
                    last = now

    # 关闭api,释放资源
    plan.api.close() 

def main():

    # api = TqApi(TqAccount("G光大期货", "65851579", ""), auth=TqAuth("wzh5728", "Wu1980125"))
    # api = TqApi(account = TqKq(),auth=TqAuth("wzh17796365728", "1980125"))
    api = TqApi(account = TqKq(), auth=TqAuth("wzh5728", "Wu1980125"))

    #api  品种名   看多/看空    价差   交易数量   交易最小单位  存储路径
    # planA = plan(api, "CZCE.PF303", 0, 12, 10, 2, 'trade_log_PF.txt') #短纤
    planB = plan(api, "CZCE.RM305", 1, 5, 10, 1, 'trade_log.txt') #菜粕
    # plan = plan(api, "DCE.cs2303", 1, 5, 10, 1, 'trade_log_cs.txt') #淀粉

    #api  品种名  交易数量   偏离最大值  亏损接受值  存储路径
    planC = wzhplan(api, "CZCE.PF303", 100, 10, 6, 'trade_log_PF_wzh.txt')

    waitMarketopen(1)
    # gridTrade(planB)
    wzhTrade(planC)

    # 为每个合约创建异步任务
    # api.create_task(gridTrade(planB))
    # api.create_task(wzhTrade(planC))

    # while True:
    #     api.wait_update()
    print('主线程完成了')
    

if __name__ == "__main__": #py文件直接运行时执行，当被当做模块时不执行
    main()

# rm.to_csv('code.txt')
# os.system('code.txt')


