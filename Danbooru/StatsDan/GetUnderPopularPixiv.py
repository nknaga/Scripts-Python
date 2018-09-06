# -*- coding: utf-8 -*-
"""
Created on Sat Jun  9 13:59:54 2018

@author: Rignak
"""
from stats_functions import Lib
from os.path import join
import json
from datetime import datetime


def GetArttags():
    api_key, username = Lib.DanbooruCodes()
    data = []
#    with open(join('res', '1'+username+'.json'), 'r') as file:
#        data += json.load(file)
    with open(join('res', '0'+username+'.json'), 'r') as file:
        data += json.load(file)
    artists = {}
    for entry in data:
        if entry['pixiv_id']:
            print(entry['pixiv_id'])
            for artist in entry['tag_string_artist'].split():
                if artist in artists:
                    artists[artist].append(int(entry['score']))
                else:
                    artists[artist] = [int(entry['score'])]
    for artist in artists:
        artists[artist] = sum(artists[artist])/len(artists[artist])
    return artists
    
def FillNbTags(tags):
    api_key, username = Lib.DanbooruCodes()
    doublets = {}
    l = len(tags)
    begin = datetime.now()
    for i, tag in enumerate(tags):
        doublets[tag] = Lib.NbTags(tag, username, api_key)
        
        ending = (datetime.now() - begin) / (i + 1) * l + begin
        Lib.Progress(str(i+1) + '/' + str(l) + ' | ' + ending.strftime('%H:%M'))
    with open(join('res', 'arttags.json'), 'w') as file:
        json.dump(doublets, file, sort_keys=True, indent=4)
        
def ReduceArttags(doublets, artists):
    for artist, nb in doublets.items():
        if nb > 25:#↓10:
            artists[artist] = -1
    print()
    for artist,score in sorted(artists.items(), key=lambda p:p[1], reverse=True):
        if score > 10:# and score <=10:
            print('https://danbooru.donmai.us/posts?tags='+artist)
if __name__ == '__main__':
    artists = GetArttags()
    #FillNbTags(artists)
#    with open(join('res', 'arttags.json'), 'r') as file:
#        doublets = json.load(file)
#    ReduceArttags(doublets, artists)