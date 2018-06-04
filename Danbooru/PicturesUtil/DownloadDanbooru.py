# -*- coding: utf-8 -*-
"""
    Author: Rignak
    Python version: 3.5
"""

import urllib
import bs4 as BeautifulSoup
import requests
import shutil
from os.path import join, exists
import time
import os
from datetime import datetime
from sys import stdout
from threading import Thread
import threading

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
    
if exists("../Danbooru_Codes.txt"):
    with open("../Danbooru_Codes.txt") as f:
        api_key = f.readline().split()[1]
        username = f.readline().split()[1]
    payload = {'api_key':api_key, 'login':username}
else:
    print('no danbooru account: will be limited to two tags')
    payload = {}
if not exists('results'):
    os.makedirs('results')
                   
def Progress(s):
    stdout.write('\r')
    stdout.write(s+'           ')
    stdout.flush()

def ListPicturesWithTag(tags, limit):
    """ Return a list of 'limit1' url, with the tags 'tags'

    Input:
    tags -- A string
    limit -- An int

    Output:
    list_pictures_with -- A list"""
    list_pictures_with = []
    n = 200
    begin = datetime.now()
    for i in range(int(limit/n)+1):
        eta = ((datetime.now()-begin)/(i+1)*int(limit/n)+begin).strftime('%H:%M')
        Progress(str(i)+'/'+str(int(limit/n))+' | '+tags+' | '+eta)
        url = "http://hijiribe.donmai.us/posts?page=" + str(i + 1)
        url = url + "&tags=limit%3A200+" + tags.replace(' ','+')
        if exists("../Danbooru_Codes.txt"):
            url += "&login="+username+"&api_key="+api_key
        req = urllib.request.Request(url, headers=hdr)
        page = urllib.request.urlopen(req)
        bytespage = page.read()
        soup = BeautifulSoup.BeautifulSoup(bytespage, "lxml")
        for j, sample in enumerate(soup.find_all('article')):
            entry = sample.get("data-large-file-url")
            entry = sample.get("data-preview-file-url")
            list_pictures_with.append(entry)
    return list_pictures_with


def Launch():
    limit_active = int(input("Thread number : ")) + threading.active_count()
    tags = input("Write some tags (split search with |): ").split('|')
    for tag in tags:
        try:
            replace = ('>', '<', '?', ':')
            name = tag.split()[-1]
            for key in replace:
                name = name.replace(key, '-')
            if not exists(join('results', name)):
                os.makedirs(join('results', name))
        except Exception as e:
            print(e)
    limits = [int(i) for i in input("Number of pictures with the tags (split with blank): ").split()]
    if len(limits) not in [1, len(tags)] :
        print('Error : not same length')
        return
    elif len(limits) == 1:
        limits = [limits[0] for i in range(len(tags))]
    total = sum(limits)
    begin = datetime.now()
    k = 0
    for j in range(len(tags)):
        urls = ListPicturesWithTag(tags[j], limits[j])
        folder = tags[j].split()[-1]
        for key in replace:
            folder = folder.replace(key, '-')
        for i, url in enumerate(urls):
            k +=1
            if i > limits[j]:
                break
            while threading.active_count() > limit_active:
                time.sleep(0.1)
            Thread(target=Download, args=(i, folder, url)).start()
            ending = (datetime.now() - begin) / k  * total + begin
            Progress(str(k) + ' on ' + str(total) + ' | ' + ending.strftime('%D-%H:%M'))


def Download(i, folder, url):
    if url.endswith('png') or url.endswith('jpg'):
        name = str(i)
        while len(name) < 6:
            name = '0'+name
        while folder.endswith('.'):
            folder = folder[:-1]
        fullname = join('results', folder, name + '.' + url.split('.')[-1][:3])
        k = 0
        while True:
            r = requests.get(url, stream=True, data=payload, headers=hdr)
            sc = r.status_code
            if sc == 200:
                with open(fullname, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
                break
            elif sc == 429:
                time.sleep(1)
            elif k == 5:
                break
            else:
                k += 1
        if not os.path.exists(fullname):
            print('not created:', url, sc)

if __name__ == '__main__':
    Launch()