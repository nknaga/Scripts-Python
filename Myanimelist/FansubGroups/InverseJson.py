# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 10:34:15 2018

@author: Rignak
"""

import json


with open('fansubs.json', 'r') as file:
    fansub = json.load(file)
anime = {}
for key, dic in fansub.items():
    if not dic or not dic['language'] in ['english', 'English'] or not 'projects' in dic:
        continue
    name = dic['name']
    for project in dic['projects']:
        title = project['name']
        if 'positiveOpinion' in project:
            s = f"{project['positiveOpinion']}/{project['opinion']}"
        else:
            s = []
        if title in anime:
            anime[title][name] = [s]+project['comments']
        else:
            anime[title] = {name:[s]+project['comments']}

with open('anime.json', 'w') as file:
    json.dump(anime, file, sort_keys=True, indent=4)