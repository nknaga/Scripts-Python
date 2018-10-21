# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 21:17:57 2018

@author: Rignak
"""

import json
from os.path import join, split
from os import walk

base = join('..', 'files', 'illustrations')

with open(join(base, 'novelIllustration.json'), 'r', encoding="utf-8") as file:
    novels = json.load(file)
for root, dirs, files in walk(base):
    current = split(root)[-1]
    if current == 'illustrations':
        continue
    if current not in novels:
        print('Unknown novel:', current)
    else:
        for file in files:
            print(novels[current]['roman'],
                  novels[current]['art'],
                  "novel_illustration official_art")
            print('-')