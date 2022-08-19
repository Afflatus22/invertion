
# -*- coding : UTF-8-*-
import datetime
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from query_data import *
import time
import _thread as thread

#定义父类
class Page:
    def __init__(self):
        self.root
        self.wid
        self.hei
        self.can
        self.time
        
    def get_img(self):
        self.impath = '1.jpg'
        self.btnpath = 'btn.png'
        self.err = 1
        self.btnerr = 1
        try:
            img = Image.open(self.impath).resize((self.wid,self.hei))
            self.im = ImageTk.PhotoImage(img)
        except FileNotFoundError as e:
            # print('请在文件目录添加1.jpg的背景图片!')
            self.err = 0
        try:
            btn = Image.open(self.btnpath)
            self.btn = ImageTk.PhotoImage(btn)
        except FileNotFoundError as e:
            # print('请在文件目录添加btn.png的背景图片!')
            self.btnerr = 0
       
    def gettime(self):
        time = datetime.datetime
        endtime = time.today().strftime('%Y%m%d')
        self.time = endtime

    def setbg(self):
        #设置背景图片
        if self.err == 1:
            print("yep")
            self.can = Canvas(self.root, width = self.wid, height = self.hei, bg='white')
            self.can.create_image(self.wid/2,self.hei/2,image = self.im)    #图片中心点位置
            self.can.grid()

