# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 13:31:34 2017

@author: Rignak
"""

from myanimelist import session
from threading import Thread
import time
import threading
from sys import stdout
import json
from os.path import join
from datetime import datetime

def Progress(s):
    stdout.write('\r'+s)
    stdout.flush()

def IndividualNb(nb,):
    global anime
    global session
    anime[nb] = {}
    ok = 0
    while ok < 100:
        try:
            anime[nb] = session.anime(nb)
            anime[nb].load()
            ok = 100
            return
        except Exception as e:
            if 'Too Many Requests' in str(e):
                ok += 1
                time.sleep(0.3)
            else:
                return

def CreateDic():
    global anime
    global session
    session = session.Session()
    anime = {}
    l = list(range(1,40000))
    limit = len(l)
    begin = datetime.now()
    now = begin
    limit_active = 1 + threading.active_count()
    try:
        for nb in l:
            while threading.active_count() > limit_active:
                time.sleep(0.1)
            Thread(target=IndividualNb, args=(nb,)).start()
            now = datetime.now()
            p = str(int(nb/limit*1000)/10)
            ending = ((now - begin)/(nb+1)*limit + begin).strftime('%D-%H:%M')
            line = p+'% | ' + str(ending) + ' | ' + str(len(anime))
            Progress(line)
    except:
        pass
    finally:
        time.sleep(3)
        anime = FormatAnime(anime)
        print('\mMEAN TIME:', (now-begin)/limit)
        with open(join('save', 'myanimelist.json'), 'w') as file:
            json.dump(anime, file, sort_keys=True, indent=4)

def FormatAnime(anime):
    newAnime = {}
    begin = datetime.now()
    nb = 0
    for key, item in anime.items():
        nb += 1
        newEntry = {}
        try:
            newEntry['length'] = (item.duration * item.episodes).seconds//60
            newEntry['episodes'] = item.episodes
            newEntry['year'], newEntry['season'], newEntry['aired'] = AddDateInfo(item.aired)
            newEntry['genres'] = [genre.name for genre in item.genres]
            newEntry['title'] = item.title
            newEntry['type'] = item.type
            newAnime[key] = newEntry

        except Exception as e:
            print(e)
            pass
        p = str(int(nb/len(anime)*1000)/10)
        now = datetime.now()
        ending = ((now - begin)/(nb+1)*len(anime) + begin).strftime('%D-%H:%M')
        line = p+'% | ' + str(ending)
        Progress(line)
    return newAnime

def AddDateInfo(td):
    d = [date.strftime('%d/%m/%Y') for date in td if date]
    if len(d) == 2:
        begin, end = d
    else:
        begin = d[0]
    if begin:
        if begin.split('/')[1] in ['12', '01', '02']:
            s = 'winter ' + begin.split('/')[-1]
        elif begin.split('/')[1] in ['03', '04', '05']:
            s = 'spring ' + begin.split('/')[-1]
        elif begin.split('/')[1] in ['06', '07', '08']:
            s = 'summer ' + begin.split('/')[-1]
        elif begin.split('/')[1] in ['09', '10', '11']:
            s = 'fall ' + begin.split('/')[-1]
    a = [int(date.toordinal()) for date in td if date]
    y = begin.split('/')[-1]
    return y, s, a

if __name__ == '__main__':
    CreateDic()