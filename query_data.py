import tushare as ts
import pandas as pd
import datetime
import os

def GetTusharedataToCsv(pro, endtime, path):
    df = pro.daily(**{"ts_code": "","trade_date": endtime,"start_date": 20220101,"end_date": endtime,"offset": "","limit": ""}, fields=["ts_code","close"])
    df = pro.stock_basic(market = '主板')
    print(df)
    #data = df[['name', 'ts_code']]
    data = {'股票名称':df['name'], '股票代码':df['ts_code']}
    data = pd.DataFrame(data)
    #print(data)
    for i in data['股票名称']:          #剔除ST股票
        if 'ST' in i:
            data = data.drop(index = (data.loc[i == data['股票名称']].index))
    print(data)
    north = pro.hk_hold('trade_date' == '20220412')
    north = north.loc[north['exchange'] == ('SH' or 'SZ')] 
    north = north.loc[ north['ratio'] >= 3.0]
    print(north)
    data.to_csv(path, encoding = 'gbk')

def main():
    #保存文件路径
    path = 'output.csv'
    #初始化ts参数
    ts.set_token('df8ba8bf0035f774d5d15c760a7bdf864bd22c45887e9fc7097769f4')
    pro = ts.pro_api()
    #获取当前日期
    time = datetime.datetime
    endtime = time.today().strftime('%Y%m%d')
    print('股票量化分析开始 当前时间：'+ endtime)

    #df = pro.daily(ts_code = '002349.SZ', start_date='20220113', end_date='20220331')
    #df = ts.pro_bar(trade_date= '20220401', start_date='20210131', end_date= endtime, ma=[50])  获取单个股票信息
    GetTusharedataToCsv(pro, endtime, path)
    print('股票量化分析结束')
    #os.system(path)
    
if __name__ == '__main__':
    main()