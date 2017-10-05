# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 14:09:22 2017

@author: Rignak
"""

from time import sleep
from urllib.request import urlopen
import json
import matplotlib.pyplot as plt
from datetime import date
import urllib
from os.path import join, exists

from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'qt')

str1 = "http://sonohara.donmai.us/counts/posts.json?tags="
f = open("../Danbooru_Codes.txt")
api_key = f.readline().split()[1]
username = f.readline().split()[1]
f.close()

def NbTags(tags):
    request = str1 + tags + '&login=' + username + '&api_key=' + api_key
    e = True
    while e:
        try:
            e = False
            page = urlopen(request)
        except urllib.error.HTTPError:
            print('Spam?')
            sleep(300)
            e = True

    bytespage = page.read()
    nb = int(bytespage.decode('utf-8')[21:-2])
    return nb

def CheckIfAlready(tag):
    if exists(join('db', tag+'.json')):
        return True
    return False

def Plt(data):
    x = []
    y = []
    for year in range(2005, date.today().year+1):
        for month in range(1, 13):
            key = str(month)+'-'+str(year)
            if key in data:
                c = data[key]
            else:
                c= 0
            plt.ion()
            y.append(c)
            x.append(date(year, month, 1))
    fig, ax1 = plt.subplots()
    ax1.plot(x, y, marker='+')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Nb')

def Count(tags, forced=False):
    if not forced and CheckIfAlready(tags):
        return CountFromFile(tags)
    results = {}
    i = 0
    j = len(range(date.today().year,2004,-1 ))*12
    for year in range(date.today().year,2004,-1 ):
        for month in range(12, 0, -1):
            i+=1
            if month == 12:
                nMonth = 1
                nYear = year+1
            else:
                nMonth = month+1
                nYear = year
            dateframe = 'date:'+str(year)+'-'+str(month)+'-'+'01..'+str(nYear)+'-'+str(nMonth)+'-'+'01'
            current_tags = tags +'%20' + dateframe
            nb = NbTags(current_tags)
            results[str(month)+'-'+str(year)] = nb
            print(i, j)
    LogCount(tags, results)
    return results

def CountFromFile(tags):
    with open('db/'+tags+'.json', 'r') as file:
        return json.load(file)

def LogCount(tags, results):
    with open('db/'+tags+'.json', 'w') as file:
        json.dump(results, file, sort_keys=True, indent=4)
    return

if __name__ == '__main__':
    tags = input('Enter tag : ')
    forced = input('Force the creation of new db ? (y/n) : ')=='y'
    res = Count(tags, forced = forced)
    Plt(res)