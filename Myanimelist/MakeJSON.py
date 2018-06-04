# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 13:31:34 2017

@author: Rignak
"""

from myanimelist import session, utilities, media
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
            item = session.anime(nb)
            item.load()
            newEntry = {}
            anime[nb]['length'] = (item.duration * item.episodes).seconds//60
            anime[nb]['episodes'] = item.episodes
            anime[nb]['year'], newEntry['season'], newEntry['aired'] = AddDateInfo(item.aired)
            anime[nb]['genres'] = [genre.name for genre in item.genres]
            anime[nb]['title'] = item.title
            anime[nb]['type'] = item.type
            anime[nb]['source'] = item.source
            ok = 100
        except Exception as e:
            if 'Too Many Requests' in str(e):
                ok += 1
                Progress('                        ')
                Progress('Flood: '+str(ok))
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
            Progress('                        '+line)
    except:
        pass
    finally:
        time.sleep(3)
        print('\mMEAN TIME:', (now-begin)/limit)
        with open(join('save', 'myanimelist.json'), 'w') as file:
            json.dump(anime, file, sort_keys=True, indent=4)


def AddDateInfo(td):
    d = [date.strftime('%d/%m/%Y') for date in td if date]
    if len(d) == 2:
        begin, end = d
    else:
        begin = d[0]
    if begin:
        year =  begin.split('/')[-1]
        month = begin.split('/')[1]
        if month in ['12', '01', '02']:
            if month in ['01', '02']:
                s = 'winter ' + str(int(year)-1)
            else:
                'winter ' + year
        elif month in ['03', '04', '05']:
            s = 'spring ' + year
        elif month in ['06', '07', '08']:
            s = 'summer ' + year
        elif month in ['09', '10', '11']:
            s = 'fall ' + year
        else:
            s = None
    a = [int(date.toordinal()) for date in td if date]
    y = begin.split('/')[-1]
    return y, s, a

if __name__ == '__main__':
    CreateDic()