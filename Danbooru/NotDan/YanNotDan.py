# -*- coding: utf-8 -*-
"""
    Author: Rignak
    Python version: 3.5
"""
import urllib
import bs4 as BeautifulSoup
from datetime import datetime
from os.path import join
from threading import Thread
from TOR.tor import renew_tor
api = None
find = 0
file = None
dic_index = {}

def IsOnDan(url_sample):
    """Check if a sample is on dan
    Input:
    url_sample - string: url of a picture

    Output:
    False if the image is not on danbooru (or error)
    True else """
    global file
    global urls_yan
    try:
        # Look if the sample is already on Danbooru
        url = 'http://danbooru.iqdb.org/?url=' + url_sample
        page = urllib.request.urlopen(url)
        strpage = page.read().decode('utf-8')
    except Exception as e:
        if "Flood detected" in str(e):
            urls_yan.append(url_yan)
            return True
        else:
            print(e)
            return False
    if 'Best match' in strpage and page.getcode()==200:
        return True
    else:
        return False

def AlreadyFound(urls):
    """Remove the links of picture which are already recorded (only for yandere)"""
    root = '../Post/files/tags'
    list_L = ["L1.txt", "L2.txt", "L3.txt", "LPriority.txt"]
    links = {}
    for file in list_L:
        temp_links = open(join(root, file), "r")
        for link in temp_links:
            if 'yande.re' in link:
                links[link.split('/')[4]] = 1

    already = []
    begin = datetime.now()
    for i, url in enumerate(urls):
        url = URLSample(url)
        md5 =  url.split('/')[4]
        if md5 in links:
            already.append(md5)
            print(md5)
            urls.pop(i)
            i = i -1
        ending = (datetime.now() - begin) / (i + 1 + len(already)) * (len(urls) +\
                len(already)) + begin
        print(len(already), 'found |', i + 1 + len(already), "on",
              len(urls) + len(already), '|', ending.strftime('%D - %H:%M'))
    return urls


def CreateListAllURL(tags, limit,tag_add):
    """Create the list of all urls resulting of the search

    Input:
    tags -- A string
    limit -- A int
    tag_add -- A string

    Output:
    urls -- A list of string"""
    tags = tags.split(' ')
    urls = []
    for tag in tags:
        i = 1
        if len(tag)<3:
            continue
        print(tag, len(urls))
        tag = tag + "+" + tag_add  # Add a tag for all search
        while i <= int(limit/1000)+1:
            # do it for each page
            url = 'https://yande.re/post?page=' + str(i)
            url = url + '&tags=' + tag + '+limit%3A' + str(limit)
            page = urllib.request.urlopen(url)
            soup = BeautifulSoup.BeautifulSoup(page, "lxml")
            temp = soup.find_all("span", class_="plid")
            if len(temp) ==0:
                break
            for turl in temp:
                turl = turl.get_text()[3:]
                if turl not in urls:
                    urls.append(turl)
            print(i, '/', limit//1000 + 1)
            i = i + 1
    return urls

def URLSample(url_yan):
    """Take a url and return the sample
    Input:
    url_yan -- A str

    Output:
    url -- A str"""
    ok = False
    while not ok:
        try:
            page = urllib.request.urlopen(url_yan)
            ok = True
            soup = BeautifulSoup.BeautifulSoup(page, "lxml")
            url = soup.find('meta', {"property": 'og:image'}).get('content')
        except Exception as e:
            print(e)
            continue
    return url

def YandereNotDanbooru():
    tags = input("Write some tags (split search with blanck): ")
    tag_add = input("Perhaps a tag for all searchs ? ")
    limit = int(input("Choose a limit: "))
    check = input("Check for Already found: ")
    urls_yan = CreateListAllURL(tags, limit, tag_add)
    if check=='y':
        urls_yan = AlreadyFound(urls_yan)
    print("The number of url is :", len(urls_yan))
    nb, k = 24, 0
    global file
    global find
    global urls_yan
    file = open('NotDanbooru_Result.html', 'w')
    try:
        begin = datetime.now()
        for i in range(int(len(urls_yan)/nb)+1):
            ts = []
            renew_tor()
            for j in range(nb):
                if k < len(urls_yan)-1:
                    k += 1
                    ts.append(Thread(target=IndividualYandereNotDan,
                                     args=(urls_yan[k],)))
                    ts[-1].start()
            [t.join() for t in ts]
            ending = (datetime.now() - begin) / (k + 1) * len(urls_yan) + begin
            print(k + 1, 'on', len(urls_yan), '|', ending.strftime('%H:%M'), '|', find)
    except Exception as e:
        print(e)
    finally:
        print('MEAN TIME:', (datetime.now()-begin)/len(urls_yan))
        file.close()

def IndividualYandereNotDan(url_yan):
    global file
    global find
    url_sample = URLSample(url_yan)
    try:
        if not IsOnDan(url_sample, url_yan):
            find += 1
            file.write('<A HREF="' + url_yan + '"> ' + url_yan + '<br/>')
    except:
        pass

if __name__ == '__main__':
    YandereNotDanbooru()
