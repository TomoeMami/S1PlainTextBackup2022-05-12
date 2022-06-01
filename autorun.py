# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import time
import sys
import io
import os
import json

old_number = 2071000+int((int(time.time())-1653881297)/86400)*175

def parse_html(html,threadict):
    # soup = BeautifulSoup(html,from_encoding="utf-8",features="lxml")
    soup = BeautifulSoup(html, 'html.parser')
    namelist = soup.find_all(name="tbody")
    for i in namelist:
        threadids = re.search(r'normalthread_\d{7}',str(i))
        if (threadids):
            levels = re.search(r'\d{1,5}</a></span>',str(i))
            threadid = re.sub(r'normalthread_','',str(threadids.group(0)))
            if levels:
                #在这里进行是否添加的检查
                if(int(threadid) > old_number):
                    level = re.sub(r'</a></span>','',str(levels.group(0)))
                    lastreplytime = re.findall(r'\d{4}-\d{1,2}-\d{1,2} \d{2}:\d{2}',str(i))
                    replytime = time.mktime(time.strptime(str(lastreplytime[1]), "%Y-%m-%d %H:%M"))
                    if(int(level) > 2) and ((int(time.time()) - replytime )< 1209600):
                        threadict[threadid] = replytime
    # replylist = soup.find_all(name='div', attrs={"class":"pcb"})
    # # next_page = soup.find('a', attrs={'class': 'nxt'})
    # # if next_page:
    # #     return soupname, souptime, next_page['herf']
    # title = soup.find_all(name='span',attrs={"id":"thread_subject"})
    # total_page = int((re.findall(r'<span title="共 (\d+) 页">', str(soup)) + [1])[0])
    # titles = re.sub(r'<.+?>','',str(title))
    # titles = re.sub(r'[\]\[]','',titles)
    # titles = re.sub(r'\|','｜',titles)
    # titles = re.sub(r'/','／',titles)
    # titles = re.sub(r'\\','＼',titles)
    # titles = re.sub(r':','：',titles)
    # titles = re.sub(r'\*','＊',titles)
    # titles = re.sub(r'\?','？',titles)
    # titles = re.sub(r'"','＂',titles)
    # titles = re.sub(r'<','＜',titles)
    # titles = re.sub(r'>','＞',titles)
    # titles = re.sub(r'\.\.\.','…',titles)
    # titles = '['+titles+']'
    # return namelist,replylist,total_page,titles
if __name__ == '__main__':
    blacklist = [2056385]
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码
    # # 浏览器登录后得到的cookie，也就是刚才复制的字符串
    with open ('/home/ubuntu/s1cookie-1.txt','r',encoding='utf-8') as f:
        cookie_str1 = f.read()
    #cookie_str1 = os.getenv('S1_COOKIE')
    cookie_str = repr(cookie_str1)[1:-1]
    # #把cookie字符串处理成字典，以便接下来使用
    cookies = {}
    for line in cookie_str.split(';'):
        key, value = line.split('=', 1)
        cookies[key] = value
    # 设置请求头
    headers = {'User-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
    forumdict = {'外野': '75','虚拟主播区专楼':'151','游戏区':'4','漫区':'6','手游专楼':'135'}
    # forumdict = {'外野': '75','游戏区':'4','漫区':'6'}
    rootdir = "./"
    session = requests.session()
    for k in forumdict.keys():
        threadict = {}
        for i in range(1,3):
            RURL = 'https://bbs.saraba1st.com/2b/forum-'+forumdict[k]+'-'+str(i)+'.html'
            s1 = session.get(RURL, headers=headers,  cookies=cookies)
            # s1 = requests.get(RURL, headers=headers)
            # s1.encoding='utf-8'
            data = s1.content
            parse_html(data,threadict)
        with open(rootdir+'RefreshingData.json',"r",encoding='utf-8') as f:
            thdata = json.load(f)
        ids = thdata.keys()
        for l in threadict.keys():
            if (int(l) not in blacklist):
                if l in ids:
                    thdata[l]['active'] = True
                else:
                    if(int(l) > old_number):
                        thdata[l] = {}
                        thdata[l]['totalreply'] =0
                        thdata[l]['title'] = "待更新"
                        thdata[l]['newtitle'] = "待更新"
                        thdata[l]['lastedit'] = int(threadict[l])
                        thdata[l]['category']= k
                        thdata[l]["active"] =  True
                        print('add:'+l)
        with open(rootdir+'RefreshingData.json',"w",encoding='utf-8') as f:
                f.write(json.dumps(thdata,indent=2,ensure_ascii=False))
    activethdata={}
    with open(rootdir+'RefreshingData.json',"r",encoding='utf-8') as f:
            thdata=json.load(f)
    for i in thdata.keys():
        if(thdata[i]['active']) or ((int(time.time()) -thdata[i]['lastedit']) < 1209600) or (int(i) > old_number):
            activethdata[i] = thdata[i]
    with open(rootdir+'RefreshingData.json',"w",encoding='utf-8') as f:
            f.write(json.dumps(activethdata,indent=2,ensure_ascii=False))
