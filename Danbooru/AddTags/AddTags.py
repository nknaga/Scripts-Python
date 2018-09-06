# -*- coding: utf-8 -*-
"""
Created on Sun Oct  31 22:21:00 2016

@author: Rignak
"""
import urllib
import requests
from io import BytesIO
from PIL import Image
from os import system
from datetime import datetime
from time import sleep
from threading import Thread
import threading
import time
f = open("../Danbooru_Codes.txt")
api_key = f.readline().split()[1]
username = f.readline().split()[1]
f.close()
#known_tags = {'f' : 'flat_chest', 's' : 'small_breasts', 'm' : 'medium_breasts',
#              'l' : 'large_breasts', 'h' : 'huge_breasts', '-' : '-sideboob -cleavage -breasts',
#              'look' : 'looking_at_viewer', 'hair' : 'hair_between_eyes',
#              'eye' : 'eyebrows_visible_through_hair ', 'see' : 'see-through',
#              'p' : 'pass', 'g' : 'gigantic_breasts' }
#"""known_tags = {',' : 'flat_chest', '1' : 'small_breasts', '2' : 'medium_breasts',
#              '4' : 'large_breasts', '3' : 'huge_breasts', '-' : '-sideboob -cleavage -breasts',
#              'look' : 'looking_at_viewer', 'hair' : 'hair_between_eyes',
#              'eye' : 'eyebrows_visible_through_hair ', 'see' : 'see-through',
#              'p' : 'pass', 'f' : 'gigantic_breasts' }"""
known_tags = {'y' : 'pass', 'n' : '-saber_alter', 'm' : 'medium_breasts'}
f = open('tags.txt', 'r')
dic_tags = {}
for line in f:
    dic_tags[line[:-1]] = 0

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}

from sys import stdout

def Progress(s):
    stdout.write('\r')
    stdout.write(s+'            ')
    stdout.flush()

class Sample:
    """Depict a sample with:
    - the Id of the image on danbooru (an str(int))
    - the data of the image (BytesIO(urllib.request.urlopen))
    - the tags corresponding to the image (a str)"""


    def __init__(self, dic):
        self._Id = str(dic['id'])

        url_sample = dic['large_file_url']+"?login="+username+"&api_key="+api_key
        ok = 0
        while ok <5:
            try:
                req = urllib.request.Request(url_sample, headers=hdr)
                page = urllib.request.urlopen(req)
                self._data = BytesIO(page.read())
                ok = 5
            except Exception as e:
                ok+=1
                print("Error on", self._Id, e, url_sample)
                print('url:', url_sample)
        self._tags = dic['tag_string']
        self._adds = ''

    def InputTags(self):
        """Display a sample, and ask an input to add tags"""
        try:
            temp_img = Image.open(self._data)
            temp_img.show()
        except:
            return 'pass'

        while self._adds == '':
            self._adds = input('tags ? ')
        system("taskkill /f /im dllhost.exe")
        return self._adds

    def AddTags(self):
        """Changes the tags of the pict _Id to _tags on danbooru"""
        if self._adds == 'pass':
            return 200
        addition = self.GetTag() + ' '+ VerifyTags(self._adds)
        url = 'http://danbooru.donmai.us/posts/' + self._Id + '.json'
        payload = {'post[tag_string]': addition,
                   'api_key':api_key,
                   'login':username}
        res = requests.put(url,data=payload, headers=hdr, stream=True)
        return res.status_code

    def GetTag(self):
        url = 'http://danbooru.donmai.us/posts/' + self._Id + '.json'
        payload = {'api_key':api_key,
                   'login': username}

        req = requests.get(url, data=payload, headers=hdr, stream=True)
        data = req.json()
        return data["tag_string"]


def VerifyTags(tags):
    """Check if the tags exist or correspond to a shortcut
    Input & Output are str"""
    tags = tags.split()
    current_tags = []
    for tag in tags:
        if tag in known_tags:
            current_tags.append(known_tags[tag])
        elif tag in dic_tags:
            current_tags.append(tag)
        elif tag[1:] in dic_tags and tag[0] == '-':
            current_tags.append(tag)
    return ' '.join(current_tags)


def ListUrl(tags):
    """Make a rqst to danbooru in order to get the data"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
    payload = {'limit ': 100, 'tags' : tags,
               'api_key':api_key,
               'login': username}
    req = requests.get('https://danbooru.donmai.us/posts.json',
                        data=payload, headers=headers, stream=True)
    data = req.json()
    return data

def ThreadSample(dic):
    global imgs
    imgs.append(Sample(dic))

def ListImgs(data):
    """Create a list of imgs, sample object"""
    global imgs
    imgs = []
    limit_active = 4 + threading.active_count()
    begin = datetime.now()
    for i,dic in enumerate(data):
        if not (dic['large_file_url'].endswith('.jpg') or  dic['large_file_url'].endswith('.png')):
            continue
        while threading.active_count() > limit_active:
            time.sleep(0.1)
        Thread(target=ThreadSample, args=(dic, )).start()
        eta = ((datetime.now()-begin)/(i+1)*len(data)+begin).strftime('%H:%M')
        Progress(str(i+1)+'/'+str(len(data))+' | '+eta+' | '+str(threading.active_count()))


    time.sleep(60)
    return imgs

def main():
    inf = 2990000
    sup = 4000000
    tags = "breasts age:<60d -comic -flat_chest -small_breasts -medium_breasts -large_breasts -huge_breasts -gigantic_breasts order:id id:>"
    tags = "artoria_pendragon_(swimsuit_archer) saber"
    #tags = "saber_alter  artoria_pendragon_(swimsuit_rider_alter)"
    limit = 3000
    data = []
    res = []
    for i in range((limit-1)//100+1):
        print('Searching for picts:', i+1, 'on', (limit-1)//100+1, '|', inf)
        data += ListUrl(tags+str(inf))
        if inf == data[-1]['id']:
            break
        inf = data[-1]['id']
        if inf>sup:
            break

    imgs = ListImgs(data)

    input('Push enter to begin')
    # Asking data from user
    begin = datetime.now()
    for i,img in enumerate(imgs):
        print(i+1, '-', img._Id, '|',
              ((datetime.now()-begin)/(i+1)*(len(imgs)-i) + datetime.now()).strftime('%H:%M'))
        img._add = Sample.InputTags(img)
        if img._add == 'return':  # End of operations
            break
        elif img._add == 'pass':
            continue
        else:
            res.append(img)
    print('MEAN TIME:', (datetime.now()-begin)/(i+1))
    begin = datetime.now()
    for i,img in enumerate(res):
        code = 0
        while code != 200:
            try:
                code = img.AddTags()
            except:
                code = 0
            if code != 200:
                sleep(5)
                print(code)
            t_mean = (datetime.now() - begin)/(i+1)
            print(img._Id, '|', i+1, 'on', len(res), '|',
                  (t_mean*(len(res) - i-1) + datetime.now()).strftime('%H:%M'))
    return


if __name__ == '__main__':
    res = main()
