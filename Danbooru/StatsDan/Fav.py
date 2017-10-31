# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 21:18:59 2017

@author: Rignak
"""
import requests
import json
from datetime import datetime
from lib import Lib

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
api_url = 'http://sonohara.donmai.us/posts.json'

def Req(page, once):
    payload = {'limit': str(once),
               'tags': 'fav:'+username,
               'api_key': api_key,
               'login': username,
               'page':str(page)}
    return requests.get(api_url, data=payload, headers=headers, stream=True).content

def FillJson():
    full = []
    once = 1
    total = 5132
    error = 0
    begin = datetime.now()
    for i in range(int(total/once)):
        try:
            new_data = json.loads(Req(i, once).decode('utf8').replace("'", '"'))
        except:
            error+=1
        full += new_data
        ending = (datetime.now() - begin) / (i + 1) * int(total/once) + begin
        Lib.Progress(str(i+1) + ' on ' + str(int(total/once)) + ' | ' +
                 ending.strftime('%H:%M')+' | '+str(error))
    with open(username+'.json', 'w') as file:
        json.dump(full, file, sort_keys=True, indent=4)
    return

def ReadJson():
    with open(username+'.json', 'r') as file:
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
    return sorted([(v, k) for (k, v) in res.items()])

def Count(mode, data):
    print(['tag_string_artist', 'tag_string_character', 'tag_string_copyright'][mode])
    for k, v in Order(mode,data):
        if k > 50:
            print(k, v)

if __name__ == '__main__':
    global api_key
    global username
    api_key, username = Lib.DanbooruCodes()
    #FillJson()
    data = ReadJson()
    Count(0, data)
    Count(1, data)
    Count(2, data)