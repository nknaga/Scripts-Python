# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 12:55:10 2017

@author: Rignak
This program is to list image from fav:user on danbooru
It shows the image and allow to decide if it should be removed from fav
It write the link in a .txt, to manually double-check and unfav
"""

from AddTags import *

limit = 2000
inf = 1630287
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
    inf = data[-1]['id']
    if inf>sup:
        break
imgs = ListImgs(data)
r_file = open('to_del.txt', 'w')
for img in imgs:
    i += 1
    print(i, '-', img._Id)
    img._add = Sample.InputTags(img)
    if img._add == 'return':  # End of operations
        break
    elif img._add == 'l' :
        r_file.write(str(img._Id) + "\n")
r_file.close()

