# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 13:31:34 2017

@author: Rignak
"""

import bs4
import json
from datetime import datetime
from threading import Thread
import requests
import time
import threading

base = 'https://'+'/'.join(['myanimelist.net','anime'])
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}

def GetTuple(soup, key):
    values = []
    for div in soup.find_all('div'):
        span = div.find('span')
        if span and str(span.string) == key:
            fa = div.find_all('a')
            if fa:
                for a in fa:
                    values.append(str(a.string))
            else:
                s = str(div).split('</span>')[-1].split('</div>')[0].split('\n')[1][2:]
                values.append(s)
    if len(values) ==1:
        return values[0]
    return values

def Month2Int(string):
    if string[-1] == ',':
        string = string[:-1]
    corr = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',
            'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
    if string in corr:
        return corr[string]
    return string

def FormatD(string):
    string = string.replace(',', '')
    if len(string) == 1:
        return '0'+string
    return string

def Date(value):
    date = None
    try:
        date = value.split()
        d1, m1, y1, d2, m2, y2 = '01', '01', '1000', '01', '01', '1000'
        if len(date) == 1:
            y1 = date[0]
        elif len(date) == 2:
            if value != 'Not available':
                m1, y1 = date
        elif len(date) == 3:
            if date[-1] != '?':
                m1, d1, y1 = date
            else:
                y1 = date[0]
        elif len(date) == 4 and date[-2] == 'to':
            m1, y1 = date[0:2]
            if date[-1] != '?':
                y2 = date[-1]
        elif len(date) == 5:
            if date[2] == 'to':
                m1, y1, to, m2, y2 = date
            else:
                d1, m1, y1 = date[0:3]
        elif len(date) == 6:
            if date[2] == 'to':
                m1, y1, to, m2, d2, y2 = date
            elif date[3] == 'to':
                m1, d1, y1, to, m2, y2 = date
        elif len(date) == 7:
            m1, d1, y1, to, m2, d2, y2 = date
        date = ['/'.join([FormatD(d1), Month2Int(m1), y1])]
        if len(date) > 3:
            date += ['/'.join([FormatD(d2), Month2Int(m2), y2])]
    except Exception as e:
        print('Error on date:', value, e)
    return date

def GetTitle(soup):
    return str(soup.find('title').string).split(' - MyAnimeList.net')[0].split('\n')[1]

def IndividualNb(nb, keys):
    global anime
    global find
    anime[nb] = {}
    try:
        url = '/'.join([base, str(nb)])
        req = requests.get(url, headers=headers, stream=True)
        while req.status_code == 429:
            time.sleep(20)
            req = requests.get(url, headers=headers, stream=True)
        if req.status_code == 404:
            anime.pop(nb)
            return
        soup = bs4.BeautifulSoup(req.content, 'lxml')
    except:
        print(Exception)
        return
    for key in keys:
        anime[nb][key] = GetTuple(soup, key)
    anime[nb]['Aired:'] = Date(anime[nb]['Aired:'])
    anime[nb]['name'] = GetTitle(soup)
    find += 1

def CreateDic():
    global anime
    global find
    anime, find = {}, 0
    l = list(range(1,36000))
    limit = len(l)
    keys = ['Episodes:', 'Type:', 'Premiered:', 'Genres:',
            'Aired:', 'Broadcast:', 'Producers:', 'Licensors:', 'Source:',
            'Studios:', 'Duration:']
    begin = datetime.now()
    last, now = begin, begin
    limit_active = 20 + threading.active_count()
    try:
        p = None
        for nb in l:
            while threading.active_count() > limit_active:
                time.sleep(0.5)
            Thread(target=IndividualNb, args=(nb, keys)).start()
            now = datetime.now()
            if str(int(nb/limit*1000)/10) != p:
                k = nb+1
                p = str(int(nb/limit*1000)/10)
                ending = ((now - begin)/k*limit + begin).strftime('%D-%H:%M')
                print(p+'%', '|', ending, '|', find)

            if (now-last).total_seconds()>10:
                last = now
    except:
        pass
    finally:
        time.sleep(10)
        print('MEAN TIME:', (now-begin)/limit)
        with open('myanimelist.json', 'w') as file:
            json.dump(anime, file, sort_keys=True, indent=4)

if __name__ == '__main__':
    CreateDic()