'''
--------------------------------------
定义查询类界面
--------------------------------------
'''
class CheckPage(Page):
    def __init__(self, root, width, height):
        self.gettime()
        self.th1 = 1
        self.treelist = []
        self.root = root
        self.hei = height
        self.wid = width
        self.frm = ''
        self.text = StringVar()
        self.input = StringVar()
        self.get_img()
        self.setbg()
        style = ttk.Style()
        style.configure("A.TLabel", relief=FLAT, foreground='red',anchor='center', font=('幼圆', 13),background= '#FDE6E0')
        style.configure("B.TLabel", relief=FLAT, foreground='black',anchor='center', font=('幼圆', 13),background= '#19CAAD')
        style.configure("C.TLabel", width=15, relief=FLAT, foreground='red',anchor='center', font=('幼圆', 15),background= 'black')
        style.configure("D.TLabel", relief=FLAT, foreground='pink',anchor='center', font=('幼圆', 13),background= 'white')
        self.creat()

    def creat(self):
        print("check page!")
        #定义组件
        self.text.set('请输入股票代码:')
        self.frm = ttk.Frame(self.root,style='BW.TLabel', padding = (0, 0, 0, 0), width = self.wid, height = 20, borderwidth=0)
        self.frm.place(x = 0, y = 0)

        self.title = ttk.Label(self.frm, style = 'A.TLabel', textvariable=self.text)
        self.input = ttk.Entry(self.frm, style = 'D.TLabel', width = 15, textvariable=self.input)
        self.btn1 = ttk.Button(self.frm, style = 'B.TLabel', text="添加", cursor = 'hand2',width = 8, command = self.GetStockInfo)
        self.btn2 = ttk.Button(self.frm, style = 'B.TLabel', text="返回", cursor = 'hand2', width = 8, command = self.returnmain)
        self.btn3 = ttk.Button(self.frm, style = 'B.TLabel', text="隐藏", cursor = 'hand2', width = 8, command = self.minisize)

        # self.VScroll = ttk.Scrollbar(self.frm, orient='vertical', command=self.listBox.yview)  # 创建滚动条
        # self.listBox.configure(yscrollcommand=self.VScroll.set)  # 滚动条与表格控件关联
        # self.VScroll.grid(row=1, column=5, sticky=NS)  # 滚动条放置位置
        colwid = 70
        self.frm1 = ttk.Frame(self.root,style='BW.TLabel', padding = (0, 0, 0, 0), width = self.wid, height = self.hei, borderwidth=0)
        self.frm1.place(x = 0, y = 22)
        columns = ('1', '2', '3')
        self.tree = ttk.Treeview(self.frm1, style='C.TLabel', height=10,show='headings', selectmode = BROWSE, columns=columns)  # 创建表格
        self.tree.heading("1", text = "Code")
        self.tree.heading("2", text = "Name")
        self.tree.heading("3", text = "Price")
        self.tree.column("1", anchor = "center", width=colwid)
        self.tree.column("2", anchor = "center", width=colwid)
        self.tree.column("3", anchor = "center", width=colwid)
        self.tree.bind('<ButtonRelease-1>',self.goToTop)
        self.tree.bind('<ButtonRelease-3>',self.goToBottom)
        if self.th1 == 1:
            thread.start_new_thread(self.freshStock, ())
            self.th1 = 0

        self.title.grid(column=0, row=0)
        self.input.grid(column=1, row=0)
        self.btn1.grid(column=2, row=0)
        self.btn2.grid(column=3, row=0)
        self.btn3.grid(column=4, row=0)
        
        self.input.focus()

    def goToTop(self,e):
        self.tree.tag_configure("select" ,foreground='purple',background='white')
        self.tree.item(self.tree.focus(), tags='select')
        if self.tree.focus() != '':
            itm = self.tree.set(self.tree.focus()) 
            self.tree.move(self.tree.focus(),'', 0)
            MoveTopOrRoot(str(itm["1"]),1)

    def goToBottom(self,e):
        self.tree.focus()
        itm = self.tree.set(self.tree.focus()) 
        self.tree.move(self.tree.focus(),'', "end")
        MoveTopOrRoot(str(itm["1"]),0)

    def minisize(self):
        nums = getnums()
        hei = 45+nums*22
        self.root.geometry(f'400x{hei}+0+900')
        self.root.resizable(TRUE,TRUE)

    def freshStock(self):
        print('start')
        while 1:
            setflash(1, 1)
            time.sleep(0.5)
            flash = getflash()
            global show
            if self.th1 == 1:
                show.clear()
                lock.release()
                break
            if flash == 0:
                # print('刷新屏幕中')
                for i in self.tree.get_children():
                    self.tree.delete(i)
                # print(show)
                for i in show:
                    self.tree.insert('', 0, values=i)
                self.tree.grid(column=0,row=0)
                show.clear()
                lock.release()
                # print('刷新屏幕完成:' + str(datetime.datetime.now()))
            else:
                print('出现错误')
                lock.release()
            time.sleep(1.5)

    def GetStockInfo(self):
        GetOnedata(self.input.get())

    def returnmain(self):
        self.th1 = 1
        time.sleep(0.7)
        try:
            self.frm.destroy()
            self.frm1.destroy()
        except AttributeError as e:
            print(e)
        if self.err == 1:
            self.can.destroy()
        MainPage(self.root, self.wid, self.hei)

'''
--------------------------------------
定义选股类界面
--------------------------------------
'''

