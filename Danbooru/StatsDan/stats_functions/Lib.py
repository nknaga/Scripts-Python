# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 22:39:43 2017

@author: Rignak
"""

import urllib
from sys import stdout

str1 = "http://shima.donmai.us/counts/posts.json?tags="

def NbTags(tags, username, api_key):
    tags = tags.replace(' ', '%20')
    request = str1 + tags + '&login=' + username + '&api_key=' + api_key
    try:
        page = urllib.request.urlopen(request)
        bytespage = page.read()
        deleted_number = int(bytespage.decode('utf-8')[21:-2])
        return deleted_number
    except:
        return 0

def DanbooruCodes(inside = False):
    if inside:
        path = "../../Danbooru_Codes.txt"
    else:
        path = "../Danbooru_Codes.txt"
    with open(path, 'r') as f:
        api_key = f.readline().split()[1]
        dan_username = f.readline().split()[1]
    return api_key, dan_username

def Progress(s):
    stdout.write('\r')
    stdout.write(s+'            ')
    stdout.flush()

if __name__ == '__main__':
    tags = input("Write some tags (split search with |): ").split('|')
    apiKey, userName = DanbooruCodes(inside = True)
    for tag in tags:
        nb = NbTags(tag, userName, apiKey)
        if nb > 1000:
            print(nb, ':',tag.split()[-1])
