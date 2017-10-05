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


blacklist = ['やおい', 'BL', '腐', '腐向け', # yaoi
            '漫画', 'マンガ'] # manga
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
    res = requests.get(api_url,data=payload, headers=headers, stream=True)
    t = 0
    while res.status_code != 200 and t<5:
        res = requests.get(api_url,data=payload, headers=headers, stream=True)
        t+=1
    if len(res.content) >= 100 or t == 5:
        return True
    else:
        global file, find
        url = prefix+str(pixivId)
        file.write('<A HREF="' + url + '"> ' + url + '<br/>')
        find += 1
        return False

def AddEntry(index, score):
    global pixiv_dic
    try:
        json = illust_detail(index, req_auth=True)
        if 'illust' in json:
            json = json.illust
            if json.total_bookmarks > score and json.page_count < 10:
                new_dic = {}
                new_dic['t'] = [tag.name for tag in json.tags]
                new_dic['u'] = json.image_urls.medium
                new_dic['n'] = json.page_count
                new_dic['d'] = json.create_date
                new_dic['s'] = json.total_bookmarks
                new_dic['r'] = json.height/json.width
                pixiv_dic[index] = new_dic
        elif 'error' in json and 'ID' not in json.error.user_message:
            print(json.error)
    except Exception as e:
        global find
        find += 1
        print(e)
        pass