class ChoosePage(Page):
    def __init__(self, root, width, height):
        self.root = root
        self.hei = height
        self.wid = width
        self.frm = ''
        self.text = StringVar()
        self.input = StringVar()
        self.get_img()
        self.setbg()
        style = ttk.Style()
        style.configure("B.TLabel", relief=FLAT, foreground='black',anchor='center', font=('幼圆', 13),background= '#19CAAD')
        self.creat()

    def creat(self):
        print("check page!")
        #定义组件
        self.text.set('请勾选需要的指标:')
        self.frm = ttk.Frame(self.root,style='B.TLabel', padding = (0, 0, 0, 0), width = self.wid, height = self.hei, borderwidth=0)
        self.frm.place(x = 0, y = 0)
        self.macd = IntVar()
        self.kdj = IntVar()
        ttk.Label(self.frm, style = 'B.TLabel', textvariable = self.text).grid(column=0, row=0)
        ttk.Checkbutton(self.frm, text = "MACD金叉", variable = self.macd, onvalue = 1, offvalue = 0).grid(column=0, row=1)
        ttk.Checkbutton(self.frm, text = "KDJ金叉", variable = self.kdj, onvalue = 1, offvalue = 0).grid(column=1, row=1)
        ttk.Button(self.frm, style = 'B.TLabel', width = 12, text = "开始选股", command=self.PickStock).grid(column=0, row=2)
        ttk.Button(self.frm, style = 'B.TLabel', text="返回", width= 12, command=self.returnmain).grid(column=1,row=2)
        self.tree = ttk.Treeview(self.frm, height=15, columns=2)  # 创建表格
        # self.VScroll = ttk.Scrollbar(self.frm, orient='vertical', command=self.listBox.yview)  # 创建滚动条
        # self.listBox.configure(yscrollcommand=self.VScroll.set)  # 滚动条与表格控件关联
        # self.VScroll.grid(row=1, column=5, sticky=NS)  # 滚动条放置位置
    
    def PickStock(self):
        # self.tree
        print("pick!")

    def returnmain(self):
        self.frm.destroy()
        if self.err == 1:
            self.can.destroy()
        MainPage(self.root, self.wid, self.hei)

'''
--------------------------------------
定义惊喜类界面
--------------------------------------
'''

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

'''
--------------------------------------
定义主页类界面
--------------------------------------
'''

class MainPage(Page):

    def __init__(self, root, width, height):
        self.hei = height
        self.wid = width
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
        self.root.configure(bg='#BEEDC7')
        self.creat()

    def creat(self):
        self.get_img()
        self.setbg()
        #定义组件
        self.text.set('欢迎来到股票小助手!')
        style = ttk.Style()
        style.configure("BW.TLabel", foreground = '#D1BA74',font=('楷体', 30, 'bold'),background= '#BEEDC7')
        style.configure("A.TLabel",activebackground='yellow',activeforeground='blue', relief=FLAT , foreground='red',anchor='center', font=('幼圆', 20),background= '#19CAAD')
        # print(self.frm.configure().keys())
        # print(ttk.Style().configure().keys())
        #设置框架
        self.frm = ttk.Frame(self.root,style='BW.TLabel', padding = (0, 0, 0, 0), width = self.wid, height = self.hei, borderwidth=0)
        self.frm.place(x = 150, y = 100)

        #设置控件
        self.title = ttk.Label(self.frm,style = 'BW.TLabel',anchor='center',textvariable=self.text)
        self.blank1 = ttk.Label(self.frm,style = 'BW.TLabel',anchor='center')
        self.blank2 = ttk.Label(self.frm,style = 'BW.TLabel',anchor='center')
        self.checkbut = ttk.Button(self.frm, style = 'A.TLabel', text="盯盘精灵", cursor = 'hand2',width = 16, command = self.gotocheck)
        self.blank3 = ttk.Label(self.frm,style = 'BW.TLabel',anchor='center')
        self.choosebut = ttk.Button(self.frm,style = 'A.TLabel', text="量化选股", cursor = 'hand2', width = 16, command = self.gotochoose)

        #控件布局
        self.title.grid(column=0, row=0)
        self.blank1.grid(column=0, row=1)
        self.blank2.grid(column=0, row=2)
        self.checkbut.grid(column=0, row=3)
        self.blank3.grid(column=0,row=4)
        self.choosebut.grid(column=0, row=5)
        # self.checkbut.configure(relief='flat',activebackground='yellow')
    def gotocheck(self):
        print("check!")
        self.frm.destroy()
        if self.err == 1:
            self.can.destroy()
        CheckPage(self.root, self.wid, self.hei)

    def gotochoose(self):
        print("choose!")
        self.frm.destroy()
        if self.err == 1:
            self.can.destroy()
        ChoosePage(self.root, self.wid, self.hei)
        # surprisePage(self.root)
        