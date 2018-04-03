# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 21:33:32 2017

@author: Rignak
"""

import os
from PIL import Image

path = "result\\ok"
k = 1
for file in os.listdir(path):
    old_name = os.path.join(path, str(file))
    img = Image.open(old_name)
    img.show()
    c = input(file[:-4] + ': ' )
    os.system("taskkill /f /im dllhost.exe")
    if c == 'm':
        old_path = old_name.split('\\')[:-1]+['ok']
        new_name = '\\'.join(old_path) + '\\' + str(k) + old_name[-4:]
        os.rename(old_name, new_name)
        k+=1
    elif c == 'exit':
        break

