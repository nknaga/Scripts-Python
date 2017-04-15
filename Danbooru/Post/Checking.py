# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 13:42:12 2017

@author: Rignak
"""
import socks
import socket

import urllib
from datetime import datetime
from stem import Signal
from stem.control import Controller
from os.path import join

# Declare each files wich will be used
root = "E:\Telechargements\Anime\post\data"
error_fname = "error.txt"
banned_fname = "banned_artist.txt"
list_T = ["T1.txt", "T2.txt", "T3.txt", "T4.txt", "Priority.txt"]
list_L = ["L1.txt", "L2.txt", "L3.txt", "L4.txt", "LPriority.txt"]
list_HTML = []
for i in range(len(list_T)):
    list_T[i] = join(root, list_T[i])
    list_L[i] = join(root, list_L[i])
    list_HTML.append(list_T[i][:-4] + 'Advanced.html')

controller = Controller.from_port(port=9151)

def renew_tor():
    controller.authenticate()
    controller.signal(Signal.NEWNYM)
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
    socket.socket = socks.socksocket

def LaunchChecking():
    data = CheckHTML()
    if input("Launch BadId ? ") == 'y':
        res = CheckBadId(data)
    else:
        res = []
    if input("Launch IsOnDan ? ") == 'y':
        res += CheckDan(data)
    Write(res)
    return

def CheckHTML():
	"""Check if the link is actual URL"""
    print("Check on HTML")
    data= {}
    for i in range(len(list_T)):
        f_T = open(list_T[i])
        f_L = open(list_L[i])
        for tags in f_T:
            link = f_L.readline()
            if link in data and link:
                print(link)
            else:
                data[link]=tags
    return data

def CheckBadId(data):
	"""Check if the link to pixiv is dead"""
    print("Check on Pixiv")
    res = ['Pixiv bad Id:\n']
    begin = datetime.now()
    for i, link in enumerate(data):
        if 'pixiv' in link:
            req = urllib.request.Request(link)
            req.add_header('Referer', 'http://www.pixiv.net/')
            try:
                urllib.request.urlopen(req).getcode()
            except:
                res.append(link)
        if i%50 == 49:
            ending = (datetime.now() - begin) / (i + 1) * len(data) + begin
            print('Bad id:',len(res)-1, '|', i+1, '/', len(data), ' - ',
                  ending.strftime('%H:%M'))
    return res

def Write(res):
    file = open('CheckBadId.txt', 'w')
    for link in res:
        file.write(link)
    return

def CheckDan(data):
	"""Check if the image is already on danbooru"""
    print("Check on Dan")
    res = ['On Dan (probably)\n']
    begin = datetime.now()
    i = 0
    for link in data:
        i += 1
        if link.startswith("https://files.yande.re/"):
            link.replace('/image/', '/sample/')
            link.replace('/jpeg/', '/sample/')
        if 'http' not in link:
            continue
        if 'seiga' in link:
            link_temp = 'http://lohas.nicoseiga.jp/thumb/' + link.split('/')[-1] + 'i'
        else:
            link_temp = link
        if i%24 == 0:
            renew_tor()
        try:
            # Look if the sample is already on Danbooru
            url = 'http://danbooru.iqdb.org/?url=' + link_temp
            page = urllib.request.urlopen(url)
            strpage = page.read().decode('utf-8')
            if 'Best match' in strpage and page.getcode()==200:
                res.append(link)
        except:
            res.append(link)
        ending = (datetime.now() - begin)/i * len(data) + begin
        print('Probably already on dan:',len(res)-1, '|', i, '/',
              len(data), '-', ending.strftime('%H:%M'))
    return res

LaunchChecking()
