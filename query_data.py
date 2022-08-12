import tushare as ts
import pandas as pd
import datetime
import os
import time
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk

global text
global input

def get_img(file,width,height):
    print(height)
    print(width)
    img = Image.open(file).resize((width,height))
    image = ImageTk.PhotoImage(img)
    return image

def GetTusharedataToCsv(pro, endtime, path):
    df = pro.daily(**{"ts_code": "","trade_date": endtime,"start_date": 20220101,"end_date": endtime,"offset": "","limit": ""}, fields=["ts_code","close"])
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
    
    data.to_csv(path, encoding = 'gbk')

def searchStock():
    global text
    global input
    print(input.get())
    # time.sleep(5)
    text.set('you are good!')
    print('good')

def openapp(width, height):
    global text
    global input
    #创建主窗口实例
    root = Tk()
    # 计算中心坐标点
    screen_width = root.winfo_screenwidth() / 2 - width / 2
    screen_height = root.winfo_screenheight() / 2 - height / 2
    root.geometry(f'{width}x{height}+{int(screen_width)}+{int(screen_height)}')
    root.resizable(FALSE, FALSE)
    root.title('analyse stock')
    # root.iconbitmap('1.jpg')

    #设置背景图片
    err = 0
    try:
        im = get_img('./1.jpg', width, height)
    except FileNotFoundError as e:
        print('请在文件目录添加1.jpg的背景图片!')
        err = 1
    finally:
        if err == 0:
            can = Canvas(root, width = width, height = height, bg='white')
            can.create_image(width/2,height/2,image = im)    #图片中心点位置
            can.grid()

    #定义组件
    text = StringVar()
    input = StringVar()
    text.set('welcome to stock market analyse tool!')
    frm = ttk.Frame(root, padding = (0, 0, 0, 0), width = width, height = height)
    print(frm.configure().keys())
    frm.place(x = 0, y = 0)
    # print(ttk.Label().configure().keys())
    ttk.Label(frm, textvariable = text,background= 'yellow').grid(column=0, row=0)
    ttk.Entry(frm, background = 'white', textvariable=input).grid(column = 0, row = 2)
    ttk.Button(frm, text="搜索", command = searchStock).grid(column=0, row=1)
    root.mainloop()

def main():
    #设置窗口大小
    width = 700
    height = 500
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
    openapp(width, height)
    #GetTusharedataToCsv(pro, endtime, path)
    print('股票量化分析结束')
    #os.system(path)
    
if __name__ == '__main__':
    main()
    