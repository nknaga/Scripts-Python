# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 12:55:10 2017

@author: Rignak
This program is to list image from fav:user on danbooru
It shows the image and allow to decide if it should be removed from fav
It write the link in a .txt, to manually double-check and unfav
"""

from AddTags import ListUrl, Sample
from datetime import datetime
from sys import stdout
from threading import Thread
import threading
import time
def Progress(s):
    stdout.write('\r')
    stdout.write(s+'           ')
    stdout.flush()

def Imgs(data):
    imgs.append(Sample(data))
    return imgs

def ListImgs(data):
    global imgs
    imgs = []
    limit_active = int(input('Number of threads ? ')) + \
        threading.active_count()
    try:
        begin = datetime.now()
        p = 0.0
        print('Begin at', begin.strftime('%H:%M'))
        for i, x in enumerate(data):
            while threading.active_count() > limit_active:
                time.sleep(0.1)
            Thread(target=Imgs, args=(x, )).start()
            if p != int(i / limit * 10000) / 100:
                mean_time = (datetime.now() - begin) / (i + 1)
                ending = (mean_time * limit + begin).strftime('%D-%H:%M')
                Progress(str(p) + '% | ' + ending + ' | ' + str(mean_time))
                p = int(i / limit * 10000) / 100
                time.sleep(0.1)
        time.sleep(10)
    except Exception as e:
        print(e, 'Stop at', i)
    return imgs


if __name__ == '__main__':
    limit = 1900
    inf = 2894374
    sup = 1000000000
    f = open("../Danbooru_Codes.txt")
    api_key = f.readline().split()[1]
    username = f.readline().split()[1]
    f.close()
    tags = 'id:<='+str(sup)+" fav:"+username+" order:id id:>="
    data = []
    for i in range((limit-1)//100+1):
        print('Searching for picts:', i+1, 'on', limit//100 + 1)
        data += ListUrl(tags+str(inf))
        inf = int(data[-1]['id'])+1
        if inf>sup:
            break
    imgs = ListImgs(data)
    r_file = open('to_del.txt', 'w')
    input('Push enter to begin')
    begin = datetime.now()
    for img in imgs:
        i += 1
        print(i, '-', img._Id, '|',
                  ((datetime.now()-begin)/(i+1)*(len(imgs)-i) + datetime.now()).strftime('%H:%M'))
        img._add = Sample.InputTags(img)
        if img._add == 'return':  # End of operations
            break
        elif img._add == 'l' :
            r_file.write('http://danbooru.donmai.us/posts/'+str(img._Id) + "\n")
    r_file.close()

