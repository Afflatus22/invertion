
# -*- coding : UTF-8-*-
from msilib.schema import Font
import tushare as ts
import pandas as pd
import datetime
import os
import time
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk

#定义父类
class Page:
    def __init__(self):
        self.root
        self.wid
        self.hei
        self.can

    def get_img(self):
        print('get img ok')
        img = Image.open(self.impath).resize((self.wid,self.hei))
        self.im = ImageTk.PhotoImage(img)

    def setbg(self):
        print("set bg in")
        #设置背景图片
        err = 1
        try:
            self.get_img()
        except FileNotFoundError as e:
            print('请在文件目录添加1.jpg的背景图片!')
            err = 0
        finally:
            if err == 1:
                print("yep")
                self.can = Canvas(self.root, width = self.wid, height = self.hei, bg='white')
                self.can.create_image(self.wid/2,self.hei/2,image = self.im)    #图片中心点位置
                self.can.grid()

class CheckPage(Page):
    def __init__(self, root, width, height):
        self.root = root
        self.hei = height
        self.wid = width
        self.impath = '1.jpg'
        self.frm = ''
        self.text = StringVar()
        self.input = StringVar()
        self.setbg()
        self.creat()

    def creat(self):
        print("check page!")
        #定义组件
        self.text.set('请输入股票代码或名称!')
        self.frm = ttk.Frame(self.root, padding = (0, 0, 0, 0), width = self.wid, height = self.hei, borderwidth=2)
        self.frm.place(x = 0, y = 0)
        ttk.Label(self.frm, textvariable = self.text,background= 'yellow').grid(column=0, row=0)
        ttk.Entry(self.frm, width = 15, textvariable=self.input).grid(column=1, row=0)
        ttk.Button(self.frm, width = 12, text = "搜索", command=self.GetStockInfo).grid(column=2, row=0)
        ttk.Button(self.frm, text="返回", width= 12, command=self.returnmain).grid(column=3,row=0)

    def GetStockInfo(self):
        self.data = 0

    def returnmain(self):
        self.frm.destroy()
        self.can.destroy()
        MainPage(self.root, self.wid, self.hei)

class surprisePage(Page):
    def __init__(self, root):
        self.root = root
        self.hei = 600
        self.wid = 450
        self.root.geometry('450x600')
        self.impath = '2.jpg'
        self.frm = ''
        self.setbg()
        self.creat()

    def creat(self):
        #定义组件
        self.can.image = self.im
        self.frm = ttk.Frame(self.root, padding = (0, 0, 0, 0), width = self.wid, height = self.hei, borderwidth=2)
        self.frm.place(x = 0, y = 0)
        ttk.Label(self.frm, font=('宋体', 20, 'italic'), text = 'I SAY I LOVE YOU FOREVER!',background= '#FDE6E0').grid(column=1, row=0)
        
class MainPage(Page):

    def __init__(self, root, width, height):
        self.hei = height
        self.wid = width
        self.impath = '1.jpg'
        self.frm = ''
        self.im = ''
        self.text = StringVar()
        screen_width = root.winfo_screenwidth() / 2 - width / 2
        screen_height = root.winfo_screenheight() / 2 - height / 2
        self.root = root
        # root.iconbitmap('1.jpg')
        self.root.geometry(f'{width}x{height}+{int(screen_width)}+{int(screen_height)}')
        self.root.resizable(FALSE, FALSE)
        self.root.title('analyse stock')
        self.root.configure(bg='#fff2e2')
        self.creat()

    def creat(self):
        self.setbg()
        #定义组件
        self.text.set('欢迎来到股票小助手!')
        self.frm = ttk.Frame(self.root, padding = (0, 0, 0, 0), width = self.wid, height = self.hei, borderwidth=2)
        print(self.frm.configure().keys())
        self.frm.place(x = 0, y = 0)
        print(ttk.Label().configure().keys())
        ttk.Label(self.frm, textvariable = self.text,background= 'yellow').grid(column=0, row=0)
        ttk.Button(self.frm, text="查询个股", width = 12, command = self.gotocheck).grid(column=0, row=1)
        ttk.Button(self.frm, text="点我有惊喜!", width = 12, command = self.gotochoose).grid(column=0, row=2)
    
    def gotocheck(self):
        print("check!")
        self.frm.destroy()
        self.can.destroy()
        CheckPage(self.root, self.wid, self.hei)

    def gotochoose(self):
        print("choose!")
        self.frm.destroy()
        self.can.destroy()
        surprisePage(self.root)
        