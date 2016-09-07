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

controller = Controller.from_port(port=9151)


def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
    socket.socket = socks.socksocket


def renew_tor():
    controller.authenticate()
    controller.signal(Signal.NEWNYM)
    # time.sleep(10)


def CreateListAllURL(tags, limit):
    """Create the list of all url of the search

    Input:
    tags -- A string
    limit -- A string

    Output:
    urls -- A list"""
    tags = tags.split(' ')
    urls = []
    for tag in tags:
        tag = tag + "+" + tag_add  # Add a tag for all search
        for i in range(int(limit) // (1000 - 1) + 1):
            # do it for each page
            url = 'https://yande.re/post?page=' + str(i + 1)
            url = url + '&tags=' + tag + '+limit%3A' + limit
            page = urllib.request.urlopen(url)
            soup = BeautifulSoup.BeautifulSoup(page, "lxml")
            temp = soup.find_all("span", class_="plid")
            for url in temp:
                url = url.get_text()[3:]
                if url not in urls:
                    urls.append(url)

    print("Search for : ", tags, len(urls), "found")
    return urls


def URLSample(urls_yan):
    """Take the list of urls and return the sample
    Input:
    urls_yan -- A list of str

    Output:
    urls_sample -- A list of str"""
    urls_sample = []
    begin = datetime.now()
    for i in range(len(urls_yan)):
        if (i % 50 == 49):
            ending = (datetime.now() - begin) / i * len(urls_yan) + begin
            print("Collecting samples, end at", ending.strftime('%H:%M'),
                  (i, len(urls_yan)))
        try:
            url = urls_yan[i]
            page = urllib.request.urlopen(url)
            soup = BeautifulSoup.BeautifulSoup(page, "lxml")
            url = soup.find('meta', {"property": 'og:image'}).get('content')
            urls_sample.append(url)
        except Exception as e:
            print(e)
            urls_sample.append("error")
    return urls_sample


def IsOnDan(urls_yan, urls_sample):
    """Check if each entry is on Danbooru and remove if so

    Input:
    urls_yan -- A list
    urls_sample -- A list

    Output:
    urls_yan -- A list"""
    print("The number of url is :", len(urls_yan))
    begin = datetime.now()
    j = 0
    for i in range(len(urls_yan)):
        if j == 24:
            # Change tor identity
            j = 0
            renew_tor()
            connectTor()
        try:
            j = j + 1
            # Look if the sample is already on Danbooru
            url = 'http://danbooru.iqdb.org/?url=' + urls_sample[i]
            page = urllib.request.urlopen(url)
            strpage = page.read().decode('utf-8')
        except Exception as e:
            print(e)
            urls_yan[i] = ''
            continue

        ending = (datetime.now() - begin) / (i + 1) * len(urls_yan) + begin
        if 'Best match' in strpage:
            T = urls_yan[i] + ' is     | '
            urls_yan[i] = ''
        else:
            T = urls_yan[i] + ' is not | '
        print(T, i + 1, ' on ', len(urls_yan), '|', ending.strftime('%H:%M'))
    return urls_yan


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
    limit = input("Choose a limit: ")
    begin = datetime.now()

    urls_yan = CreateListAllURL(tags, limit)
    urls_sample = URLSample(urls_yan)  # Get the samples
    urls_yan = IsOnDan(urls_yan, urls_sample)

    while '' in urls_yan:
        urls_yan.remove('')

    print('\n', len(urls_yan), 'results')
    WriteHTML(urls_yan)
    print("Done in", (datetime.now() - begin).seconds, "seconds")
