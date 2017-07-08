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
case = True
controller = False
from stem import Signal
from stem.control import Controller
import socks
import socket
def renew_tor():
    """Create a connexion to Tor or renew it if it already exist"""
    global case
    global controller
    if case:
        controller = Controller.from_port(port=9151)
        case = False
    controller.authenticate()
    controller.signal(Signal.NEWNYM)
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1",
                          9150, True)
    socket.socket = socks.socksocket

def PixIsOnDan(pixivId):
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
        global file
        global find
        url = prefix+str(pixivId)
        file.write('<A HREF="' + url + '"> ' + url + '<br/>')
        find += 1
        return False

def IndividualWritePixiv(index, score):
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
    except Exception as e:
        global find
        find += 1
        print(e)
        pass

def IndividualFromDic(i, score):
    global pixiv_dic
    global result
    small_dic = pixiv_dic[i]
    if (small_dic['s'] > score[0] and small_dic['s'] < score[1])\
        and (str(i) in small_dic['u'] or 'r18' in small_dic['u']):
        if 'r' in small_dic and small_dic['r']>2.5:
            return
        for tag in blacklist:
            if tag in small_dic['t']:
                return
        if score[2]:
            for tag in score[2].split():
                if tag in small_dic['t']:
                    if PixIsOnDan(i):
                        result[tag] += 1
                    return
        else:
            PixIsOnDan(i)

def PixivNotDanbooru(mode = 0, data = None):
    global find
    global file
    global pixiv_dic
    score = int(input('Minimum score? '))
    if mode == 0:
        global illust_detail
        last = int(input('Where to begin? '))
        limit = int(input('How many to check? '))
        function = IndividualWritePixiv
        pixiv_dic = {}
        index = range(last-limit,last)
        api = AppPixivAPI()
        illust_detail = api.illust_detail
    elif mode == 1:
        global result
        score = [score, int(input('maximum score? ')), input('tags? ')]
        result = {key:0 for key in score[2].split()}
        file = open('NotDanbooru_Result.html', 'w')
        function = IndividualFromDic
        pixiv_dic = data
        index = list(data.keys())
        index.sort()
        limit = len(index)
    limit_active = int(input('Number of threads ? '))+threading.active_count()
    p, find = 0.0, 0
    #renew_tor()
    try:
        begin = datetime.now()
        lastLogin = begin
        for i, x in enumerate(index):
            while threading.active_count() > limit_active:
                time.sleep(0.5)
            if mode == 0 and ((lastLogin-begin).seconds > 3500 or i == 0):
                api.login(pixiv_mail, pixiv_code)
                lastLogin = datetime.now()
            Thread(target=function, args=(x, score)).start()
            if p != int(i/limit*1000)/10:
                ending = ((datetime.now() - begin)/(i+1)*limit + begin).strftime('%H:%M')
                print(str(p)+'%', '|', ending, '|', find, len(pixiv_dic))
                p = int(i/limit*1000)/10
    except Exception as e:
        print(e)
        print('Stop at', i)
    finally:
        time.sleep(10)
        if not mode:
            name = 'pixiv/'+str((last-limit)//1000000)+'.json'
            with open(name, 'w') as file:
                json.dump(pixiv_dic, file, sort_keys=True, indent=4)
        if mode == 1:
            for key, value in result.items():
                print(key, ':', value)
        print('FOUND:', find)
        print('MEAN TIME:', (datetime.now()-begin)/(i+1))
        file.close()


def ReadJSON(files):
    data = {}
    for file in files:
        with open('pixiv/'+file+'.json', 'r') as file:
            data.update(json.load(file))
    PixivNotDanbooru(mode = 1, data = data)


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


if __name__ == '__main__':
    print('mode 0 : go to pixiv and write a .json')
    print('mode 1 : read .json and check on dan')
    print('mode 2 : split .json')
    mode = int(input('Which mode ? '))
    if mode:
        files = input('File numbers ? ')
        if ':' in files:
            r = files.split(':')
            files = [str(x) for x in list(range(int(r[0]), int(r[1])))]
        else:
            files = files.split()
    if mode == 1:
        ReadJSON(files)
    elif mode == 2:
        SplitJSON(files)
    else:
        PixivNotDanbooru(mode = 0)


# -----------------------
# Next functions not used
#------------------------


def getR18_URL(json_result, index):
    date = json_result['illust']['create_date']
    sample_prefix = 'https://i.pximg.net/c/600x600/img-master/img/'
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    hour = date[11:13]
    minute = date[14:16]
    second = date[17:19]
    add = '/'.join([year, month, day, hour, minute, second])
    url_sample = sample_prefix + add + '/' + str(index) + '_p0_master1200.jpg'
    return url_sample
