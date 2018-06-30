# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 14:39:52 2018

@author: Rignak
"""


from os import listdir,makedirs
from os.path import join,exists
from PIL import Image

root = '.'
files = listdir(root)

if not exists(join(root, 'res')):   
    makedirs(join(root, 'res'))

radicals = {}
pngs = []
for file in files:
    if file.endswith('.jpeg'):
        radical = file.split('.')[0][:-1]
        if radical not in radicals:
            radicals[radical] = [join(root, file)]
        else:
            radicals[radical].append(join(root, file))
    elif file.endswith('.png'):
        pngs.append(file)
        
# No need to sort the lists, as listdir already do that

for res, imgs in radicals.items():
    widths, heights = zip(*(i.size for i in map(Image.open, imgs)))
    total_width = sum(widths)
    max_height = max(heights)
    
    imgRes = Image.new('RGB', (total_width, max_height))
    
    x_offset = 0
    for img in map(Image.open, imgs):
      imgRes.paste(img, (x_offset,0))
      x_offset += img.size[0]
    imgRes.save(join(root,'res',res+'.jpg'), quality=100)
    
for file in pngs:
        img = Image.open(join(root, file))
        img.save(join(root, 'res', file.split('.')[0]+'.jpg'), quality=100)