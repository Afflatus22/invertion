# -*- coding : UTF-8-*-
import datetime
from tkinter import *
from tkinter import ttk
from main_page import *
from query_data import *

def appinit():
    GetItemsFromFile()

def openapp(width, height):
    #创建主窗口实例
    root = Tk()
    MainPage(root, width, height)
    root.mainloop()

def main():
    #设置窗口大小
    width = 700
    height = 500
    #保存文件路径
    path = 'output.csv'
    #获取当前日期
    endtime = datetime.datetime.today().strftime('%Y%m%d')
    print('股票量化分析开始 当前时间：'+ endtime)
    appinit()
    thread.start_new_thread(slave, ())
    openapp(width, height)
    print('股票量化分析结束')
    #os.system(path)
    
if __name__ == '__main__':
    main()
    