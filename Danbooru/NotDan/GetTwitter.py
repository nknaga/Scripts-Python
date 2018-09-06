# -*- coding: utf-8 -*-
"""
Created on Thu Aug 23 16:42:04 2018

@author: Rignak
"""

import requests
from TS import twitterScraper
import os
import shutil
from sys import stdout

def Progress(s):
    stdout.write('\r')
    stdout.write(s+'            ')
    stdout.flush()
    
    
def DownloadPic(url, namefile):
    k = 0
    while True:
        r = requests.get(url, stream=True)
        sc = r.status_code
        if sc == 200:
            with open(os.path.join('res', namefile), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
                break
        elif k == 5:
            break
        else:
            k += 1
            
def main():
    toDownload = []
    artName = "boz_kun"
    pageLimit = 300
    print('Search for tweets:')
    try:
        for i, tweet in enumerate(twitterScraper.get_tweets(artName, pages=pageLimit)):
            for i, pic in enumerate(tweet['entries']['photos']):
                namefile = f"{artName} {tweet['tweetId']} {i} {pic.split('/')[-1]}"
                toDownload.append((namefile, pic))
    except Exception as e:
        print('Error', e)
        
    print('Grab pictures')
    for i, (namefile, pic) in enumerate(toDownload):
        Progress(f'{i}/{len(toDownload)}')
        DownloadPic(pic, namefile)
        
if __name__ == '__main__':
    main()