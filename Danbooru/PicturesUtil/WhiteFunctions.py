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
import re
import os
from sys import stdout


def Progress(s):
    stdout.write('\r')
    stdout.write(s+'           ')
    stdout.flush()


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
        for y in range(self._width-1,-1, -1):
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


def onFolder(folder = dirname(realpath(__file__))):
    list_file = listdir(folder)
    Launch(list_file, folder = folder)

def onFile(f, i, folder = dirname(realpath(__file__))):
    location = join(folder, f)
    image = IMG(location)
    image.Remove_Transparency()
    image.ImToArray()
    image.Reduce()
    image.ArrayToIm()
#    if image._width > 1200 or image._height > 1200:
#        image.Thumbnail((1200,1200))
#        image.ImToArray()
    image.GetBlocs()
    image.TrimBloc()
    image.Reduce()
    image.GetBorder()
    image.ArrayToIm()
    if image._ratio < 0.3:
        image.Thumbnail((int(174*wikiRate), int(839*wikiRate)))
        image.ImToArray()
        goal = 1
    elif image._ratio <= 1:
        image.Thumbnail((int(549*gooRate), int(706*gooRate)))
        image.ImToArray()
        goal = 2
    else:
        goal = 0
    if image._border[0] and not image._border[1]:
        image.Sym_Y()
        image.ArrayToIm()
    os.remove(image._name)
    if goal:
        goal = ['wikipedia','google'][goal-1]
        path = image._name.split('\\')
        image._name = '\\'.join(path[:-1]) + '\\' + goal +'\\'+str(i)+'.jpg'
        image.Save()


def Launch(files, folder = dirname(realpath(__file__))):
    #files.sort(key =lambda z:int(re.split(r'[._()]+',z)[1]))
    n = len(files)
    begin = dt.now()
    for i, f in enumerate(files):
        if '.' != f[-4]:
            continue
        onFile(f, i, folder)

        Progress(str(i+1)+' on '+str(n)+' | '+((dt.now()-begin)/(i+1)*n + begin).strftime('%H:%M'))
    print("MEAN TIME:", (dt.now()-begin)/n)


if __name__ == '__main__':
    wikiRate = 1
    gooRate = 1.1
    a = join(dirname(realpath(__file__)), 'result\\to dobis')
    onFolder(folder=a)