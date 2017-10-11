# -*- coding: utf-8 -*-
"""
    Author: Rignak
    Python version: 3.5
"""
from datetime import datetime
from threading import Thread
import threading
import time
import requests
import json
from pixivpy3 import AppPixivAPI
from io import BytesIO
from PIL import Image
from os import system
import urllib
from lib.progress import Progress
import io

with io.open("blacklist.txt",'r',encoding='utf8') as f:
    blacklist = []
    for line in f:
        blacklist.append(line[:-1])

with open("../Danbooru_Codes.txt", 'r') as f:
    api_key = f.readline().split()[1]
    dan_username = f.readline().split()[1]
with open("../Pixiv_Codes.txt", 'r') as f:
    pixiv_mail = f.readline().split()[1]
    pixiv_code = f.readline().split()[1]

headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
api_url = 'http://danbooru.donmai.us/posts.json'
prefix = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='

class Sample:
    """Depict a sample with:
    - the Id of the image on danbooru (an str(int))
    - the data of the image (BytesIO(urllib.request.urlopen))
    - the tags corresponding to the image (a str)"""

    def __init__(self, url):
        ok = False
        self._url = url
        self._adds = ''
        while not ok:
            try:
                req = urllib.request.Request(url)
                req.add_header('Referer', 'https://www.pixiv.net/')
                self._data = BytesIO(urllib.request.urlopen(req).read())
                ok = True
            except Exception as e:
                print("Sample init - error on", self._url, e)
                break

    def InputTags(self):
        """Display a sample, and ask an input to add tags"""
        try:
            temp_img = Image.open(self._data)
            temp_img.show()
        except:
            return 'pass'
        while self._adds == '':
            self._adds = input('tags ? ')
        system("taskkill /f /im dllhost.exe")
        return self._adds

def CheckOnDan(pixivId):
    payload = {'limit': '1',
               'tags':'pixiv:'+str(pixivId),
               'api_key':api_key,
               'login':dan_username}
    req = requests.get(api_url,data=payload, headers=headers, stream=True)
    t = 0
    while res.status_code != 200 and t<5:
        req = requests.get(api_url,data=payload, headers=headers, stream=True)
        t+=1
    if len(req.content) >= 100 or t == 5:
        return True
    else:
        global file
        url = prefix+str(pixivId)
        req.append(pixivId)
        file.write('<A HREF="' + url + '"> ' + url + '<br/>')
        return False

def AddEntry(index):
    try:
        json = illust_detail(index, req_auth=True)
        if 'illust' in json:
            json = json.illust
            if json.total_bookmarks > score and json.page_count < 10:
                new_dic = {}
                new_dic['t'] = [tag.name for tag in json.tags] + [str(json.user.id)]
                #new_dic['u'] = json.image_urls.medium
                new_dic['n'] = json.page_count
                #new_dic['d'] = json.create_date
                new_dic['s'] = json.total_bookmarks
                new_dic['r'] = json.height/json.width
                global res
                res[index] = new_dic
        elif 'error' in json and 'ID' not in json.error.user_message:
            print(json.error)
    except Exception as e:
        print(e)
        print()

