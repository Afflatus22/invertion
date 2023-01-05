import requests
import sys
import os
import json
import numpy as np
import efinance as ef
from datetime import datetime
import time
import threading
from tqsdk import TqApi, TqAuth, TqAccount, TqKq, TargetPosTask
from tqsdk.ta import ATR, MA

class plan():
    def __init__(self, api, obj, dir, delta, num, step, cash, path):
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
        self.cash = cash
    def buyit(self, vol = 0):
        if vol == 0:
            vol = self.num
        if self.dir == 0:
            self.order = self.api.insert_order(symbol= self.obj, direction="BUY", offset="CLOSETODAY", limit_price= self.now+self.step, volume=vol)
        elif self.dir == 1:
            self.order = self.api.insert_order(symbol= self.obj, direction="BUY", offset="OPEN", limit_price= self.now+self.step, volume=vol)
    def sellit(self, vol = 0):
        if vol == 0:
            vol = self.num
        if self.dir == 0:
            self.order = self.api.insert_order(symbol= self.obj, direction="SELL", offset="OPEN", limit_price= self.now-self.step, volume=vol)
        elif self.dir == 1:
            self.order = self.api.insert_order(symbol= self.obj, direction="SELL", offset="CLOSETODAY", limit_price= self.now-self.step, volume=vol)

class wzhplan():
    def __init__(self, api, obj, volume, maxnum, maxloss, path):
        self.api = api
        self.obj = obj
        self.volume = volume
        self.maxnum = maxnum
        self.maxloss = maxloss
        self.path = path

# https://oapi.dingtalk.com/robot/send?access_token=db46b7ef6f95fb96b1bc814254d4a3ffaf9b1f6e585aacd9351783ed4764da09
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
            break
        if int(timenow) > 103005 and int(timenow) < 113000:
            break
        if int(timenow) > 133005 and int(timenow) < 150000:
            break
        if int(timenow) > 210005 and int(timenow) < 230000:
            break
        time.sleep(5)
    if show:
        print("begin!")

