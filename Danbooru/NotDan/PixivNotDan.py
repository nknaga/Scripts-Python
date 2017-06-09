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

with open("../Danbooru_Codes.txt", 'r') as f:
    api_key = f.readline().split()[1]
    dan_username = f.readline().split()[1]

headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
api_url = 'http://danbooru.donmai.us/posts.json'
prefix = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='


def PixIsOnDan(pixivId):
    payload = {'limit': '1',
               'tags':'pixiv:'+str(pixivId),
               'api_key':api_key,
               'login':dan_username}
    res = requests.get(api_url,data=payload, headers=headers, stream=True)
    while res.status_code != 200:
        print(res.status_code)
        res = requests.get(api_url,data=payload, headers=headers, stream=True)
    if len(res.content) >= 100:
        return False
    else:
        global file
        global find
        url = prefix+str(pixivId)
        file.write('<A HREF="' + url + '"> ' + url + '<br/>')
        find += 1

def IndividualPixivNotDan(i, score):
    global api
    try:
        json_result = api.illust_detail(i)
        if 'illust' in json_result and \
            json_result['illust']['total_bookmarks'] > score \
            and int(json_result['illust']['page_count']) < 5 \
            and (str(i) in json_result['illust']['image_urls']['medium']\
            or 'r18' in json_result['illust']['image_urls']['medium']) \
            and json_result['illust']['type'] == 'illust':
            PixIsOnDan(i)
    except Exception as e:
        #print(e)
        pass

def IndividualWritePixiv(index, score):
    global api
    global pixiv_dic
    try:
        json = api.illust_detail(index)
        if 'illust' in json and json['illust']['type'] == 'illust' \
            and json['illust']['total_bookmarks'] > score \
            and json['illust']['page_count'] < 10:
            new_dic = {}
            tags = [json['illust']['tags'][i]['name'] for i in range(len(json['illust']['tags']))]
            new_dic['t'] = tags
            new_dic['u'] = json['illust']['image_urls']['medium']
            new_dic['n'] = json['illust']['page_count']
            new_dic['d'] = json['illust']['create_date']
            new_dic['s'] = json['illust']['total_bookmarks']
            pixiv_dic[index] = new_dic
    except Exception as e:
        global find
        find += 1
        pass

def IndividualFromDic(i, score):
    global pixiv_dic
    if pixiv_dic[i]['s'] > score\
        and (str(i) in pixiv_dic[i]['u']\
        or 'r18' in pixiv_dic[i]['u']):
        PixIsOnDan(i)


def PixivNotDanbooru(mode = 0, data = None):
    if mode != 2:
        last = int(input('Where to begin? '))
        limit = int(input('How many to check? '))
    score = int(input('Minimum score? '))
    global api
    global find
    global file
    global pixiv_dic
    nb, limit_active, k, p, find  = 10, 100, 0, 0.0, 0
    with open("../Pixiv_Codes.txt", 'r') as f:
        pixiv_username = f.readline().split()[1]
        pixiv_password = f.readline().split()[1]

    if mode == 0:
        function = IndividualWritePixiv
        pixiv_dic = {}
        index = range(last, last-limit, -1)
    elif mode == 1:
        file = open('NotDanbooru_Result.html', 'w')
        function = IndividualPixivNotDan
        index = range(last, last-limit, -1)
    elif mode == 2:
        file = open('NotDanbooru_Result.html', 'w')
        function = IndividualFromDic
        pixiv_dic = data
        index = list(data.keys())
        limit = len(index)
    try:
        api = AppPixivAPI()
        begin = datetime.now()
        api.login(pixiv_username, pixiv_password)
        last_login = begin
        for i in range(limit//nb):
            if (datetime.now()-last_login).total_seconds() > 3500:
                try:
                    api.login(pixiv_username, pixiv_password)
                    last_login = datetime.now()
                except:
                    print('Unable to login')
            while threading.active_count() > limit_active:
                time.sleep(0.5)
            for j in range(nb):
                Thread(target=function, args=(index[k], score)).start()
                k += 1
            ending = ((datetime.now() - begin)/k*limit + begin).strftime('%D-%H:%M')
            if p != int(k/limit*1000)/10:
                print(str(p)+'%', '|', ending, '|', find)
                p = int(k/limit*1000)/10
    except Exception as e:
        print(e)
    finally:
        if mode==0:
            name = 'pixiv/'+str((last-limit)//100000)+'.json'
            with open(name, 'w') as file:
                json.dump(pixiv_dic, file, sort_keys=True, indent=4)

        time.sleep(10)
        print('FOUND:', find)
        print('MEAN TIME:', (datetime.now()-begin)/limit)
        if find != 0:
            print('Time by result:', (datetime.now()-begin)/find)
        file.close()


def ReadJSON(file):
    with open(file, 'r') as file:
        data = json.load(file)
    PixivNotDanbooru(mode = 2, data = data)

def FuseJSON(files):
    dic = {}
    new_name = 'pixiv/new/'+input('Number of new file ? ')+'.json'
    for file in files:
        name = 'pixiv/'+file+'.json'
        with open(name, 'r') as file:
            data = json.load(file)
        for key, value in data.items():
            dic[key] = value
    with open(new_name, 'w') as file:
        json.dump(dic, file, sort_keys=True, indent=4)

def SplitJSON(file):
    dic = {}
    l = 1000000
    with open(file, 'r') as file:
        data = json.load(file)
    for key, value in data.items():
        if int(key)//l not in dic.keys():
            dic[int(key)//l] = {}
        dic[int(key)//l][key] = value
    for key, value in dic.items():
        name = 'pixiv/new'+str(key)+'.json'
        with open(name, 'w') as file:
            json.dump(value, file, sort_keys=True, indent=4)
        print('Done on', key)


if __name__ == '__main__':
    print('mode 0 : go to pixiv and write a .json')
    print('mode 1 : go to pixiv and directly check on dan')
    print('mode 2 : read a .json')
    print('mode 3 : fuse several .json')
    print('mode 4 : split .json')
    mode = int(input('Which mode ? '))
    if mode == 2:
        ReadJSON('pixiv/'+input('File number ? ')+'.json')
    elif mode == 3:
        FuseJSON(input('File numbers ? ').split())
    elif mode == 4:
        SplitJSON('pixiv/'+input('File number ? ')+'.json')
    else:
        PixivNotDanbooru(mode = mode)


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
