# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 14:42:42 2017

@author: Rignak
"""
from scipy import signal as sg
from PIL import Image
import numpy as np
import io
from os.path import join, dirname, realpath

root = join(dirname(realpath(__file__)), "Example")

def np_from_img(im):
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
        alpha = im.convert('RGBA').split()[-1]
        bg = Image.new("RGBA", im.size, (255, 255, 255) + (255,))
        bg.paste(im, mask=alpha)
        im = bg
    return np.asarray(im, dtype=np.float32)

def img_from_np(ar):
    return Image.fromarray(ar.round().astype(np.uint8))

def Grayscale(ar):
    return np.mean(ar, -1)

def Intensity(ar):
    dimension = np.prod(ar.shape)
    return np.sum(ar)/dimension

def Filter(array, c):
    hp_filter = MakeFilter(c)
    edges = sg.convolve2d(array, hp_filter)[1:-1, 1:-1]
    edges = np.absolute(edges)
    edges = np_from_img(img_from_np(edges))
    return edges

def MakeFilter(c):
    hp_filter = np.array([[0, -1, 0],[-1, 4, -1],[0, -1, 0]])*c
    return hp_filter

def DetectJPG(fname, mode = 0):
    p = 3
    noise = []
    im0 = Image.open(fname)
    array0 = Grayscale(np_from_img(im0))
    array0 = Filter(array0, p)
    i = Intensity(array0)
    for q in [74,75,76,79,80,81,84,85,86,89,90,91,94,95,96]:
        f2 = io.BytesIO()
        im0.save(f2, format="JPEG", quality=q)
        im2 = Image.open(f2)
        array2 = Grayscale(np_from_img(im2))
        array2 = Filter(array2, p)

        ar3 = np.absolute(array0-array2)
        noise.append((Intensity(ar3)/i, q))
    if mode == 1:
        img_from_np(array2).show()
        print(noise[FirstLocalMinimum(noise)][1])
        return noise
    else:
        return(noise[FirstLocalMinimum(noise)][1])

def FirstLocalMinimum(t):
    for i in [1,4,7,10,13]:
        if t[i-1][0]-t[i][0] > 0.05 and t[i+1][0]-t[i][0] > 0.05:
            return i
    return -1


def Test():
    from matplotlib import pyplot as plt
    n1 =  'example/Miki 9A.jpg'
    y = DetectJPG(n1, mode=1)
    x = [y[a][1] for a in range(len(y))]
    y = [y[a][0] for a in range(len(y))]
    plt.plot(x, y)

    n2 =  'example/Miki 9B.jpg'
    y = DetectJPG(n2, mode=1)
    x = [y[a][1] for a in range(len(y))]
    y = [y[a][0] for a in range(len(y))]
    plt.plot(x, y)


    plt.xlabel("Quality")
    plt.ylabel("Intesity")
    plt.legend(['Noisy picture', 'Noiseless picture'])


if __name__ == '__main__':
    Test()