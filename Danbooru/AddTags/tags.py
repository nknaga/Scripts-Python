# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 21:50:59 2016

@author: Rignak
"""
import urllib
import bs4 as BeautifulSoup

url_beg = "http://sonohara.donmai.us/tags?commit=Search&page="
url_end = "&search%5Bcategory%5D=0&search%5Bhide_empty%5D=yes&search%5Border%5D=count&utf8=%E2%9C%93"

tags = []
for i in range(500):
    print(i)
    url = url_beg + str(i+1) + url_end
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup.BeautifulSoup(page, "lxml")
    td = soup.find_all('td')
    for ele in td:
        tag = str(ele).split('>')[-3][:-3]
        if tag.startswith('<'):
            continue
        if len(tag)<4:
            continue
        tags.append(tag)

f = open('tags.txt', 'w')
f.write("\n".join(tags))