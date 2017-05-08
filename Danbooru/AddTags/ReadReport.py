# -*- coding: utf-8 -*-
"""
Created on Sun Oct  31 22:21:00 2016

@author: Rignak
If the AddTags program abord, this one will be able to recover some work
"""

import requests
from datetime import datetime

codes = open("../Danbooru_Codes.txt")
api_key = codes.readline().split()[1]
username = codes.readline().split()[1]

known_tags = {'g' : 'flat_chest', 's' : 'small_breasts', 'm' : 'medium_breasts',
              'l' : 'large_breasts', 'h' : 'huge_breasts', '-' : '-sideboob -cleavage -breasts',
              'look' : 'looking_at_viewer', 'hair' : 'hair_between_eyes',
              'eye' : 'eyebrows_visible_through_hair ', 'see' : 'see-through',
              'p' : 'pass', 'f' : 'gigantic_breasts' }
f = open('tags.txt', 'r')
dic_tags = {}
for line in f:
    dic_tags[line[:-1]] = 0

def VerifyTags(tags):
    """Check if the tags exist or correspond to a shortcut
    Input & Output are str"""
    tags = tags.split()
    current_tags = []
    for tag in tags:
        if tag in known_tags:
            current_tags.append(known_tags[tag])
        elif tag in dic_tags:
            current_tags.append(tag)
        elif tag[1:] in dic_tags and tag[0] == '-':
            current_tags.append(tag)
    return ' '.join(current_tags)

def GetTag(Id):
    url = 'http://danbooru.donmai.us/posts/' + Id + '.json'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
    payload = {'api_key':api_key,
               'login': username}

    req = requests.get(url,
                        data=payload, headers=headers, stream=True)
    data = req.json()
    return data["tag_string"]

def ReadReport(file ='res.txt'):
    txt = open(file, 'r')
    begin = datetime.now()
    nb = 3000
    j = 0
    for line in txt:
        tags = line.split()[1:]
        tags = VerifyTags(' '.join(tags))
        Id = line.split()[0]
        if tags == 'pass' or tags == 'p':
            continue
        tags  += ' ' + GetTag(Id)
        url = 'http://danbooru.donmai.us/posts/' + Id + '.json'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
        payload = {'post[tag_string]': tags,
                   'api_key':api_key,
                   'login': username}
        code = 0
        while code != 200:
            try:
                code = requests.put(url,data=payload, headers=headers,
                                    stream=True).status_code
            except:
                print(code)
        j+=1
        t_mean = (datetime.now()-begin)/j
        print(j, (t_mean*(nb - j) + datetime.now()).strftime('%H:%M'), Id)
    return


ReadReport()