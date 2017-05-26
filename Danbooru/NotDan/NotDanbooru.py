# -*- coding: utf-8 -*-
"""
    Author: Rignak
    Python version: 3.5
"""
print('Begin')
import socks
import socket

import urllib
import bs4 as BeautifulSoup
from datetime import datetime
from stem import Signal
from stem.control import Controller
from os.path import join
from threading import Thread

from pixivpy3 import AppPixivAPI
case = True
controller = None
api = None
find = 0
file = None

def renew_tor():
    global case
    global controller
    if case:
        controller = Controller.from_port(port=9151)
        case = False
    controller.authenticate()
    controller.signal(Signal.NEWNYM)
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
    socket.socket = socks.socksocket

def IsOnDan(url_sample):
    """Check if a sample is on dan

    Output:
    False if the image is not on danbooru
    True else """
    global file
    try:
        # Look if the sample is already on Danbooru
        url = 'http://danbooru.iqdb.org/?url=' + url_sample
        page = urllib.request.urlopen(url)
        strpage = page.read().decode('utf-8')
    except Exception as e:
        print(e)
        return False
    if 'Best match' in strpage and page.getcode()==200:
        return True
    else:
        return False

def AlreadyFound(urls):
    """Remove the links of picture which are already recorded (only for yandere)"""
    root = 'E:\\Telechargements\\Anime\\post\\data'
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
        ending = (datetime.now() - begin) / (i + 1 + len(already)) * (len(urls) + len(already)) + begin
        print(len(already), 'found |', i + 1 + len(already), "on",
              len(urls) + len(already), '|', ending.strftime('%D - %H:%M'))
    return urls


def WriteHTML(urls_yan):
    """Write the result of the search in a .html

    Input:
    urls_yan -- A list

    Output:"""
    file = open('NotDanbooru_Result.html', 'w')
    for url in urls_yan:
        file.write('<A HREF="' + url + '"> ' + url + '<br/>')
    file.close()
    return

def CreateListAllURL(tags, limit,tag_add):
    """Create the list of all urls resulting of the search

    Input:
    tags -- A string
    limit -- A int

    Output:
    urls -- A list"""
    tags = tags.split(' ')
    urls = []
    for tag in tags:
        i = 1
        if len(tag)<3:
            continue
        print(tag, len(urls))
        tag = tag + "+" + tag_add  # Add a tag for all search
        while i <= (limit+1)//1000+1:
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
    url_sample -- A str"""
    ok = False
    while not ok:
        try:
            page = urllib.request.urlopen(url_yan)
            ok = True
        except:
            continue
    soup = BeautifulSoup.BeautifulSoup(page, "lxml")
    url = soup.find('meta', {"property": 'og:image'}).get('content')
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

    n = len(urls_yan)
    nb = 20
    global file
    global find
    file = open('NotDanbooru_Result.html', 'w')
    begin = datetime.now()
    try:
        for i in range(n//nb):
            ts = []
            renew_tor()
            for j in range(nb):
                k = i*nb+j
                args = (urls_yan[k],)
                ts.append(Thread(target=IndividualYandereNotDan, args=args))
                ts[-1].start()
            [t.join() for t in ts]
            ending = (datetime.now() - begin) / (k + 1) * n + begin
            print(k + 1, 'on', n, '|', ending.strftime('%D - %H:%M'), '| results:', find)
    except Exception as e:
        print(e)
    finally:
        print('MEAN TIME:', (datetime.now()-begin)/n)
        file.close()

def IndividualYandereNotDan(url_yan):
    global file
    global find
    url_sample = URLSample(url_yan)
    try:
        if not IsOnDan(url_sample):
            find += 1
            file.write('<A HREF="' + url_yan + '"> ' + url_yan + '<br/>')
    except:
        pass


def PixivNotDanbooru():
    last = int(input('Where to begin? '))
    limit = int(input('How many to check? '))
    score = int(input('Minimum score? '))

    codes = open("../Pixiv_Codes.txt")
    username = codes.readline().split()[1]
    password = codes.readline().split()[1]
    codes.close()

    begin = datetime.now()
    global api
    global find
    global file
    api = AppPixivAPI()
    file = open('NotDanbooru_Result.html', 'w')
    api.login(username, password)
    nb = 50
    for i in range(limit//nb):
        ts = []
        for j in range(nb):
            k = i*nb+j
            args = (k, username, password, begin, last, score, limit)
            ts.append(Thread(target=IndividualPixivNotDan, args=args))
            ts[-1].start()
        [t.join() for t in ts]
        ending = (datetime.now() - begin) / (k + 1) * limit + begin
        print(k + 1, 'on', limit, '|', ending.strftime('%D - %H:%M'),'| results:', find)
    print('MEAN TIME:', (datetime.now()-begin)/limit)
    file.close()

def IndividualPixivNotDan(i, username, password, begin, last, score, limit):
    global api
    global file
    global find
    censor = 'https://source.pixiv.net/common/images/limit_r18_360.png'
    prefix = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
    if i%2500 == 2499:
        try:
            api.login(username, password)
        except:
            print('Unable to login')
    index = last - i
    try:
        json_result = api.illust_detail(index)
        url = json_result['illust']['image_urls']['medium']
        s = json_result['illust']['total_bookmarks']
        type_ = json_result['illust']['type']
        if s > score and type_=='illust' and url != censor and not IsOnDan(url):
            url = prefix+str(index)
            file.write('<A HREF="' + url + '"> ' + url + '<br/>')
            find += 1
    except:
        pass
        #print('Error on', index)

if __name__ == '__main__':
    choice = input('Website? (pixiv:0, yandere:1) ')
    if choice == '1':
        YandereNotDanbooru()
    elif choice == '0':
        PixivNotDanbooru()