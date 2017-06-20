# -*- coding: utf-8 -*-
"""
    Author: Rignak
    Python version: 3.5
"""

import urllib
import bs4 as BeautifulSoup
from os.path import join, dirname, realpath
import os
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
    for i in range(int(limit/200)):
        url = "https://danbooru.donmai.us/posts?page=" + str(i + 1)
        url = url + "&tags=limit%3A200+" + tags.replace(' ','+')
        url += "&login="+username+"&api_key="+api_key
        print(url)
        page = urllib.request.urlopen(url)
        bytespage = page.read()
        soup = BeautifulSoup.BeautifulSoup(bytespage, "lxml")
        for sample in soup.find_all('article'):
            entry = "http://danbooru.donmai.us/"
            entry = entry + sample.get("data-file-url")
            list_pictures_with.append(entry)
            limit = limit - 1
            if limit == 0:
                break
    return list_pictures_with

def DownloadPictures(url, name, folder = join(dirname(realpath(__file__)), 'result')):
    """Download one image as a jpeg
    Input:
    list_pictures -- A url, a string
    name -- A string, the name without the extension
    folder -- A string
    """
    try:
        os.mkdir(folder)
    except Exception:
        pass
    urllib.request.urlretrieve(url,join(folder, name + url[-4:]))
    return

def Launch():
    tags = input("Write some tags: ")
    limit = int(input("Number of pictures with the tags: "))
    list_pictures = ListPicturesWithTag(tags, limit)
    for i, url in enumerate(list_pictures):
        DownloadPictures(url, str(i))

#Launch()
