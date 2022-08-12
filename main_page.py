import tushare as ts
import pandas as pd
import datetime
import os
import time
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk

class MainPage():

    def __init__(self, root, width, height):
        self.hei = height
        self.wid = width
        self.impath = '1.jpg'
        self.im = ''
        self.text = StringVar()
        self.input = StringVar()
        screen_width = root.winfo_screenwidth() / 2 - width / 2
        screen_height = root.winfo_screenheight() / 2 - height / 2
        self.root = root
        # root.iconbitmap('1.jpg')
        self.root.geometry(f'{width}x{height}+{int(screen_width)}+{int(screen_height)}')
        self.root.resizable(FALSE, FALSE)
        self.root.title('analyse stock')
        self.root.configure(bg='#fff2e2')
        self.creat()

    def get_img(self):
        img = Image.open(self.impath).resize((self.wid,self.hei))
        self.im = ImageTk.PhotoImage(img)

    def searchStock(self):
        print(self.input.get())
        # time.sleep(5)
        self.text.set('you are good!')
        print('good')

    def creat(self):
        print('good')
        #设置背景图片
        # err = 1
        # try:
        self.get_img()
        # except FileNotFoundError as e:
        #     print('请在文件目录添加1.jpg的背景图片!')
        #     err = 0
        # finally:
        #     if err == 1:
        can = Canvas(self.root, width = self.wid, height = self.hei, bg='white')
        can.create_image(self.wid/2,self.hei/2,image = self.im)    #图片中心点位置
        can.grid()

        #定义组件
        self.text = StringVar()
        self.input = StringVar()
        self.text.set('请输入股票代码:')
        frm = ttk.Frame(self.root, padding = (0, 0, 0, 0), width = self.wid, height = self.hei, borderwidth=2)
        print(frm.configure().keys())
        frm.place(x = 0, y = 0)
        # print(ttk.Label().configure().keys())
        ttk.Label(frm, textvariable = self.text,background= 'yellow').grid(column=0, row=0)
        ttk.Entry(frm, background = 'white', textvariable=input).grid(column = 1, row = 0)
        ttk.Button(frm, text="搜索", width = 8, command = self.searchStock).grid(column=2, row=0)
    