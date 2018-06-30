# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 11:38:26 2018

@author: Rignak
"""

from PIL import Image
import numpy as np

threshold = 30


class Tile():
    def __init__(self, im, i):
        self._content = im
        self._size = im.size
        self._id = i
        self.ar = np.array(im).astype(np.int16)
        self._simil = {}
        
        
def GetTileHeight(ar):
    diffs = [(0, 0)]
    sizes = [-1]
    for i in range(ar.shape[0]-1):
        diff = np.mean(abs(ar[i]-ar[i+1]))
        diffs.append((diff, i))
        if diff > threshold:
            sizes.append(i)
    for i in range(1, len(sizes)):
        sizes[-i] = sizes[-i]-sizes[-i-1]
    sizes.pop(0)
    eles = {}
    for size in sizes:
        if size not in eles:
            eles[size] = 0
        else:
            eles[size] +=1
    size = max(eles.keys(), key=(lambda key: eles[key]))
    return size


def Main(filename):
    im = Image.open(filename)
    ar = np.array(im).astype(np.int16)
    dim = (GetTileHeight(np.swapaxes(ar,1,0)), GetTileHeight(ar))
    print('Tile size:', dim)
    return(dim)

def HowToSquareTile(filename, dim):
    im = Image.open(filename)
    size = im.size
    print('Image size:', size)
    r = dim[0]/dim[1]
    if r > 1:
        print('Image size to square tile:', (size[0], int(size[1]*r)))
    else:
        print('Image size to square tile:', (int(size[0]/r), size[1]))
        
    
if __name__ == '__main__':
    from os.path import join
    
    print('On square tile:')
    filename = join('images', "demo_puzzle.jpg")
    dim = Main(filename)
    HowToSquareTile(filename, dim)
    
    print('\nOn rectangular tile:')
    filename = join('images', "demo_novel.jpg")
    dim = Main(filename)
    HowToSquareTile(filename, dim)
    
    print('\nOn rectangularized tile:')
    filename = join('images', "demo_novel(squared).jpg")
    dim = Main(filename)