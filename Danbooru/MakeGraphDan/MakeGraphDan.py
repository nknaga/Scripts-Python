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
import sys
from datetime import datetime


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
    for year in range(date.today().year,2004,-1 ):
        r = [range(12, 0, -1), range(date.today().month-1, 0, -1)][year == date.today().year]
        for month in r:
            key = str(month)+'-'+str(year)
            if key in data:
                c = data[key]
            else:
                c= 0
            y.append(c)
            x.append(date(year, month, 1))
    while y[-1] == 0:
        x = x[:-1]
        y = y[:-1]
    fig, ax1 = plt.subplots()
    plt.margins(0)
    ax1.plot(x, y, marker='+')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Nb')
    plt.xticks(rotation=45)

def Progress(s):
    sys.stdout.write('\r')
    sys.stdout.write(s)
    sys.stdout.flush()

def Count(tags, mode, forced=False):
    namefile = tags.replace(':', '-').replace('/', '-').replace('>', '-').replace('?', '-')
    if not forced and CheckIfAlready(namefile):
        results = CountFromFile(namefile)
    else:
        results = {}
        i = 0
        j = len(range(date.today().year,2004,-1 ))*12
        begin = datetime.now()
        for year in range(date.today().year,2004,-1 ):
            r = [range(12, 0, -1), range(date.today().month-1, 0, -1)][year == date.today().year]
            for month in r:
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

                i+=1
                mean_time = (datetime.now()-begin)/i
                Progress(str(int(i/j*100))+'% | ' + str((mean_time*j+begin).strftime('%D-%H:%M')))
        LogCount(namefile, results)
    if mode == 0:
        total = CountFromFile('age--1s')
        for key in results.keys():
            if total[key]!=0:
                results[key] = results[key]/total[key]*100
            else:
                results[key]=0
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
    print('mode 0 : result in %')
    print('mode 1 : result in nb')
    mode = int(input('mode ? : '))
    forced = input('Force the creation of new db ? (y/n) : ')=='y'
    for tag in tags.split():
        print(tag)
        res = Count(tag, mode, forced = forced)
        Plt(res)
        print()