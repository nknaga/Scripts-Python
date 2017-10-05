# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 21:33:32 2017

@author: Rignak
"""

import os
from PIL import Image

for file in os.listdir("result"):
    old_name = os.path.join("result", str(file))
    img = Image.open(old_name)
    img.show()
    c = input(file[:-4] + ': ' )
    os.system("taskkill /f /im dllhost.exe")
    if c == 'y':
        new_name = old_name[:-4] + '_ok' + old_name[-4:]
        os.rename(old_name, new_name)
    elif c == 'exit':
        break
    else:
        new_name = old_name[:-4] + '_no' + old_name[-4:]
        os.rename(old_name, new_name)
        

        