# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 14:01:57 2018

@author: Rignak
"""

from os import listdir
from PIL import Image
import numpy as np


def GetRadicals():
    radicals = {}
    for file in listdir():
        if file.endswith('.png'):
            radical = file.split()[0]
            if radical not in radicals:
                radicals[radical] = [file]
            else:
                radicals[radical].append(file)
    return radicals

def Crop1920():
    for img in listdir():
        if img.endswith('.png'):
            ar = np.array(Image.open(img))[:,:1920]
            Image.fromarray(ar.astype(np.uint8)).save(img[:-4]+'_bis.png', format='PNG')
            
def main():
    radicals = GetRadicals()
    for radical, lst in radicals.items():
        arrays = []
        for im in lst:
            arrays.append(np.array(Image.open(im)))
        if len(arrays) != 1:
            img = []
            for i, current in enumerate(arrays[:-1]):
                minDiff = 255
                for j, line in enumerate(current):
                    diff = np.mean(abs(arrays[i+1][0]-line))
                    if diff < minDiff:
                        minJ = j
                        minDiff = diff
                [img.append(line) for line in current[:minJ]]
                if i == len(lst)-2:
                    [img.append(line) for line in arrays[i+1]]
            img = np.array(img)
            print(radical,'--', img.shape)
        else:
            img = arrays[0]
        Image.fromarray(img.astype(np.uint8)).save(radical+'.png', format='PNG')


if __name__ == '__main__':
    main()