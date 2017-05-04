# -*- coding: utf-8 -*-
"""
    Author: Rignak
    Python version: 3.5
"""
from NoiseFunctions import DetectJPG
from PIL import Image
from os import remove, makedirs
from os.path import join, dirname, realpath, exists
import requests

standartRoot = 'E:\Mes images\Anime - Manga\Art'
waifuRoot = join(dirname(realpath(__file__)), "waifu")

maxDimWaifu = pow(1500, 2)
maxDimAll = pow(3000, 2)
maxForThumb = 3*maxDimWaifu

if not exists(waifuRoot):
    makedirs(waifuRoot)

def LaunchWaifu(file, ext = 'png', scale=2, noise=1):
    """
    scale :  0, 1, 2 for x1, x1.6, x2
    noise : -1, 0, 1, 2, 3 for none, low, medium, high, maximum"""
    i = True
    while i:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
            files = {'file':  (file.split('\\')[-1], open(file, 'rb'))}
            payload = {'scale': scale, 'style': 'art', 'noise': noise}

            r = requests.post('http://waifu2x.udp.jp/api', files=files,
                              data=payload, headers=headers, stream=True)
            if r.status_code == 200:
                i = False
                name = file[:-4] + '_waifu.png'
                with open(name, 'wb') as out_file:
                    out_file.write(r.content)
                out_file.close()
                if ext == 'jpg':
                    Convert_to_jpg(file)
            else:
                print(r.status_code)
        except Exception as e:
            print(e)

def Remove_Transparency(im, bg_colour=(255, 255, 255)):
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
        alpha = im.convert('RGBA').split()[-1]
        bg = Image.new("RGBA", im.size, bg_colour + (255,))
        bg.paste(im, mask=alpha)
        return bg
    else:
        return im

def Convert_to_jpg(file):
    """Convert png to jpg"""
    print("--------------")
    print("Convert_to_jpg Begin")
    if file[-4:] != ".png":
        return
    im = Image.open(file)
    im = Remove_Transparency(im).convert('RGB')
    im.save(file[:-4] + ".jpg", format="JPEG", quality=100)
    remove(file)
    im.close()

def Unnoise(file, ext = 'png'):
    if DetectJPG(file, mode = 0) < 95:
        LaunchWaifu(file, ext=ext, scale=0, noise=3)
        return True
    return False