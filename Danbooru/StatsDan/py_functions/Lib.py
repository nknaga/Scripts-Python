# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 22:39:43 2017

@author: Rignak
"""

import urllib
from time import sleep
from sys import stdout

str1 = "http://sonohara.donmai.us/counts/posts.json?tags="

def NbTags(tags, username, api_key):
    request = str1 + tags + '&login=' + username + '&api_key=' + api_key
    e = True
    while e:
        try:
            e = False
            page = urllib.request.urlopen(request)
        except urllib.error.HTTPError:
            print('Spam?')
            sleep(300)
            e = True

    bytespage = page.read()
    deleted_number = int(bytespage.decode('utf-8')[21:-2])
    return deleted_number

def DanbooruCodes():
    with open("../Danbooru_Codes.txt", 'r') as f:
        api_key = f.readline().split()[1]
        dan_username = f.readline().split()[1]
    return api_key, dan_username

def Progress(s):
    stdout.write('\r')
    stdout.write(s+'            ')
    stdout.flush()
