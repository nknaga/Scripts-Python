# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 19:07:31 2017

@author: Rignak
"""

from WaifuFunctions import *
from NoiseFunctions import *
from os import listdir
import sys
import re
from datetime import datetime

def Preliminaries():
    Alt0160()
    Convert_to_jpg(ListAllFiles())
    SameName(ListAllFiles())
    Rem_Waifu()
    Replace(ListAllFiles())
    Convert_to_jpg(ListAllFiles())
    Thumbnail(ListAllFiles(maxDim = maxForThumb, minDim = maxDimWaifu),
              maxDim=maxDimWaifu)
    return

def Loop():
    listWaifu = ListAllFiles(maxDim=maxDimWaifu)

    Unnoise(listWaifu)
    Rem_Waifu()
    Replace(ListAllFiles())
    listWaifu = ListAllFiles(maxDim=maxDimWaifu)
    while listWaifu:
        LaunchWaifu(listWaifu, scale=2, noise=0)
        Rem_Waifu()
        Replace(ListAllFiles())
        Thumbnail(ListAllFiles(maxDim = maxForThumb, minDim = maxDimWaifu),
                  maxDim=maxDimWaifu)
        listWaifu = ListAllFiles(maxDim=maxDimWaifu)
    return

def Reduce():
    listThumb = ListAllFiles(minDim = maxDimAll)
    Thumbnail(listThumb, maxDim=maxDimAll)
    LaunchWaifu(listThumb, scale=0, noise=2)
    Rem_Waifu()
    Replace(ListAllFiles())
    return

if __name__ == '__main__':
    path = 'E:\\Mes documents\\Documents\\Raccourcis\\Logiciels\\Extension\\ffmpeg\\ZnT'
    l_clean = listdir(path)
    l_clean.sort(key =lambda z:int(re.split(r'[._()]+',z)[0]))
    file_list = l_clean#[120:]
    begin = datetime.now()
    now = begin
    for i, file in enumerate(file_list):
        LaunchWaifu(join(path,file), scale=0, noise = 3)
        delay = datetime.now()-now
        now = datetime.now()
        t_mean = (now-begin)/(i+1)
        estimated_end = t_mean*(len(file_list)-i) + now
        print(i+1, 'on', len(file_list), '|', estimated_end.strftime('%D - %H:%M'),
              '| mean time:', t_mean.seconds//60, ':', t_mean.seconds%60, '| last delay:',
               delay.seconds//60, ':', delay.seconds%60,)
        sys.stdout.flush()