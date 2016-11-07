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
        tag = tag + "+" + tag_add  # Add a tag for all search
        while i <= limit//1000 + 1:
            # do it for each page
            url = 'https://yande.re/post?page=' + str(i)
            url = url + '&tags=' + tag + '+limit%3A' + str(limit)
            page = urllib.request.urlopen(url)
            soup = BeautifulSoup.BeautifulSoup(page, "lxml")
            temp = soup.find_all("span", class_="plid")

            for url in temp:
                url = url.get_text()[3:]
                if url not in urls:
                    urls.append(url)
                    if len(urls) > limit:
                        break
            i = i + 1
    return urls


def URLSample(url_yan):
    """Take a url and return the sample
    Input:
    url_yan -- A str

    Output:
    url_sample -- A str"""
    page = urllib.request.urlopen(url_yan)
    soup = BeautifulSoup.BeautifulSoup(page, "lxml")
    url = soup.find('meta', {"property": 'og:image'}).get('content')
    return url


def IsOnDan(url_sample, url_yan):
    """Check if a sample is on dan

    Input:
    urls_yan -- A list
    urls_sample -- A list

    Output:
    False if the image is not on anbooru
    True else """
    try:
        # Look if the sample is already on Danbooru
        url = 'http://danbooru.iqdb.org/?url=' + url_sample
        page = urllib.request.urlopen(url)
        strpage = page.read().decode('utf-8')
    except Exception as e:
        print(e)
        return True
    if 'Best match' in strpage:
        return True
    else:
        return False

def AlreadyFound(urls):
    """Remove the links of picture which are already recorded"""
    root = 'E:\\Telechargements\\Anime\\post\\data'
    list_L = ["L1.txt", "L2.txt", "L3.txt", "LPriority.txt"]
    links = {}
    for file in list_L:
        temp_links = open(join(root, file), "r")
        for link in temp_links:
            links[link] = 1

    for i in range(len(urls)):
        if urls[i] in links:
            urls.pop(i)
            i = i -1
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
    begin = datetime.now()
    urls = []
    urls_yan = AlreadyFound(CreateListAllURL(tags, limit, tag_add))
    print("The number of url is :", len(urls_yan))

    n = len(urls_yan)
    for i in range(n):
        url = urls_yan[i]
        if i%24 == 0:
            renew_tor()
        res =  IsOnDan(URLSample(url), url)
        ending = (datetime.now() - begin) / (i + 1) * n + begin
        if not res:
            print(url, '|' , i + 1, 'on', n, '|', ending.strftime('%H:%M'), '| OK')
            urls.append(url)
        else:
            print(url, '|' , i + 1, "on", n, '|', ending.strftime('%H:%M'))

    print('\n', len(urls), 'results')
    WriteHTML(urls)
    print("Done in", (datetime.now() - begin).seconds, "seconds")
