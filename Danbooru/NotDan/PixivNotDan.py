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

from pixivpy3 import AppPixivAPI
case = True
controller = None
api = None
find = 0
file = None
dic_index = {}

f = open("../Danbooru_Codes.txt")
api_key = f.readline().split()[1]
dan_username = f.readline().split()[1]
f.close()

f = open("../Pixiv_Codes.txt")
pixiv_username = f.readline().split()[1]
pixiv_password = f.readline().split()[1]
f.close()

def PixIsOnDan(pixivId):
    url = 'http://danbooru.donmai.us/posts.json'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
    payload = {'limit': '1',
               'tags':'pixiv:'+str(pixivId),
               'api_key':api_key,
               'login':dan_username}
    res = requests.get(url,data=payload, headers=headers, stream=True)
    while res.status_code != 200:
        print(res.status_code)
        res = requests.get(url,data=payload, headers=headers, stream=True)
    if len(res.content) >= 100:
        return False
    else:
        prefix = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
        global file
        global find
        url = prefix+str(pixivId)
        file.write('<A HREF="' + url + '"> ' + url + '<br/>')
        find += 1

def PixivNotDanbooru():
    last = int(input('Where to begin? '))
    limit = int(input('How many to check? '))
    score = int(input('Minimum score? '))
    global api
    global find
    global file
    api = AppPixivAPI()
    api.login(pixiv_username, pixiv_password)
    nb, p, limit_active  = 50, 0, 200
    file = open('NotDanbooru_Result.html', 'w')
    try:
        begin = datetime.now()
        last_login = begin
        for i in range(limit//nb):
            if (datetime.now()-last_login).total_seconds() > 3500:
                try:
                    api.login(pixiv_username, pixiv_password)
                    last_login = datetime.now()
                except:
                    print('Unable to login')
            while threading.active_count() > limit_active:
                time.sleep(1)
            for j in range(nb):
                k = i*nb+j
                Thread(target=IndividualPixivNotDan, args=(last-k, score)).start()
            if int((k + 1)/limit*1000)/10 != p:
                p = int((k + 1)/limit*1000)/10
                ending = (datetime.now() - begin) / (k + 1) * limit + begin
                print(str(p)+'%', '|', ending.strftime('%H:%M'),'|', find)
    except Exception as e:
        print(e)
    finally:
        file.close()
        print('MEAN TIME:', (datetime.now()-begin)/limit)

def IndividualPixivNotDan(i, score):
    global api
    try:
        json_result = api.illust_detail(i)
        if 'illust' in json_result and \
            json_result['illust']['total_bookmarks'] > score and \
            int(json_result['illust']['page_count']) < 5:
            if str(i) in json_result['illust']['image_urls']['medium']:
                PixIsOnDan(i)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    PixivNotDanbooru()


# Next functions not used
def IndividualWritePixiv(i, username, password, begin, last, limit):
    global api
    global pixiv_dic
    if i%200000 == 199999:
        try:
            api.login(username, password)
        except:
            print('Unable to login')
    index = last - i
    try:
        json = api.illust_detail(index)
        if 'illust' in json and json['illust']['type'] == 'illust':
            json = json['illust']
            tags = [json['tags'][i]['name'] for i in range(len(json['tags']))]
            new_dic = {}
            new_dic['tag'] = tags
            new_dic['url'] = json['image_urls']['medium']
            new_dic['nb'] = json['page_count']
            new_dic['date'] = json['create_date']
            new_dic['sc'] = json['total_bookmarks']
            pixiv_dic[index] = new_dic
    except Exception as e:
        print(e)
        pass


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
