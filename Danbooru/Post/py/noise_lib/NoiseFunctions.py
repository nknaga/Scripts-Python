# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 14:42:42 2017

@author: Rignak
"""
from scipy import signal as sg
from PIL import Image
import numpy as np
import io

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

def DetectJPG(pic):
    p = 3
    noise = []
    im0 = Image.open(pic)
    array0 = Grayscale(np_from_img(im0))
    array0 = Filter(array0, p)
    i = Intensity(array0)
    for q in range(89, 92):#[74,75,76,79,80,81,84,85,86,89,90,91,94,95,96]:
        f2 = io.BytesIO()
        im0.save(f2, format="JPEG", quality=q)
        im2 = Image.open(f2)
        array2 = Grayscale(np_from_img(im2))
        array2 = Filter(array2, p)

        ar3 = np.absolute(array0-array2)
        noise.append((Intensity(ar3)/i, q))
    return noise
