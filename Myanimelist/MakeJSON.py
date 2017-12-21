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
from sys import stdout

base = 'https://'+'/'.join(['myanimelist.net','anime'])
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}

def Progress(s):
    stdout.write('\r'+s)
    stdout.flush()

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
        pass
        #print('Error on date:', value, e)
    return date

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
    except Exception as e:
        #print('\nexception:',e)
        return
    for key in keys:
        anime[nb][key] = GetTuple(soup, key)
    anime[nb]['Aired:'] = Date(anime[nb]['Aired:'])
    anime[nb] = FormatEntry(anime[nb])
    anime[nb]['name'] = str(soup.find('title').string).split(' - MyAnimeList.net')[0].split('\n')[1]
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
    now = begin
    limit_active = 10 + threading.active_count()
    try:
        p = None
        for nb in l:
            while threading.active_count() > limit_active:
                time.sleep(0.5)
            Thread(target=IndividualNb, args=(nb, keys)).start()
            now = datetime.now()
            p = str(int(nb/limit*1000)/10)
            ending = ((now - begin)/(nb+1)*limit + begin).strftime('%D-%H:%M')
            line = p+'% | ' + str(ending) + ' | ' + str(find)
            Progress(line)
    except:
        pass
    finally:
        time.sleep(10)
        print('MEAN TIME:', (now-begin)/limit)
        with open('myanimelist.json', 'w') as file:
            json.dump(anime, file, sort_keys=True, indent=4)

def FormatEntry(dic):
    new_dic = {}
    new_dic['genres'] = dic['Genres:']
    new_dic['studios'] = [[], list(dic['Studios:'])][dic['Studios:']  == 'add some']
    new_dic['type'] = dic['Type:']
    new_dic['source'] = [None, dic['Source:']][dic['Source:']!="Unkonwn"]
    #--------------------------------------------------------------------------
    if dic['Episodes:'] in [False, 'Unknown'] or type(dic['Episodes:'] ) == list:
        new_dic['episodes'] = 1
    else:
        new_dic['episodes'] = int(dic['Episodes:'])
    #--------------------------------------------------------------------------
    if len(dic['Aired:']) == 2:
        new_dic['begin'], new_dic['end'] = dic['Aired:']
    elif len(dic['Aired:']) == 1:
        new_dic['begin'] = dic['Aired:']
        new_dic['end'] = new_dic['begin']
    else:
        new_dic['begin'], new_dic['end'] = (None, None)
    #--------------------------------------------------------------------------
    if new_dic['begin'][0:2] in ['12', '01', '02']:
        new_dic['season'] == 'winter ' + new_dic['begin'].split('/')[-1]
    elif new_dic['begin'][0:2] in ['03', '04', '05']:
        new_dic['season'] == 'spring ' + new_dic['begin'].split('/')[-1]
    elif new_dic['begin'][0:2] in ['06', '07', '08']:
        new_dic['season'] == 'summer ' + new_dic['begin'].split('/')[-1]
    elif new_dic['begin'][0:2] in ['09', '10', '11']:
        new_dic['season'] == 'fall  ' + new_dic['begin'].split('/')[-1]
    #--------------------------------------------------------------------------
    epi_length = dic['Duration:']
    h, m, s = 0, 0, 0
    if "hr." in epi_length:
        if 'min' in epi_length:
            try:
                h, a1, m, a2 = epi_length.split()[0:4]
            except Exception as e:
                print(e, epi_length)
        else:
            h = epi_length.split()[0]
    elif 'min' in epi_length:
        m = epi_length.split()[0]
    elif 'sec' in epi_length:
        s = epi_length.split()[0]
    new_dic['length'] = (60*int(h)+int(m)+int(s)/60)*new_dic['episodes']
    #--------------------------------------------------------------------------

    return new_dic
if __name__ == '__main__':
    CreateDic()