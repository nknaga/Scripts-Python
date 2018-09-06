# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 14:39:52 2018

@author: Rignak
"""


from os import listdir,makedirs
from os.path import join,exists
import numpy as np
from PIL import Image, ImageChops

class IMG():
    def __init__(self, filename):
        self._name = filename
        self._im = Image.open(filename)
        self._array =  np.asarray(self._im, dtype=np.float32)
        self._height = len(self._array)
        self._width = len(self._array[0])

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


    def Reduce(self, i = 255*0.80):
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

    def Save(self, ext = 'jpeg'):
        if ext == 'jpg':
            self._im.save(self._name[:-4] + ".jpg", format="JPEG", quality=100)
        if ext == 'jpeg':
            self._im.save(self._name[:-5] + ".jpeg", format="JPEG", quality=100)
        else:
            self._im.save(self._name[:-4] + ".png", format="PNG")


def Initialization(root):
    root = '.'
    files = listdir(root)

    if not exists(join(root, 'res')):
        makedirs(join(root, 'res'))
    return files

def main(root='.'):
    radicals = {}
    pngs = []
    files = Initialization(root)
    for file in files:
        if file.endswith('.jpeg'):

            img = IMG(file)
            img.Reduce()
            img.ArrayToIm()
            img.Save(ext='jpeg')

            radical = file.split('.')[0][:-1]
            if radical not in radicals:
                radicals[radical] = [join(root, file)]
            else:
                radicals[radical].append(join(root, file))
        elif file.endswith('.png'):
            pngs.append(file)

    # No need to sort the lists, as listdir already do that

    for res, imgs in radicals.items():
        imgs = [Image.open(img) for img in imgs]
        widths, heights = zip(*(ing.size for ing in imgs))
        total_width = sum(widths)
        max_height = max(heights)

        imgRes = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for img in imgs:
            imgRes.paste(img, (x_offset,0))
            x_offset += img.size[0]
        imgRes.save(join(root,'res',res+'.jpg'), quality=100)

    for file in pngs:
            img = Image.open(join(root, file))
            img.save(join(root, 'res', file.split('.')[0]+'.jpg'), quality=100)


if __name__ == '__main__':
    main()