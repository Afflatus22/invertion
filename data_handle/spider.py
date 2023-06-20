#coding = uft-8
from email.header import Header
import types
import requests
import lxml
import sys
import time
if(sys.version[:1] == "3"):
    import _thread as thread
else:
    import thread 
from bs4 import BeautifulSoup as bb

def client(threadName, delay):
    count = 0
    while count < 10:
        time.sleep(delay)
        count += 1
        print("%s, %s" %(threadName, time.ctime(time.time())))

def getspider(web):
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
    web = "https://" + web
    print("抓取的网址是：" + web)
    req = requests.get(web, headers= header)
    print('获取网址状态：' + str(req))
    print('获取到的网址内容')
    print(req.content)
    bsobj = bb(req.content, 'lxml')
    a_list = bsobj.find_all('a')
    text = ''
    for a in a_list:
        href = a.get('href')
        if href is not None:
            text += href + '\n'
    print('获取到的网址链接：' + '\n' + text)

def host(delay, web):
    time.sleep(delay)
    web = "https://" + web
    print("抓取的网址是：" + web)
    req = requests.get(web)
    print('获取网址状态：' + str(req))
    print('获取到的网址内容')
    print(req.content)
    with open('content.txt', 'wb') as f1:
            f1.write(req.content)

    bsobj = bb(req.content, 'lxml')
    a_list = bsobj.find_all('a')
    text = ''
    for a in a_list:
        href = a.get('href')
        text += href + '\n'
    with open('url.txt', 'w') as f:
        f.write(text)
    print('获取到的网址链接：' + '\n' + text)
    print(time.ctime(time.time()))
def main():
    print("请输入需要抓取的网址:(例如www.xxx.com)")
    web = input()
    thread.start_new_thread(client, ("client", 1, ))
    thread.start_new_thread(host, (1,web, ))
    time.sleep(30)

if __name__ == '__main__':
    main()