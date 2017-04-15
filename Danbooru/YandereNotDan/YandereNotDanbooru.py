# -*- coding: utf-8 -*-
"""
    Author: Rignak
    Python version: 3.5
"""
import socks
import socket

import urllib
import bs4 as BeautifulSoup
from datetime import datetime
from stem import Signal
from stem.control import Controller
from os.path import join

controller = Controller.from_port(port=9151)


def renew_tor():
    controller.authenticate()
    controller.signal(Signal.NEWNYM)
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
    socket.socket = socks.socksocket
    # time.sleep(10)


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
        while i <= limit//1000 + 1:
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


def IsOnDan(url_sample, url_yan):
    """Check if a sample is on dan

    Input:
    urls_yan -- A list
    urls_sample -- A list

    Output:
    False if the image is not on danbooru
    True else """
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

if __name__ == '__main__':
    tags = input("Write some tags (split search with blanck): ")
    tag_add = input("Perhaps a tag for all searchs ? ")
    limit = int(input("Choose a limit: "))
    urls = []
    if input("Check for Already found: ")=='y':
        urls_yan = AlreadyFound(CreateListAllURL(tags, limit, tag_add))
    else:
        urls_yan = CreateListAllURL(tags, limit, tag_add)
    print("The number of url is :", len(urls_yan))

    n = len(urls_yan)
    begin = datetime.now()
    try:
        for i in range(n):
            url = urls_yan[i]
            if i%24 == 0:
                renew_tor()
            res =  IsOnDan(URLSample(url), url)
            ending = (datetime.now() - begin) / (i + 1) * n + begin
            if not res:
                print("founds: ", len(urls), '|' , i + 1, 'on', n, '|',
                      ending.strftime('%D - %H:%M'), '| OK')
                urls.append(url)
            else:
                print("founds: ", len(urls), '|' , i + 1, "on", n, '|',
                      ending.strftime('%D - %H:%M'))
    except KeyboardInterrupt as e:
        print(e)
        print("Will write the report")
    finally:

        print('\n', len(urls), 'results')
        WriteHTML(urls)
        print("Done in", (datetime.now() - begin).seconds, "seconds")
