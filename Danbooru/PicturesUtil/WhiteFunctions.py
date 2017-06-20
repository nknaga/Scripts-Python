# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 16:54:38 2017

@author: Rignak
"""

from PIL import Image
import numpy as np
from datetime import datetime as dt
from os import listdir
from os.path import join, dirname, realpath
import WaifuFunctions
import sys
import re
import DownloadDanbooru


class bloc():
    """A bloc is a set of pixel, surrounded only by white pixel"""
    def __init__(self, img, xy, i = 255*0.98):
        self._coord = set()
        self.CreateBloc(img, xy, i)

    def CreateBloc(self, img, xy, i):
        limit = set()
        limit.add(xy)
        while limit:
            (x, y) = limit.pop()
            self._coord.add((x, y))
            if x+1 < img._height and ((img._array[x+1, y,:3] < [i]*3).any()) and ((x+1, y) not in limit) and ((x+1, y) not in self._coord):
                limit.add((x+1, y))
            if y+1 < img._width and ((img._array[x, y+1,:3] < [i]*3).any()) and ((x, y+1) not in limit) and ((x, y+1) not in self._coord):
                limit.add((x, y+1))
            if x-1 >= 0 and ((img._array[x-1, y,:3] < [i]*3).any()) and ((x-1, y) not in limit) and ((x-1, y) not in self._coord):
                limit.add((x-1, y))
            if y-1 >= 0 and ((img._array[x, y-1,:3] < [i]*3).any()) and ((x, y-1) not in limit) and ((x, y-1) not in self._coord):
                limit.add((x, y-1))

class IMG():
    def __init__(self, filename):
        self._name = filename
        self._im = Image.open(filename)
        self._array =  np.asarray(self._im, dtype=np.float32)
        self._height = len(self._array)
        self._width = len(self._array[0])
        self._ratio = self._width/self._height
        self._blocs = []
        self._border = [False, False, False, False]

    def GetBlocs(self, i = 255*0.98):
        """Detect the blocs constituting the image"""
        seen = set()
        for x in range(self._height):
            for y in range(self._width):
                if ((self._array[x, y,:3] < [i]*3).any()) and not (x, y) in seen:
                    current_bloc = bloc(self, (x, y), i=i)
                    self._blocs.append(current_bloc)
                    for coord in current_bloc._coord:
                        seen.add(coord)

    def TrimBloc(self):
        """Keep only the larger bloc, all other bloc is replace by white pixels"""
        blocs_inf = []
        max_len_bloc = 0
        max_bloc = []
        for bloc in self._blocs:
            if len(bloc._coord) < max_len_bloc:
                blocs_inf.append(bloc._coord)
            else:
                blocs_inf.append(max_bloc)
                max_len_bloc = len(bloc._coord)
                max_bloc = bloc._coord
        w = len(self._array)
        h = len(self._array[0])
        for x in range(w):
            for y in range(h):
                if (x,y) not in max_bloc:
                    self._array[x,y,:3] = (255, 255, 255)

    def Reduce(self, i = 255*0.98):
        """Trim the white row and column of the image"""
        s = 0
        x=0
        xmin, xmax, ymin, ymax = [0,self._height,0,self._width]
        for x in range(self._height-1):
            if s == 1:
                xmin = x
                break
            for y in range(self._width):
                l = np.array([e < i for e in self._array[x,y,:3]])
                if l.any():
                    s = 1
                    break
        s = 0
        for y in range(self._width-1):
            if s == 1:
                ymin=y
                break
            for x in range(self._height):
                l = np.array([e < i for e in self._array[x,y,:3]])
                if l.any():
                    s=1
                    break
        s = 0
        for x in range(self._height-1,-1, -1):
            if s == 1:
                xmax = x
                break
            for y in range(self._width):
                l = np.array([e < i for e in self._array[x,y,:3]])
                if l.any():
                    s = 1
                    break
        s = 0
        for y in range(self._width-1):
            if s == 1:
                ymax=y
                break
            for x in range(self._height-1,-1, -1):
                l = np.array([e < i for e in self._array[x,y,:3]])
                if l.any():
                    s=1
                    break
        self.Crop(max(xmin-1,0), min(xmax+1, self._height), max(ymin-1,0), min(ymax+1,self._width))
        return max(xmin-1,0), min(xmax+1, self._height), max(ymin-1,0), min(ymax+1,self._width)

    def Crop(self, xmin, xmax, ymin, ymax):
        """Crop the image on the indicated coordinates"""
        temp = self._array[xmin:xmax,ymin:ymax,:3]
        self._array = temp

    def Remove_Transparency(self, bg_colour=(255, 255, 255)):
        alpha = self._im.convert('RGBA').split()[-1]
        bg = Image.new("RGBA", self._im.size, bg_colour + (255,))
        bg.paste(self._im, mask=alpha)
        self._im = bg

    def Thumbnail(self, size = (1000, 822)):
        self._im.thumbnail(size)

    def Sym_Y(self):
        """Applicate a axial symetry on the image"""
        temp = self._array[:,::-1,:3]
        self._array = temp

    def ImToArray(self):
        self._array = np.asarray(self._im, dtype=np.float32)
        self._height = len(self._array)
        self._width = len(self._array[0])
        self._ratio = self._width/self._height
        return self._array

    def ArrayToIm(self):
        self._im = Image.fromarray(self._array.round().astype(np.uint8))
        self._height = len(self._array)
        self._width = len(self._array[0])
        self._ratio = self._width/self._height
        return self._im

    def Show(self):
        self._im.show()

    def Save(self, ext = 'jpg'):
        if ext == 'jpg':
            self._im.save(self._name[:-4] + ".jpg", format="JPEG", quality=100)
        else:
            self._im.save(self._name[:-4] + ".png", format="PNG")

    def GetBorder(self, i =255):
        """Change the border to know if a side a mostly white or not"""
        s = 0
        for e in [e for e in self._array[:,0]]:
            if (e != [i]*3).all():
                s += 1
        if s>self._height*0.1:
            self._border[0]= True
        s = 0
        for e in [e for e in self._array[:,-1]]:
            if (e != [i]*3).all():
                s += 1
        if s>self._height*0.1:
            self._border[1]= True
        s = 0
        for e in [e for e in self._array[0,:]]:
            if (e != [i]*3).all():
                s += 1
        if s>self._width*0.1:
            self._border[2]= True
        s = 0
        for e in [e for e in self._array[-1,:]]:
            if (e != [i]*3).all():
                s += 1
        if s>self._width*0.1:
            self._border[3]= True

def Full():
    tags = 'age:<9d+~white_background+~transparent_background+-watermark+fav:rignak'
    n = 10000
    urls = DownloadDanbooru.ListPicturesWithTag(tags, n)
    sys.stdout.flush()
    Launch(urls, mode = 'full')

def onFolder(folder = dirname(realpath(__file__))):
    list_file = listdir(folder)
    Launch(list_file, mode = 'folder', folder = folder)

def Launch(files, mode='full', folder = dirname(realpath(__file__))):
    files.sort(key =lambda z:int(re.split(r'[._()]+',z)[1]))
    n = len(files)
    begin = dt.now()
    for i, f in enumerate(files):
        if mode == 'full':
            location = join(dirname(realpath(__file__)), 'result', str(i) +'.jpg')
            DownloadDanbooru.DownloadPictures(f, str(i))
        elif mode == 'folder':
            location = join(folder, f)
        image = IMG(location)
        image.Remove_Transparency()
        image.ImToArray()
        image.Reduce()
        image.ArrayToIm()
        image.Save()
        if image._height*image._width<2900*2900 and WaifuFunctions.Unnoise(image._name):
            image._name = image._name[:-4] + "_waifu.png"
            location = join(dirname(realpath(__file__)), 'result', image._name)
            image = IMG(location)
        if image._width > 1500 or image._height > 1500:
            image.Thumbnail((1500,1500))
            image.ImToArray()
        image.GetBlocs()
        image.TrimBloc()
        image._name = image._name = image._name[:-4] + "_trimmed" + image._name[-4:]
        image.Reduce()
        image.GetBorder()
        image.ArrayToIm()
        if image._ratio < 0.3:
            image.Thumbnail((174, 676))
            image.ImToArray()
            image._name = image._name[:-4] + "_wikipedia" + image._name[-4:]
        elif image._ratio <= 1:
            image.Thumbnail((549, 706))
            image.ImToArray()
            image._name = image._name[:-4] + "_google" + image._name[-4:]
        if image._border[0] == True:
            image._name = image._name[:-4] + "_left" + image._name[-4:]
        if image._border[1] == True:
            image._name = image._name[:-4] + "_right" + image._name[-4:]
        if image._border[2] == True:
            image._name = image._name[:-4] + "_up" + image._name[-4:]
        if image._border[3] == True:
            image._name = image._name[:-4] + "_down" + image._name[-4:]
        if "left" in image._name and "right" not in image._name:
            image.Sym_Y()
            image.ArrayToIm()
            image._name = image._name.replace("left", "right")
        image._name = image._name[:-4] + "_end" + image._name[-4:]
        image.Save()
        print(i+1, 'on', n, '|', (dt.now()-begin)/(i+1)*n + begin)
    print("MEAN TIME:", (dt.now()-begin)/n)


if __name__ == '__main__':
#Full(folder = join(dirname(realpath(__file__)), 'result\\test'))
    a = join(dirname(realpath(__file__)), 'result\\to do')
    onFolder(folder=a)
