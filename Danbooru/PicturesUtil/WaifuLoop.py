# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 19:07:31 2017

@author: Rignak
"""

from WaifuFunctions import *
from NoiseFunctions import *

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
    """
    Preliminaries()
    Loop()
    Reduce()"""
    l_noise = ListAllFiles(folder='E:\\Telechargements\\Anime\\ors\\ok\\noise')
    l_clean = ListAllFiles(folder='E:\\Telechargements\\Anime\\ors\\ok\\clean')
    print(len(l_clean))
    #LaunchWaifu(l_noise, scale=0, noise = 3)
    LaunchWaifu(l_clean, scale=0, noise = 0)
    #print(jpeg)
