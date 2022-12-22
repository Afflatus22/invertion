import requests
import sys
import os
import numpy as np
import efinance as ef
import time
from tqsdk import TqApi, TqAuth, TqAccount, TqKq

class plan():
    def __init__(self, api, obj, dir, delta, num):
        self.have = 0
        self.last = 0
        self.now = 0
        self.order = ''
        self.api = api
        self.obj = obj
        self.dir = dir
        self.delta = delta
        self.num = num
    def buyit(self):
        if self.dir == 0:
            self.order = self.api.insert_order(symbol= self.obj, direction="BUY", offset="CLOSETODAY", limit_price= self.now+1, volume=self.num)
        elif self.dir == 1:
            self.order = self.api.insert_order(symbol= self.obj, direction="BUY", offset="OPEN", limit_price= self.now+1, volume=self.num)
    def sellit(self):
        if self.dir == 0:
            self.order = self.api.insert_order(symbol= self.obj, direction="SELL", offset="OPEN", limit_price= self.now-1, volume=self.num)
        elif self.dir == 1:
            self.order = self.api.insert_order(symbol= self.obj, direction="SELL", offset="CLOSETODAY", limit_price= self.now-1, volume=self.num)

# DCE
# 大连商品交易所
# CZCE
# 郑州商品交易所
def waitMarketopen():
    while True:
        timenow = time.strftime('%H%M%S', time.localtime(time.time()))
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
        f.write(data)
        f.close()
    else:
        f = open(path, 'r', encoding='utf-8')
        items = f.readlines()
        for i in items:
            print(i)
            price = int(i)
        f.close()
    return price
        

def main():
    waitMarketopen()
    path = 'trade_log.txt'
    obj = "CZCE.RM305" # CZCE.RM305
    dir = 1     #0看空  1看多
    delta = 5  #价差
    num = 5

    if os.access(path, os.F_OK) == 0:
        f = open(path, 'w', encoding='utf-8')
        f.close()
    haveit = 0
    sellorbuy = 0
    # api = TqApi(TqAccount("G光大期货", "65851579", ""), auth=TqAuth("wzh5728", "Wu1980125"))
    # api = TqApi(account = TqKq(),auth=TqAuth("wzh17796365728", "1980125"))
    api = TqApi(account = TqKq(), auth=TqAuth("wzh5728", "Wu1980125"))
    planA = plan(api, obj, dir, delta, num)

    account = api.get_account()     #获取账户信息
    # quote = api.get_quote("CZCE.RM305") #菜粕合约
    quote = planA.api.get_quote(planA.obj) #淀粉合约
    lev = planA.api.get_position(planA.obj)    #获取持仓情况
    
    print(lev)
    # print("\n")
    # print(account)

    #确定是否有持仓
    if planA.dir == 1:
        if lev == {} or lev.volume_long == 0:
            planA.order = planA.api.insert_order(symbol=planA.obj, direction="BUY", offset="OPEN", limit_price = quote.last_price+1, volume=200)
            sellorbuy = 2
        else:
            planA.last = lev.open_price_long
            planA.have = lev.volume_long
            planA.order = lev
            haveit = 1
    else:
        if lev == {} or lev.volume_short == 0:
            if planA.dir == 0:
                planA.order = planA.api.insert_order(symbol=planA.obj, direction="SELL", offset="OPEN", limit_price = quote.last_price+1, volume=200)
            sellorbuy = 2
        else:
            planA.last = lev.open_price_short
            planA.have = lev.volume_short
            planA.order = lev
            haveit = 1
    

    while True:
        try:
            planA.api.wait_update()
            print("剩余资金：" + str(account.available))
            print("商品现价：%s"%(quote.last_price))
            # print(planA.order)
            #确定当前价
            planA.now = quote.last_price

            #确定过去成交价
            if haveit == 0:
                while True:
                    if planA.order.status == "FINISHED":
                        break
                    planA.api.wait_update()
                    print("价格：%s,单状态: %s, 已成交: %d 手, 盈亏：%f" % (planA.order.limit_price,planA.order.status, planA.order.volume_orign - planA.order.volume_left, lev.float_profit))
                    time.sleep(1)
                print("价格：%s,单状态: %s, 已成交: %d 手, 盈亏：%f" % (planA.order.limit_price,planA.order.status, planA.order.volume_orign - planA.order.volume_left, lev.float_profit))
                if planA.order.volume_orign - planA.order.volume_left != 0 :
                    planA.last = planA.order.limit_price
                    logPrice(path, planA.last, 1)
            elif planA.dir == 1:
                print("价格：%s, 盈亏：%f" % (planA.order.position_price_long, planA.order.float_profit))
                planA.last = logPrice(path, planA.last, 0)
            elif planA.dir == 0:
                print("价格：%s, 盈亏：%f" % (planA.order.position_price_short, planA.order.float_profit))
                planA.last = logPrice(path, planA.last, 0)

            #确定持仓量
            if planA.dir == 1:
                if sellorbuy == 2:
                    planA.have = planA.have + planA.order.volume_orign - planA.order.volume_left
                    sellorbuy = 0
                elif sellorbuy == 1:
                    planA.have = planA.have - planA.order.volume_orign + planA.order.volume_left
                    sellorbuy = 0
            else:
                if sellorbuy == 1:
                    planA.have = planA.have + planA.order.volume_orign - planA.order.volume_left
                    sellorbuy = 0
                elif sellorbuy == 2:
                    planA.have = planA.have - planA.order.volume_orign + planA.order.volume_left
                    sellorbuy = 0
            
            print("now:%s,have:%s,last:%s"%(planA.now, planA.have, planA.last))

            if planA.now > planA.last + planA.delta:
                sellorbuy = 1
                print("sell it!")
                planA.sellit()
                haveit = 0
            elif planA.now < planA.last - planA.delta:
                sellorbuy = 2
                print("buy it!")
                planA.buyit()
                haveit = 0
            print("\n")
            time.sleep(2)
        except:
            print("运行出错！！！")
    # 关闭api,释放资源
    planA.api.close()

if __name__ == "__main__": #py文件直接运行时执行，当被当做模块时不执行
    main()

# rm.to_csv('code.txt')
# os.system('code.txt')