def Routeur(mode = 0, data = None):
    global file, res, illust_detail
    index = data
    res = []
    if mode == 0:
        global score
        score = int(input('Minimum score? '))
        ran = input('Range? ').split()
        index = []
        for ele in ran:
            x,y = ele.split(':')
            index += list(range(int(x), int(y)))
        res = {}
    elif mode == 1:
        file = open('NotDanbooru_Result.html', 'w')
        data.sort()
    elif mode == 3:
        res = {}
    limit = len(index)
    limit_active = int(input('Number of threads ? '))+threading.active_count()
    function = [AddEntry, CheckOnDan, getImg, getUrl][mode]
    try:
        begin = datetime.now()
        p = 0.0
        print('Begin at', begin.strftime('%H:%M'))
        lastLogin = begin
        for i, x in enumerate(index):
            while threading.active_count() > limit_active:
                time.sleep(0.1)
            if mode in [0,3] and ((datetime.now()-lastLogin).seconds > 3590 or i == 0):
                if i == 0:
                    api = AppPixivAPI()
                    illust_detail = api.illust_detail
                    api.login(pixiv_mail, pixiv_code)
                else:
                    api.login(pixiv_mail, pixiv_code)
                    lastLogin = datetime.now()
            Thread(target=function, args=(x, )).start()
            if p != int(i/limit*10000)/100:
                ending = ((datetime.now() - begin)/(i+1)*limit + begin).strftime('%D-%H:%M')
                Progress(str(p)+'% | '+ending)
                p = int(i/limit*10000)/100
        time.sleep(10)
    except Exception as e:
        print(e)
        print('Stop at', i)
    finally:
        print()
        print('FOUND:', len(res))
        if mode in [0, 1]:
            if not mode and res:
                name = 'pixiv/temp'+str((index[0])//1000000)+'.json'
                with open(name, 'w') as file:
                    json.dump(res, file, sort_keys=True, indent=4)
            file.close()
        elif mode == 3:
            res = []
            for value in res.values():
                for url in value:
                    res.append(url)
            res.sort()
            return res
        elif mode ==2:
            return res

def ReadJSON(files):
    print('----------------------------')
    print('---- BEGIN JSON READING ----')
    r = input("score range ? ")
    if ':' in r: scm, scM = r.split(':')
    else: scm, scM = 0, 9999999
    score = [int(scm), int(scM), input('tags? ')]
    tag_f = input('Enforce tags? : ').split()
    data = []
    scm, scM, tags = score
    nb = {key:0 for key in tags.split()}
    for j,file in enumerate(files):
        Progress("read : "+str(j)+'/'+str(len(files)))
        with open('pixiv/'+file+'.json', 'r') as file:
            temp = json.load(file)
            for i, v in temp.items():
                if (v['s'] > scm and v['s'] < scM ) \
                and (not any(tag in v['t'] for tag in blacklist))\
                and (not tag_f or any(tag in v['t'] for tag in tag_f))\
                and (not tags or any(tag in v['t'] for tag in tags.split())):
                    data.append(int(i))
                    for tag in set(tags.split()).intersection(set(v['t'])):
                        nb[tag]+=1
    print()
    for key, value in nb.items():
        print(key, ':', value)
    print('---- JSON READING OK ----')
    if input(str(len(data))+' images found. Check on Dan ? (y/n) ') == 'y':
        Routeur(mode = 1, data = data)
        if input('Continue to extract urls ? (y/n) : ')=='y':
            ShowPixiv()

def SplitJSON(files):
    l = 1000000
    data = {}
    dic = {}
    for file in files:
        with open('pixiv/'+file+'.json', 'r') as file:
            data.update(json.load(file))
    for key, value in data.items():
        if int(key)//l not in dic.keys():
            dic[int(key)//l] = {}
        dic[int(key)//l][key] = value
    for key, value in dic.items():
        name = 'pixiv/temp' + str(key)+'.json'
        with open(name, 'w') as file:
            json.dump(value, file, sort_keys=True, indent=4)
        Progress('Done on '+key)

def getUrl(i):
    try:
        res1 = illust_detail(i, req_auth=True)
        if 'illust' in res1:
            res2 = [dic.image_urls.original for dic in res1.illust.meta_pages]
            if not res2:
                res2 = [res1.illust.meta_single_page.original_image_url]
            res[i] = res2
    except Exception as e:
        print('IndividualUrl - error on :', i, e)

def getImg(url):
    res.append(Sample(url))

def Index():
    file = open('NotDanbooru_Result.html', 'r')
    r = input('Range ? ')
    if ':' in r:
        begin, end = r.split(':')
        line = file.readline().split('<br/>')
        index = [int(ele.split('=')[-1]) for ele in line[:-1]]
        return index[index.index(int(begin)):index.index(int(end))]
    else:
        line = file.readline().split('<br/>')
        return [int(ele.split('=')[-1]) for ele in line[:-1]]

def ShowImgs(imgs):
    input('Press a key to begin')
    begin = datetime.now()
    print('-----------------------')
    print('--- BEGIN SHOW IMGS ---')
    print('Begin at', begin.strftime('%H:%M'), len(imgs))
    i, l = 0, len(imgs)
    file = open('final.html', 'w')
    while imgs:
        img = imgs[0]
        imgs = imgs[1:]
        img.InputTags()
        if img._adds == 'y':
            file.write('<A HREF="' + img._url + '"> ' + img._url + '<br/>')
        elif img._adds == 'exit':
            break
        i+=1
        ending = ((datetime.now() - begin)/i*l+ begin).strftime('%H:%M')
        s = str(i)+'/'+str(l)+' | '+ending+' | ' + img._url.split('/')[-1]
        Progress(s)
    print()
    print('--- SHOW IMGS OK ---')

def ShowPixiv():
    n = int(input('Proxy number ? '))
    if n:
        from lib.tor import SetProxy
        SetProxy(n)
        urls = Routeur(mode=3, data=Index())
        file = open('directlink.html', 'w')
        for url in urls:
            file.write(url)
    else:
        if input('import url from file ? (y/n) : ') == 'y':
            urls = open('directlink.html', 'r').readline().split('https')
            urls = ['https'+url for url in urls]
        else:
            urls = Routeur(mode=3, data=Index())
        imgs = Routeur(mode=2, data=urls[1:])
        ShowImgs(imgs)

if __name__ == '__main__':
    print('mode 0 : go to pixiv and write a .json')
    print('mode 1 : read .json and check on dan')
    print('mode 2 : split .json')
    print('mode 3 : show images')
    mode = int(input('Which mode ? '))
    if mode in [1, 2]:
        files = input('File numbers ? ')
        if ':' in files:
            r = files.split(':')
            files = [str(x) for x in list(range(int(r[0]), int(r[1])))]
        else:
            files = files.split()
    if mode == 0:
        n = int(input('Proxy number ? '))
        if n:
            from lib.tor import SetProxy
            SetProxy(n)
        Routeur(mode = 0)
    elif mode == 1: ReadJSON(files)
    elif mode == 2: SplitJSON(files)
    elif mode == 3: ShowPixiv()