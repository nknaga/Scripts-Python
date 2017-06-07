# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 18:26:34 2017

@author: Rignak
"""

import pytube

f = open('Youtube_Links.txt')
lines = f.readlines()
f.close()
for i, line in enumerate(lines):
    line = line.split('\t')
    url = line[0]
    name = line[1][:-1]
    yt = pytube.YouTube(url)
    yt.set_filename(name)
    yt.filter('mp4')[-1].download('res')
    print(i+1, '/', len(lines))