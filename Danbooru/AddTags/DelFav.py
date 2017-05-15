# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 12:55:10 2017

@author: Rignak
This program is to list image from fav:user on danbooru
It shows the image and allow to decide if it should be removed from fav
It write the link in a .txt, to manually double-check and unfav
"""

from AddTags import ListImgs, ListUrl, Sample
from datetime import datetime

limit = 2500
inf = 2439224
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

