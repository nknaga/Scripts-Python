# -*- coding: utf-8 -*-
"""
    Author: Rignak
    Python version: 3.5
"""

import urllib
import bs4 as BeautifulSoup
from datetime import datetime
from threading import Thread
import threading
import time

def EndTime(begin, i, n):
    mean_time = (datetime.now()-begin)/i
    remaining_time = mean_time*(n-i)
    end_time = datetime.now() + remaining_time
    return end_time.strftime('%H:%M')

def GetDataLink(link):
    n = 0
    while n < 5:
        try:
            page = urllib.request.urlopen(link)
            bytespage = page.read()
            soup = BeautifulSoup.BeautifulSoup(bytespage, "lxml")
            n = 7
        except Exception as e:
            n += 1
    if n == 7:
        present_links = soup.find_all('a', href=True)
        return present_links
    else:
        return []


def GetDataWebsite(site):
    if site == '':
        return
    global visited
    global unvisited
    global pictures_id
    visited = []
    unvisited = [site]
    pictures_id = {}
    limit_active = 100+threading.active_count()

    begin = datetime.now()
    last = begin
    ini_thread = threading.active_count()
    while unvisited or threading.active_count() != ini_thread:
        while not unvisited:
            if (datetime.now()-last).total_seconds() > 300:
                return
            else:
                time.sleep(0.5)
        while threading.active_count() > limit_active:
            time.sleep(0.5)
        current_link = unvisited.pop(0)
        visited.append(current_link)
        Thread(target=IndividualGetData, args=(current_link, site)).start()
        if (datetime.now()-last).total_seconds() > 10:
            l1, l2, l3 = [len(x) for x in [visited, unvisited, pictures_id]]
            print('V|R[P:', l1,'|',l2,'|', l3,'|', EndTime(begin, l1, l1+l2))
            last = datetime.now()

def IndividualGetData(url, site):
    global visited
    global unvisited
    present_links = GetDataLink(url)
    for i, data in enumerate(present_links):
        href = data['href'].split('?')[0].split('#')[0]
        if href.startswith(site) and href not in visited and href not in unvisited:
            unvisited.append(href)
        if href.endswith(".png") or href.endswith(".jpg"):
            ID = href.split('/')[-1]
            if ID not in pictures_id:
                Thread(target=IndividualDownload, args=(href,)).start()
                pictures_id[ID] = href


def IndividualDownload(url):
    try:
        url = url.replace('-1.png', '.png').replace('-2.png', '.png').replace('-3.png', '.png')
        urllib.request.urlretrieve(url, "Images/" + url.split('/')[-1])
    except:
        pass

if __name__ == '__main__':
    GetDataWebsite(input('Enter a website: '))
