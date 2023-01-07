# --coding: utf-8 --
from ast import Return
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from query_data import *
from spider import *

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
        # try:
        #     btn = Image.open(self.btnpath)
        #     self.btn = ImageTk.PhotoImage(btn)
        # except FileNotFoundError as e:
        #     # print('请在文件目录添加btn.png的背景图片!')
        #     self.btnerr = 0
       
    def gettime(self):
        time = datetime.datetime
        endtime = time.today().strftime('%Y%m%d')
        self.time = endtime

    def setbg(self):
        #设置背景图片
        if self.err == 1:
            self.can = Canvas(self.root, width = self.wid, height = self.hei, bg='white')
            self.can.create_image(self.wid/2,self.hei/2,image = self.im)    #图片中心点位置
            self.can.grid(column=0,row=0)

    def getwinsize(self, root):
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
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
        self.im = ''
        self.root = root
        self.hei = height
        self.wid = width
        self.frm = ''
        self.mini = 0
        self.text = StringVar()
        self.inputtext = StringVar()
        self.getwinsize(self.root)
        style = ttk.Style()
        style.configure("A.TLabel", relief=FLAT, foreground='red',anchor='center', font=('幼圆', 13),background= '#FDE6E0')
        style.configure("B.TLabel", relief=FLAT, foreground='black',anchor='center', font=('幼圆', 13),background= '#19CAAD')
        style.configure("C.TLabel", width=15, relief=FLAT, foreground='red',anchor='center', font=('幼圆', 15),background= 'black')
        style.configure("D.TLabel", relief=FLAT, foreground='pink',anchor='center', font=('幼圆', 13),background= 'white')
        style.configure("E.TLabel", relief=FLAT, foreground='red', font=('幼圆', 10),background= 'black')
        self.creat()

    def creat(self):
        self.get_img()
        self.setbg()
        #定义组件
        self.text.set('请输入股票代码:')
        self.frm = ttk.Frame(self.root,style='BW.TLabel', padding = (0, 0, 0, 0), width = self.wid, height = 20, borderwidth=0)
        self.frm.place(x = 0, y = 0)

        self.title = ttk.Label(self.frm, style = 'A.TLabel', textvariable=self.text)
        self.input = ttk.Entry(self.frm, style = 'D.TLabel', width = 15, textvariable=self.inputtext)
        self.btn1 = ttk.Button(self.frm, style = 'B.TLabel', text="添加", cursor = 'hand2',width = 8, command = self.GetStockInfo)
        self.btn2 = ttk.Button(self.frm, style = 'B.TLabel', text="返回", cursor = 'hand2', width = 8, command = self.returnmain)
        self.btn3 = ttk.Button(self.frm, style = 'B.TLabel', text="隐藏", cursor = 'hand2', width = 8, command = self.minisize)
        self.help = ttk.Label(self.root, style='E.TLabel', text='左键单击置顶\n右键单击置底\n鼠标滚轮单击删除')

        colwid = 120
        self.frm1 = ttk.Frame(self.root,style='BW.TLabel', padding = (0, 0, 0, 0), width = self.wid, height = self.hei, borderwidth=0)
        self.frm1.place(x = 0, y = 22)
        columns = ('1', '2', '3', '4', '5')
        self.tree = ttk.Treeview(self.frm1, style='C.TLabel', height=10,show='headings', selectmode = BROWSE, columns=columns)  # 创建表格
        self.tree.heading("1", text = "Code")
        self.tree.heading("2", text = "Name")
        self.tree.heading("3", text = "Price")
        self.tree.heading("4", text = "Ratio")
        self.tree.heading("5", text = "Preclose")
        self.tree.column("1", anchor = "center", width=50)
        self.tree.column("2", anchor = "center", width=colwid)
        self.tree.column("3", anchor = "center", width=50)
        self.tree.column("4", anchor = "center", width=40)
        self.tree.column("5", anchor = "center", width=50)
        self.tree.tag_configure("select" ,foreground='purple',background='white')

        self.input.bind('<Return>', self.GetStockInfo)
        self.tree.bind('<ButtonRelease-1>',self.goToTop)
        self.tree.bind('<Button-3>', self.selection)
        self.tree.bind('<Button-2>', self.selection)
        self.tree.bind('<ButtonRelease-2>', self.deleteitem)
        self.tree.bind('<ButtonRelease-3>',self.goToBottom)

        self.title.grid(column=0, row=0)
        self.input.grid(column=1, row=0)
        self.btn1.grid(column=2, row=0)
        self.btn2.grid(column=3, row=0)
        self.btn3.grid(column=4, row=0)
        self.help.place(x=580,y=450)
        
        self.input.focus()
        if self.th1 == 1:
            thread.start_new_thread(self.freshStock, ())
            self.th1 = 0

    def deleteitem(self, e):
        print('delete')
        if self.tree.focus() != '':
            itm = self.tree.set(self.tree.focus()) 
            self.tree.delete(self.tree.focus())
            ItemHandle(str(itm["1"]),2)
            if self.mini == 1:
                self.minisize()

    def selection(self, e):
        print(f'{e.x}, {e.y}')
        self.tree.focus(self.tree.identify('item', e.x, e.y))
        self.tree.item(self.tree.focus(), tags='select')

    def goToTop(self,e):
        self.tree.item(self.tree.focus(), tags='select')
        if self.tree.focus() != '':
            itm = self.tree.set(self.tree.focus()) 
            self.tree.move(self.tree.focus(),'', 0)
            ItemHandle(str(itm["1"]),1)

    def goToBottom(self,e):
        if self.tree.focus() != '':
            itm = self.tree.set(self.tree.focus()) 
            self.tree.move(self.tree.focus(),'', "end")
            ItemHandle(str(itm["1"]),0)

    def minisize(self):
        self.mini = 1
        nums = getnums()
        hei = 45+nums*22
        self.root.geometry(f'400x{hei}+0+{self.screen_height - hei - 100}')
        self.root.resizable(FALSE,FALSE)

    def freshStock(self):
        print('start')
        self.tree.tag_configure("down" ,foreground='#84fa84',background='black')
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
                    i.insert(3, str(round((float(i[2]) - float(i[3]))*100/float(i[3]),2)) + '%')
                    if i[2] < i[4]:
                        self.tree.insert('', 0, values=i, tags='down')
                    else:
                        self.tree.insert('', 0, values=i)
                self.tree.grid(column=0,row=0)
                show.clear()
                lock.release()
                # print('刷新屏幕完成:' + str(datetime.datetime.now()))
            else:
                print('出现错误')
                lock.release()
            time.sleep(1.5)

    def GetStockInfo(self, e = None):
        if self.inputtext.get() != '':
            GetOnedata(self.inputtext.get())
            if self.mini == 1:
                self.minisize()
        self.inputtext.set('')

    def returnmain(self):
        self.th1 = 1
        # time.sleep(0.7)
        try:
            self.frm.destroy()
            self.frm1.destroy()
            self.help.destroy()
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
定义爬虫功能界面
--------------------------------------
'''

class SpiderPage(Page):
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
        style.configure("D.TLabel", relief=FLAT, foreground='pink',anchor='center', font=('幼圆', 13),background= 'white')
        style.configure("B.TLabel", relief=FLAT, foreground='black',anchor='center', font=('幼圆', 13),background= '#19CAAD')
        self.creat()

    def creat(self):
        #定义组件
        self.text.set('请输入要爬的网址:')
        self.frm = ttk.Frame(self.root,style='B.TLabel', padding = (0, 0, 0, 0), width = self.wid, height = self.hei, borderwidth=0)
        self.frm.place(x = 0, y = 0)

        self.lab = ttk.Label(self.frm, style = 'B.TLabel', textvariable = self.text)
        self.entry = ttk.Entry(self.frm, style = 'D.TLabel',width=15, textvariable = self.input)
        self.but = ttk.Button(self.frm, style = 'B.TLabel', width = 8, text = "开始", command=self.startSpider)
        self.but1 = ttk.Button(self.frm, style = 'B.TLabel', text="返回", width= 8, command=self.returnmain)
        self.tree = ttk.Treeview(self.frm, height=15, columns=2)

        self.lab.grid(column=0, row=0)
        self.entry.grid(column=1, row=0)
        self.but.grid(column=2,row=0)
        self.but1.grid(column = 3, row=0)
        
        self.entry.focus()
        self.entry.bind('<Return>', self.startSpider)

    def startSpider(self, e = None):
        print("SPIDER!")
        getspider(str(self.input.get()))

    def checkRatio(self):
        GetDvRatioFromtushare()

    def returnmain(self):
        self.frm.destroy()
        if self.err == 1:
            self.can.destroy()
        MainPage(self.root, self.wid, self.hei)

'''
--------------------------------------
定义展示功能界面
--------------------------------------
'''

class ShowPage(Page):
    def __init__(self, root, width, height):
        self.root = root
        self.hei = height
        self.wid = width
        self.frm = ''
        self.text = StringVar()
        self.text1 = StringVar()
        self.input = StringVar()
        self.get_img()
        self.setbg()
        style = ttk.Style()
        style.configure("D.TLabel", relief=FLAT, foreground='#D1BA74',anchor='center', font=('幼圆', 13),background= 'black')
        style.configure("E.TLabel", relief=FLAT, foreground='white',anchor='center', font=('幼圆', 13),background= 'black')
        style.configure("B.TLabel", relief=RAISED, foreground='black',anchor='center', font=('幼圆', 13),background= 'white')
        self.creat()

    def creat(self):
        #定义组件
        self.text.set('Nothing for now!')
        self.text1.set('显示窗口:')
        self.frm = ttk.Frame(self.root,style='D.TLabel', padding = (0, 0, 0, 0), width = self.wid, height = self.hei/2, borderwidth=1)
        self.frm.place(x = 5, y = 5, bordermode = 'outside', height= 400, width=690)
        self.frm1 = ttk.Frame(self.root,style='E.TLabel', padding = (0, 0, 0, 0), width = self.wid, height = self.hei, borderwidth=5)
        self.frm1.place(x = 5, y = 300, height= 200, width=690)

        self.lab = ttk.Label(self.frm, style = 'D.TLabel', textvariable = self.text1)
        self.lab1 = ttk.Label(self.frm, style = 'E.TLabel', textvariable = self.text)
        self.but = ttk.Button(self.frm1, style = 'B.TLabel', width = 8, padding= 5 , text = "开始", command=self.startSpider)
        self.but2 = ttk.Button(self.frm1, style = 'B.TLabel', width = 8, padding= 5 , text = "结束", command=self.startSpider)
        self.but1 = ttk.Button(self.frm1, style = 'B.TLabel', text="返回", width= 8, padding= 5  , command=self.returnmain)
        self.tree = ttk.Treeview(self.frm1, height=15, columns=2)

        self.lab.grid(column=0, row=0)
        self.lab1.grid(column=1, row=0)
        self.but.grid(column=1,row=0, padx= 10, sticky= 's',pady= 10)
        self.but2.grid(column = 2, row=0, padx= 10, pady= 10)
        self.but1.grid(column = 3, row=0, padx= 10, pady= 10)

    def startSpider(self, e = None):
        print("show!")
        self.text.set('is good')

    def checkRatio(self):
        GetDvRatioFromtushare()

    def returnmain(self):
        self.frm.destroy()
        if self.err == 1:
            self.can.destroy()
        MainPage(self.root, self.wid, self.hei)

'''
--------------------------------------
定义主页类界面
--------------------------------------
'''

class MainPage(Page):

    def __init__(self, root, width, height):
        self.root = root
        self.hei = height
        self.wid = width
        self.frm = ''
        self.im = ''
        self.text = StringVar()
        self.getwinsize(self.root)
        screen_width = (self.screen_width - self.wid)/2
        screen_height = (self.screen_height - self.hei)/2
        root.iconbitmap('icon.ico')
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
        style.configure("A.TLabel",activebackground='yellow',activeforeground='blue', relief=RIDGE , foreground='red',anchor='center', font=('幼圆', 20),background= '#19CAAD')
        # print(self.frm.configure().keys())
        # print(ttk.Style().configure().keys())
        #设置框架
        self.frm = ttk.Frame(self.root,style='BW.TLabel', padding = (0, 0, 0, 0), width = self.wid, height = self.hei, borderwidth=0)
        self.frm.place(x = 150, y = 100)
        self.frm1 = ttk.Frame(self.root,style='BW.TLabel', padding = (0, 0, 0, 0), width = self.wid, height = self.hei, borderwidth=0)
        self.frm1.place(x = 233, y = 230)
        self.frm2 = ttk.Frame(self.root,style='BW.TLabel', padding = (0, 0, 0, 0), width = self.wid, height = self.hei, borderwidth=0)
        self.frm2.place(x = 233, y = 300)
        self.frm3 = ttk.Frame(self.root,style='BW.TLabel', padding = (0, 0, 0, 0), width = self.wid, height = self.hei, borderwidth=0)
        self.frm3.place(x = 233, y = 370)

        #设置控件
        self.title = ttk.Label(self.frm,style = 'BW.TLabel',anchor='center',textvariable=self.text)
        self.checkbut = ttk.Button(self.frm1, style = 'A.TLabel', text="盯盘精灵", cursor = 'hand2',width = 16, command = self.gotocheck)
        # self.blank3 = ttk.Label(self.frm,style = 'BW.TLabel',anchor='center')
        self.choosebut = ttk.Button(self.frm2,style = 'A.TLabel', text="爬虫工具", cursor = 'hand2', width = 16, command = self.gotochoose)
        self.showbut = ttk.Button(self.frm3,style = 'A.TLabel', text="量化交易", cursor = 'hand2', width = 16, command = self.gotoshow)

        #控件布局
        self.title.grid(column=0, row=0)
        self.checkbut.grid(column=0, row=0)
        self.choosebut.grid(column=0, row=0)
        self.showbut.grid(column=0, row=0)
        # self.checkbut.configure(activebackground='yellow')

    def gotocheck(self):
        print("check!")
        self.frm.destroy()
        self.frm1.destroy()
        self.frm2.destroy()
        if self.err == 1:
            self.can.destroy()
        CheckPage(self.root, self.wid, self.hei)

    def gotochoose(self):
        print("choose!")
        self.frm.destroy()
        self.frm1.destroy()
        self.frm2.destroy()
        if self.err == 1:
            self.can.destroy()
        SpiderPage(self.root, self.wid, self.hei)
        # surprisePage(self.root)

    def gotoshow(self):
        print("show!")
        self.frm.destroy()
        self.frm1.destroy()
        self.frm2.destroy()
        if self.err == 1:
            self.can.destroy()
        ShowPage(self.root, self.wid, self.hei)
        