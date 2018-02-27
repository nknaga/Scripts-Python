# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 21:50:59 2016

@author: Rignak
"""
import urllib
import bs4 as BeautifulSoup
from sys import stdout
from datetime import datetime
from time import sleep
from threading import Thread
import threading

def Progress(s):
    stdout.write('\r')
    stdout.write(s+'            ')
    stdout.flush()

def DanbooruCodes():
    with open("../Danbooru_Codes.txt", 'r') as f:
        api_key = f.readline().split()[1]
        dan_username = f.readline().split()[1]
    return api_key, dan_username

def IndividualRequest(url,i):
    global tags
    ok = False
    while not ok:
        try:
            page = urllib.request.urlopen(url)
            soup = BeautifulSoup.BeautifulSoup(page, "lxml")
            ok = True
        except:
            pass
    td = soup.find_all('td')
    if i == 0:
        j = -3
    elif i == 1:
        j = 2
    for ele in td:
        tag = str(ele).split('>')[j][:-3]
        if tag and not tag.startswith('<') and tag!='fix' and tag != 'show':
            tags.append(tag)


if __name__ == '__main__':
    urls_beg = ["http://sonohara.donmai.us/tags?commit=Search&page=",
               "http://sonohara.donmai.us/tag_aliases?commit=Search&limit=1000&page="]
    urls_end = ["&search%5Bhide_empty%5D=yes&search%5Border%5D=count&limit=1000",
               "&search%5Border%5D=tag_count&search%5Bstatus%5D=Approved"]
    ls = [150, 12]
    api_key, username = DanbooruCodes()
    global tags
    tags = []
    begin = datetime.now()
    limit_active = 20
    for i in range(len(ls)):
        urls_end[i] += '&login=' + username + '&api_key=' + api_key
        for j in range(1,ls[i]+1):
            while threading.active_count() > limit_active:
                sleep(0.1)
            url = urls_beg[i] + str(j) + urls_end[i]
            Thread(target=IndividualRequest, args=(url,i)).start()
            ending = (datetime.now() - begin) / j * sum(ls) + begin
            Progress(str(j+ls[0]*i) + ' on ' + str(sum(ls)) + ' | ' + ending.strftime('%H:%M') + ' | ' + str(len(tags)))
    sleep(200)
    tags = set(tags)
    with open('tags.txt', 'w') as f:
        for tag in tags:
            try:
                f.write(tag+'\n')
            except:
                print('error:', tag)