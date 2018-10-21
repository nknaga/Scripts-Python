# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 15:45:38 2018

@author: Rignak
"""

import json
from os.path import join

namefile = join('..', 'files', 'illustrations', 'to add.txt')
with open(namefile, 'r', encoding="utf-8") as file:
    newEntries = [line.split() for line in file.readlines()[1:]]
namefile = join('..', 'files', 'illustrations', 'novelIllustration.json')
with open(namefile, 'r', encoding="utf-8") as file:
    novels = json.load(file)
for copy, romaji, artist in newEntries:
    if copy in novels:
        print(f"Error: {copy} in json")
    else:
        novels[copy] = {"roman":romaji, "art":artist}
with open(namefile, 'w') as file:
    json.dump(novels, file, sort_keys=True, indent=4)