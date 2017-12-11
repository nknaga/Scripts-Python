# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 16:06:30 2017

@author: Rignak
"""


import requests
import time
import json
from datetime import datetime
from py_functions import Lib
from threading import Thread
import threading



api_key, username = Lib.DanbooruCodes()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
api_url = 'http://sonohara.donmai.us/post_versions.json?limit=1000&search%5Bpost_id%5D='

def Req(i):
    url = api_url+str(i)
    payload = {'api_key': api_key,
               'login': username,}
    res = requests.get(url, data=payload, headers=headers, stream=True).content
    return res

def Id2Json(i):
    r1 = json.loads(Req(i).decode('utf8'))
    for c in r1:
        r2 = {}
        for key in ['added_tags', 'post_id', 'removed_tags', 'updater_id',
            'version', 'updated_at','tags']:
            r2[key]=c[key]
        global final
        final[c['id']] =r2

def ImportJson(m,M):
    global final
    final = {}
    limit_active = int(input('Number of threads ? ')) + threading.active_count()
    try:
        begin = datetime.now()
        p = 0.0
        print('Begin at', begin.strftime('%H:%M'))
        k = 0
        for i in range(m, M+1):
            k+=1
            while threading.active_count() > limit_active:
                time.sleep(0.1)
            Thread(target=Id2Json, args=(i, )).start()
            if p != int(k / (M-m) * 10000) / 100:
                mean_time = (datetime.now() - begin) / k
                ending = (mean_time * (M-m)  + begin).strftime('%D-%H:%M')
                Lib.Progress(str(p) + '% | ' + ending + ' | ' + str(mean_time))
                p = int(k / (M-m)  * 10000) / 100
        time.sleep(10)
    except Exception as e:
        print(e, 'Stop at', i)
    with open('res/c'+str(m/100000)+'.json', 'w') as file:
        json.dump(final, file, sort_keys=True, indent=4)

if __name__ == '__main__':
    ImportJson(1,10000)