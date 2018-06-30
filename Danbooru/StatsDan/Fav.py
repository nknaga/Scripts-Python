# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 21:18:59 2017

@author: Rignak
"""
import requests
import json
from datetime import datetime
from stats_functions import Lib
from os.path import join
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
api_url = 'https://hijiribe.donmai.us/posts.json'

def Req(page, once, mode):
    if mode == 1:
        tag = 'user:'+username
    elif mode == 0:
        tag = 'fav:'+username
    payload = {'limit': str(once),
               'tags': tag,
               'api_key': api_key,
               'login': username,
               'page':str(page)}
    return requests.get(api_url, data=payload, headers=headers, stream=True).content

def FillJson(mode):
    full = []
    once = 200
    total = [4328, 24474][mode]
    error = 0
    begin = datetime.now()
    for i in range(int(total/once)):
        try:
            page = Req(i, once, mode).decode('utf8').replace("'", "")
            new_data = json.loads(page)
        except Exception as e:
            print(e)
            print(page)
            error+=1
        full += new_data
        ending = (datetime.now() - begin) / (i + 1) * int(total/once) + begin
        Lib.Progress(str(i+1) + ' on ' + str(int(total/once)) + ' | ' +
                 ending.strftime('%H:%M')+' | '+str(error))
    with open(join('res', str(mode)+username+'.json'), 'w') as file:
        json.dump(full, file, sort_keys=True, indent=4)
    return

def ReadJson(mode):
    with open(join('res', str(mode)+username+'.json'), 'r') as file:
        data = json.load(file)
    return data

def Order(mode, data):
    """mode == 0 => artist
    mode == 1 => character
    mode == 2 => copyright"""
    key = ['tag_string_artist', 'tag_string_character', 'tag_string_copyright'][mode]
    res = {}
    for dic in data:
        if type(dic)==dict:
            for s in dic[key].split():
                if s in res:
                    res[s]+=1
                else:
                    res[s]=1
    return sorted([(v, k) for (k, v) in res.items()])[-20:]

def Count(mode, data):
    print('\n',['tag_string_artist', 'tag_string_character', 'tag_string_copyright'][mode])
    for k, v in Order(mode,data):
        print(k, v)

if __name__ == '__main__':
    global api_key
    global username
    api_key, username = Lib.DanbooruCodes()
    print('mode 0 : fav, mode 1 : posted')
    mode = int(input('mode: (0 or 1) '))
    fill = input('Make a new json ? (y/n) ') == 'y'
    if fill:
        FillJson(mode)
    data = ReadJson(mode)
    Count(0, data)
    Count(1, data)
    Count(2, data)
