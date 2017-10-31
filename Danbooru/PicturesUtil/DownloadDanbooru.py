# -*- coding: utf-8 -*-
"""
    Author: Rignak
    Python version: 3.5
"""

import urllib
import bs4 as BeautifulSoup
import requests
import shutil
from os.path import join
import time
import os
from datetime import datetime
from sys import stdout
from threading import Thread
from PIL import Image
import threading

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
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}

    for i in range(int(limit/200)+1):
        url = "https://danbooru.donmai.us/posts?page=" + str(i + 1)
        url = url + "&tags=limit%3A200+" + tags.replace(' ','+')
        url += "&login="+username+"&api_key="+api_key
        req = urllib.request.Request(url, headers=hdr)
        page = urllib.request.urlopen(req)
        bytespage = page.read()
        soup = BeautifulSoup.BeautifulSoup(bytespage, "lxml")
        for sample in soup.find_all('article'):
            entry = "https://danbooru.donmai.us/"
            entry = entry + sample.get("data-file-url")
            list_pictures_with.append(entry)
    return list_pictures_with


def Launch():
    limit_active = int(input("Thread number : "))
    tags = input("Write some tags (split search with |): ").split('|')
    for tag in tags:
        try:
            os.makedirs(join('result', tag.split()[-1]))
        except Exception as e:
            print(e)
    limits = [int(i) for i in input("Number of pictures with the tags (split with blank): ").split()]
    if len(tags)!=len(limits):
        print('Error : not same length')
        return
    total = sum(limits)
    begin = datetime.now()
    k = 0
    for j in range(len(tags)):
        urls = ListPicturesWithTag(tags[j], limits[j])
        folder = tags[j].split()[-1]
        for i, url in enumerate(urls):
            k +=1
            if i > limits[j]:
                break
            while threading.active_count() > limit_active:
                time.sleep(0.1)
            Thread(target=Download, args=(i, folder, url)).start()
            ending = (datetime.now() - begin) / k  * total + begin
            Progress(str(k) + ' on ' + str(total) + ' | ' + ending.strftime('%H:%M'))


def Download(i, folder, url):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(join('result', folder, str(i) + '.' + url.split('.')[-1]), 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

if __name__ == '__main__':
    with open("../Danbooru_Codes.txt") as f:
        api_key = f.readline().split()[1]
        username = f.readline().split()[1]
    Launch()