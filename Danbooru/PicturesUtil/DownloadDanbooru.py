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
f = open("../Danbooru_Codes.txt")
api_key = f.readline().split()[1]
username = f.readline().split()[1]
f.close()
    
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
    tags = input("Write some tags: ")
    limit = int(input("Number of pictures with the tags: "))
    urls = ListPicturesWithTag(tags, limit)
    for i, url in enumerate(urls):
        if i > limit:
            break
        print(i, '|', len(urls), '|', url)
        ok = False
        while not ok:
            try:
                r = requests.get(url, stream=True)
                ok = True
            except Exception as e:
                print(e)
                time.sleep(10)
        if r.status_code == 200:
            with open(join('result', str(i) + '.' + url.split('.')[-1]), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
Launch()