def send_msg(content):
    """钉钉消息提醒模块"""
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=db46b7ef6f95fb96b1bc814254d4a3ffaf9b1f6e585aacd9351783ed4764da09"

    # 钉钉安全规则将 天勤量化 设为关键字
    msg = {"msgtype": "text",
           "text": {"content": "{}\n{}\n".format("量化\n" + content,
                                                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}, }
    headers = {"content-type": "application/json;charset=utf-8"}
    body = json.dumps(msg)
    requests.post(webhook, data=body, headers=headers)

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

def logJson(path, rw, data={}):
    if rw == 1:
        a = json.dumps(data)
        f = open(path, 'a', encoding='utf-8')
        f.write(a)
        f.write('\n')
        f.close()
    else:
        f = open(path, 'r', encoding='utf-8')
        items = f.readlines()
        if items == '':
            return {}
        a = json.loads(items[-1])
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
    
    print("品种：%s,空头持仓： %d,多头持仓：%d"%(plan.obj, lev.pos_short, lev.pos_long))
    print("\n")
    print("可用资金：%f,浮动盈亏:%f"%(account.available, account.float_profit))

    #确定是否有持仓
    if plan.dir == 1:
        if lev == {} or lev.volume_long == 0:
            plan.order = plan.api.insert_order(symbol=plan.obj, direction="BUY", offset="OPEN", limit_price = quote.last_price+plan.step, volume=100)
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
        
        if plan.api.is_changing(quote, "last_price"):
            print("剩余资金：" + str(account.available))
            print("商品现价：%s"%(quote.last_price))
            print("now:%s,have:%s,last:%s"%(plan.now, plan.have, plan.last))

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
    high = quote.last_price
    low = quote.last_price
    if lev.pos_short > lev.pos_long:
        status = 0  #此前趋势
        last = lev.position_price_short #上次成交价格
    else:
        status = 1
        last = lev.position_price_long #上次成交价格
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
            print("持仓价格：%s, low:%s, high: %s,status:%d" %(last, low, high, status))
            print("剩余资金：" + str(account.available))
            print("商品现价：%s\n"%(quote.last_price))

            #确定最新价
            now = quote.last_price

            #确定趋势
            if status == 0:         #看空持仓
                if now < low:               #继续下跌时
                    low = now
                elif now > low + plan.maxnum or now > last + plan.maxloss:          #趋势相反或超过买入点时时反手
                    target.set_target_volume(plan.volume)
                    last = now
                    low = now
                    status = 1
                    print("空 -> 多")
            else:                   #看多持仓
                if now > high:              #继续上涨时
                    high = now
                elif now < high - plan.maxnum or now < last - plan.maxloss: #趋势相反或超过买入点时时反手
                    target.set_target_volume(-plan.volume)
                    last = now
                    high = now
                    status = 0
                    print("多 -> 空")
        time.sleep(2)
    # 关闭api,释放资源
    plan.api.close() 

def recordPrice(code , n, inprice, out, nums):
    logs = {
        "code": code,
        "N": n,
        "in_price": inprice,
        "out_price": out,
        "nums": nums,
    }
    return logs

#海龟交易法则  可选参考K线，20日均线入场，10日均线止盈，参考ATR指标为N
def turtleTrade(plan, times, cash):
    # logJson(plan.path, 1, recordPrice(plan.obj,42,2947, 2871, 10))
    if os.access(plan.path, os.F_OK) == 0:
        f = open(plan.path, 'w', encoding='utf-8')
        f.close()
    # logJson(plan.path, 1, logs)
    logs = logJson(plan.path, 0)
    print(logs)

    #计算指标参数   
    quote =   plan.api.get_quote(plan.obj) #淀粉合约
    lev =   plan.api.get_position(plan.obj)    #获取持仓情况
    klines = plan.api.get_kline_serial(plan.obj, times)
    target = TargetPosTask(plan.api, plan.obj)

    atr = ATR(klines, 20).atr.tolist()[-1]
    ma20 = MA(klines, 20).ma.tolist()[-1]
    ma10 = MA(klines, 10).ma.tolist()[-1]
    plan.num = int(cash/(100*atr*10*plan.step))
    have = lev.pos_long-lev.pos_short
    print("品种：%s, N:%d, IN:%d, OUT:%d, 交易量:%d, 持仓：%d"%(plan.obj, atr, ma20, ma10, plan.num, have))
    if have != 0:
        N = logs["N"]
        in_price = logs["in_price"]
        out_price = logs["out_price"]
        print("当前情况: N:%d, IN:%d, OUT:%d, have:%d"%(N, in_price, out_price, have))
    
    #当前趋势状态
    if quote.last_price > ma20:
        plan.dir = 0
    else:
        plan.dir = 1

    while True:
        plan.api.wait_update()
        waitMarketopen(0)
        if plan.api.is_changing(klines.iloc[-1], "datetime"): #更新指标参数
            atr = ATR(klines, 20).atr.tolist()[-1]
            ma20 = MA(klines, 20).ma.tolist()[-1]
            ma10 = MA(klines, 10).ma.tolist()[-1]
            plan.num = cash/(100*atr*10*plan.step)
            print("Parameter  update!ATR:%d,MA20:%d,MA10:%d,NUM:%d"%(atr, ma20, ma10, plan.num))

        if plan.api.is_changing(quote,"last_price"):
            plan.now = quote.last_price
            print(plan.now)
            if have > 0:    #多头持仓
                plan.dir = 1
                if have == 4*plan.num:
                    out_price = ma10
                if plan.now >= in_price + N/2 + plan.step and have < 4*plan.num:  #加仓操作
                    print("%s 多头加仓：%d,%d" %(plan.obj ,plan.now, plan.num))
                    send_msg("%s 多头加仓：%d,%d" %(plan.obj, plan.now, plan.num))
                    plan.buyit()
                    in_price = plan.now
                    out_price = out_price + N/2
                    have += plan.num
                    if have == 4*plan.num:
                        out_price = ma10
                    logJson(plan.path, 1, recordPrice(plan.obj, N, in_price, out_price, have))
                elif plan.now <= out_price + plan.step:     #到止损位或止盈位
                    print("%s 虽然很不情愿，止损清仓:%d"%(plan.obj, plan.now))
                    send_msg("%s 虽然很不情愿，止损清仓:%d"%(plan.obj, plan.now))
                    plan.sellit(have)
                    have = 0
                    plan.dir = 0
                    logJson(plan.path, 1, recordPrice(plan.obj, N, in_price, out_price, 0))
            elif have < 0:  #空头持仓
                plan.dir = 0
                if have == 4*plan.num:
                    out_price = ma10
                if plan.now <= in_price - N/2 + plan.step and have < 4*plan.num:  #加仓操作
                    print("%s 空头加仓：%d,%d" %(plan.obj, plan.now, plan.num))
                    send_msg("%s 空头加仓：%d,%d" %(plan.obj, plan.now, plan.num))
                    plan.sellit()
                    in_price = plan.now
                    out_price = out_price + N/2
                    have += plan.num
                    if have == 4*plan.num:
                        out_price = ma10
                    logJson(plan.path, 1, recordPrice(plan.obj, N, in_price, out_price, have))
                elif plan.now >= out_price + plan.step:     #到止损位或止盈位
                    print("%s 虽然很不情愿，止损清仓:%d"%(plan.obj, plan.now))
                    send_msg("%s 虽然很不情愿，止损清仓:%d"%(plan.obj, plan.now))
                    plan.buyit(have)
                    have = 0
                    plan.dir = 1
                    logJson(plan.path, 1, recordPrice(plan.obj, N, in_price, out_price, 0))
            else:
                if plan.dir == 0:
                    if plan.now <= ma20 + plan.step:
                        plan.sellit()
                        N = ATR(klines, 20).atr.tolist()[-1]
                        in_price = plan.now
                        out_price = plan.now - 2*N
                        have = plan.num
                        logJson(plan.path, 1, recordPrice(plan.obj, N, in_price, out_price, have))
                elif plan.dir == 1:
                    if plan.now >= ma20 - plan.step:
                        plan.buyit()
                        N = ATR(klines, 20).atr.tolist()[-1]
                        in_price = plan.now
                        out_price = plan.now - 2*N
                        have = plan.num
                        logJson(plan.path, 1, recordPrice(plan.obj, N, in_price, out_price, have)) 

#双均线策略
def doubleMaTrade(plan):
    print("double begin!")

def main():

    # api = TqApi(TqAccount("G光大期货", "65851579", ""), auth=TqAuth("wzh5728", "Wu1980125"))
    # api = TqApi(TqAccount("Z中信期货", "121615398", "1624362377"), auth=TqAuth("wzh5728", "Wu1980125"))
    # api = TqApi(account = TqKq(),auth=TqAuth("wzh17796365728", "1980125"))
    with TqApi(account = TqKq(), auth=TqAuth("wzh5728", "Wu1980125")) as api:

        #api  品种名   看多/看空    价差   交易数量   交易最小单位  资金量  存储路径
        planA = plan(api, "CZCE.PF303", 0, 12, 10, 2, 50000, 'trade_log_PF.txt') #短纤
        planB = plan(api, "CZCE.RM305", 1, 5, 10, 1, 50000, 'trade_log.txt') #菜粕
        planD = plan(api, "CZCE.MA305", 1, 5, 10, 1, 50000, 'trade_log_MA.txt') #甲醇
        plancs = plan(api, "DCE.cs2303", 1, 5, 10, 1, 50000, 'trade_log_cs_turtle.json') #淀粉

        #api  品种名  交易数量   偏离最大值  亏损接受值  存储路径
        planC = wzhplan(api, "CZCE.PF303", 100, 12, 6, 'trade_log_PF_wzh.txt')

        # account =  api.get_account()     #获取账户信息
        # print(account)
        waitMarketopen(1)
        # gridTrade(planA)
        # wzhTrade(planC)
        turtleTrade(plancs, 24*60*60, 500000)

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


