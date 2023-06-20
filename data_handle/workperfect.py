import os
import re
import logging
import pandas as pd
import numpy as np
from xml.dom.minidom import parse
import xml.dom.minidom
logging.basicConfig(level = logging.INFO)
tableout = []
tablein  = []
sqlfrom  = []
ktr      = []
outflag = 0
sqlflag = 0
count = 0
tempinput = []
def readfilename(path):     #获取ktr文件
    L=[]
    for root,dirs,files in os.walk(path):
        if root == path:
            for i in files:
                if os.path.splitext(i)[1] == '.ktr':
                    L.append(i)
    return L
    
def findtable(data):
    global tempinput
    st = re.compile('from\s*?[a-zA-Z\[].*?[\s)]', flags=re.IGNORECASE)
    st2 = re.compile('from\s*?[a-zA-Z\[].*', flags = re.IGNORECASE)
    result = st.findall(data)
    if result == []:
        result = st2.findall(data)
    logging.debug(result)
    if result == []:
        return -1
    for i in result:
        temp = re.sub('from|[\n\r\t\s)]', '', i, flags=re.IGNORECASE)
        if temp not in tempinput:
            tempinput.append(temp)
            tablein.append(temp)
            ktr.append(ktr[-1])
            sqlfrom.append(sqlfrom[-1])
            tableout.append(tableout[-1])
    return 0

def findinputtable(hops, steps, fromname):      #寻找所有输入表
    global outflag
    global sqlflag
    global tempinput
    for step in steps:
        if fromname == step.getElementsByTagName('name')[0].firstChild.data:
            type = step.getElementsByTagName('type')[0].firstChild.data
            if (type == 'TableInput'): #| (type == 'ExecSQL'):
                logging.debug('\nin:\n')
                tempinput = []
                if sqlflag == 1:
                    sqlfrom.pop()
                connection = step.getElementsByTagName('connection')[0].firstChild.data
                sqlfrom.append(connection)
                sql = step.getElementsByTagName('sql')[0].firstChild.data
                if findtable(sql) == -1:
                    return -1
                logging.debug(connection)
                sqlflag = 1
                break
            else:
                for hop in hops:
                    toname = hop.getElementsByTagName('to')[0].firstChild.data
                    fromname1 = hop.getElementsByTagName('from')[0].firstChild.data
                    if toname == fromname:
                        logging.debug("nexthop:" + fromname1)
                        if findinputtable(hops, steps, fromname1) == -1:
                            return -1
                break
    return 0

def handledata(path, L):
    for name in L:
        #name = L[16]
        global outflag
        global sqlflag
        outflag = 0
        sqlflag = 0
        status = 0
        ktr.append(name)
        handlepath = path + '\\' + name
        logging.info(handlepath)
        DOMTree = xml.dom.minidom.parse(handlepath)
        collection = DOMTree.documentElement
        hops = collection.getElementsByTagName('hop')
        steps = collection.getElementsByTagName('step')
        for hop in hops:                                #  遍历order
            toname = hop.getElementsByTagName('to')[0].firstChild.data
            fromname = hop.getElementsByTagName('from')[0].firstChild.data
            for step in steps:
                if toname == step.getElementsByTagName('name')[0].firstChild.data:
                    type = step.getElementsByTagName('type')[0].firstChild.data
                    if type == 'TableOutput':
                        logging.debug('\nout:\n')
                        logging.debug(toname)
                        if outflag == 1:
                            tableout.pop()
                        table = step.getElementsByTagName('table')[0].firstChild.data
                        tableout.append(table)      #表输出
                        logging.debug("outputtable:" + table)
                        status = findinputtable(hops, steps, fromname)  #寻找所有输入表
                        if status == -1:       #错误处理
                            print(len(tablein))
                            print(len(tableout))
                            print(len(ktr))
                            print(len(sqlfrom))
                            logging.error("该文件错误，已跳过，请手动更新！" + handlepath)
                            break
                        outflag = 1
                        break
            if status == -1:
                status = 0
                break
        ktr.pop()
        tableout.pop()
        sqlfrom.pop()
        data = {'ktr':ktr, '表输出':tableout,  '来源数据库':sqlfrom, '表输入':tablein}
        try:
            data = pd.DataFrame(data)
        except Exception as e:
            logging.error("error: 文件格式错误!")
            print(e)
def outputtocsv(path):
    data = {'ktr':ktr, '表输出':tableout,  '来源数据库':sqlfrom, '表输入':tablein}
    data = pd.DataFrame(data)
    #data.T
    data.to_csv(path, encoding = 'gbk')
    os.system(path)

def main():
    logging.debug(os.getcwd())
    path = os.getcwd() + '\\20220407'
    resultpath = 'output.csv'
    L = readfilename(path)
    handledata(path, L)
    outputtocsv(resultpath)
    logging.debug(ktr)
    logging.debug(tableout)
    logging.debug(tablein)
    logging.debug(sqlfrom)
    input()
if __name__ == '__main__':
    main()