def PixivNotDanbooru(mode = 0, data = None):
    print('-------------------------------')
    print('---- BEGIN CHECKING ON DAN ----')
    global find, file, pixiv_dic, illust_detail, result
    p, find = 0.0, 0
    if mode == 0:
        score = int(input('Minimum score? '))
        ran = input('Range? ').split()
        index = []
        for ele in ran:
            x,y = ele.split(':')
            index += list(range(int(x), int(y)))
        pixiv_dic = {}
    elif mode == 1:
        file = open('NotDanbooru_Result.html', 'w')
        data.sort()
        pixiv_dic = data
        index = data
    limit = len(index)
    limit_active = int(input('Number of threads ? '))+threading.active_count()
    try:
        begin = datetime.now()
        print('Begin at', begin.strftime('%H:%M'))
        lastLogin = begin
        for i, x in enumerate(index):
            while threading.active_count() > limit_active:
                time.sleep(0.1)
            if mode == 0 and ((datetime.now()-lastLogin).seconds > 3590 or i == 0):
                if i == 0:
                    api = AppPixivAPI()
                    illust_detail = api.illust_detail
                    api.login(pixiv_mail, pixiv_code)
                else:
                    api.login(pixiv_mail, pixiv_code)
                    lastLogin = datetime.now()
            if mode == 0:
                Thread(target=AddEntry, args=(x, score)).start()
            elif mode == 1:
                Thread(target=CheckOnDan, args=(data[i],)).start()

            if p != int(i/limit*1000)/10:
                ending = ((datetime.now() - begin)/(i+1)*limit + begin).strftime('%H:%M')
                print(str(p)+'%', '|', ending, '|', find, len(pixiv_dic), '|', x)
                p = int(i/limit*1000)/10
        time.sleep(10)
    except Exception as e:
        print(e)
        print('Stop at', i)
    finally:
        if not mode and pixiv_dic:
            name = 'pixiv/'+str((index[0])//1000000)+'.json'
            with open(name, 'w') as file:
                json.dump(pixiv_dic, file, sort_keys=True, indent=4)
        print('FOUND:', find)
        file.close()
        print('---- CHECKING ON DAN OK ----')
        

def ReadJSON(files):
    print('----------------------------')
    print('---- BEGIN JSON READING ----')
    r = input("score range ? ")
    if ':' in r:
        scm, scM = r.split(':')
    else:
        scm, scM = 0, 9999999
    score = [int(scm), int(scM), input('tags? ')]
    data = []
    scm, scM, tags = score
    for file in files:
        print("read :",file)
        with open('pixiv/'+file+'.json', 'r') as file:
            temp = json.load(file)
            for i, v in temp.items():
                blacklisted = False
                long = False
                if (v['s'] > scm and v['s'] < scM )\
                and (str(i) in v['u'] or 'r18' in v['u'] or 'r18' in v['t']):
                    if 'r' in v and v['r']>2.5:
                        long = True
                    for tag in blacklist:
                        if tag in v['t']:
                            blacklisted = True
                    if long or blacklisted:
                        continue
                    if tags:
                        for tag in tags.split():
                            if tag in v['t']:
                                data.append(int(i))
                                break
                    else:
                        data.append(i)
    print('---- JSON READING OK ----')
    if input(str(len(data))+' images found. Check on Dan ? (y/n) ') == 'y':
        PixivNotDanbooru(mode = 1, data = data)
        if input('Continue to extract urls ? (y/n) :')=='y':
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
        name = 'pixiv/' + str(key)+'.json'
        with open(name, 'w') as file:
            json.dump(value, file, sort_keys=True, indent=4)
        print('Done on', key)



def getUrl(i):
    try:
        res1 = illust_detail(i, req_auth=True)
        res2 = [dic.image_urls.original for dic in res1.illust.meta_pages]
        if not res2:
            res2 = [res1.illust.meta_single_page.original_image_url]
        pixiv_dic[i] = res2
    except Exception as e:
        print('IndividualUrl - error on :', i, e)
   
def getUrls(index, limit_active):
    print('-----------------------')
    print('---- BEGIN GET URL ----')
    global find, file, pixiv_dic, illust_detail, result
    pixiv_dic = {}
    p = 0.0
    try:
        begin = datetime.now()
        print('Begin at', begin.strftime('%H:%M'))
        lastLogin = begin
        for i, x in enumerate(index):
            while threading.active_count() > limit_active:
                time.sleep(0.1)
            if (datetime.now()-lastLogin).seconds > 3590 or i == 0:
                if i == 0:
                    api = AppPixivAPI()
                    illust_detail = api.illust_detail
                    api.login(pixiv_mail, pixiv_code)
                else:
                    api.login(pixiv_mail, pixiv_code)
                    lastLogin = datetime.now()
            Thread(target=getUrl, args=(x,)).start()
            if p != int(i/len(index)*100)/1:
                ending = ((datetime.now() - begin)/(i+1)*len(index) + begin).strftime('%H:%M')
                print(str(p)+'%', '|', ending)
                p = int(i/len(index)*100)/1
        time.sleep(10)
    except Exception as e:
        print("getUrls",e)
    file = open('no_result.html', 'w')
    res = []
    for value in pixiv_dic.values():
        for url in value:
            if 'limit' in url or 'r18' in url or 'R18' in url:
                url = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id=" + str(i)
                file.write('<A HREF="' + url + '"> ' + url + '<br/>')
            else:
                res.append(url)
    res.sort()
    print(len(res), 'results')
    print('---- GET URL OK ----')
    return res

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
    
def getImg(url):
    imgs.append(Sample(url))

def getImgs(urls, limit_active):
    print('-----------------------')
    print('---- BEGIN GET PIC ----')
    global imgs
    imgs = []
    p = 0.0
    ini = threading.active_count()
    try:
        begin = datetime.now()
        print('Begin at', begin.strftime('%H:%M'))
        for i, x in enumerate(urls):
            now = datetime.now()
            while threading.active_count() > limit_active:
                time.sleep(0.1)
                if (datetime.now()-now).seconds > 60:
                    break
            if (datetime.now()-now).seconds > 60:
                break
            Thread(target=getImg, args=(x,)).start()
            if p != int(i/len(urls)*1000)/10:
                ending = ((datetime.now() - begin)/(i+1)*len(urls) + begin).strftime('%H:%M')
                print(str(p)+'%', '|', ending)
                p = int(i/len(urls)*1000)/10
        while threading.active_count() > ini:
            if (datetime.now()-now).seconds > 60:
                break
            time.sleep(1)

    except Exception as e:
        print('getImgs',e)
    print(len(imgs), 'results')
    print('---- GET PIC OK ----')
    return imgs
        
def ShowImgs(imgs):
    input('Press a key to begin')
    file = open('result.html', 'w')
    begin = datetime.now()
    print('-----------------------')
    print('--- BEGIN SHOW IMGS ---')
    print('Begin at', begin.strftime('%H:%M'), len(imgs))
    i, l = 0, len(imgs)
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
        print(i, '/', l, '|', ending, '|', img._url.split('/')[-1])
    print('--- SHOW IMGS OK ---')
    
def ShowPixiv():
    limit_active = int(input('Number of threads ? '))+threading.active_count()
    tor = input('Use tor ? (y/n) : ') == 'y'
    if tor:
        from TOR.tor import renew_tor
        renew_tor()
        index = Index()
        urls = getUrls(index, limit_active)
        file = open('tor_result.html', 'w')
        for url in urls:
            file.write(url)
    else:
        if input('import url from file ? (y/n) : ') == 'y':
            urls = open('tor_result.html', 'r').readline().split('https')
            urls = ['https'+url for url in urls]
        else:
            index = Index()
            urls = getUrls(index, limit_active)
        imgs = getImgs(urls, limit_active)
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
        if input('Use tor ? (y/n) : ') == 'y':
            from TOR.tor import renew_tor
            renew_tor()
        PixivNotDanbooru(mode = 0)
    elif mode == 1:
        ReadJSON(files)
    elif mode == 2:
        SplitJSON(files)
    elif mode == 3:
        ShowPixiv()