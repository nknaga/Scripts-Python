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

f = open("../Danbooru_Codes.txt")
api_key = f.readline().split()[1]
username = f.readline().split()[1]
f.close()
known_tags = {'g' : 'flat_chest', 's' : 'small_breasts', 'm' : 'medium_breasts',
              'l' : 'large_breasts', 'h' : 'huge_breasts', '-' : '-sideboob -cleavage -breasts',
              'look' : 'looking_at_viewer', 'hair' : 'hair_between_eyes',
              'eye' : 'eyebrows_visible_through_hair ', 'see' : 'see-through',
              'p' : 'pass', 'f' : 'gigantic_breasts' }
f = open('tags.txt', 'r')
dic_tags = {}
for line in f:
    dic_tags[line[:-1]] = 0


class Sample:
    """Depict a sample with:
    - the Id of the image on danbooru (an str(int))
    - the data of the image (BytesIO(urllib.request.urlopen))
    - the tags corresponding to the image (a str)"""


    def __init__(self, dic):
        self._Id = str(dic['id'])
        url_sample = 'http://hijiribe.donmai.us'+dic['large_file_url']
        ok = False
        while not ok:
            try:
                self._data = BytesIO(urllib.request.urlopen(url_sample).read())
                ok = True
            except:
                print("Error on", self._Id)
                break
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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
        payload = {'post[tag_string]': addition,
                   'api_key':api_key,
                   'login':username}
        res = requests.put(url,data=payload, headers=headers, stream=True)
        return res.status_code

    def GetTag(self):
        url = 'http://danbooru.donmai.us/posts/' + self._Id + '.json'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
        payload = {'api_key':api_key,
                   'login': username}

        req = requests.get(url,
                            data=payload, headers=headers, stream=True)
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

def ListImgs(data):
    """Create a list of imgs, sample object"""
    imgs = []
    begin = datetime.now()
    for i,dic in enumerate(data):
        imgs.append(Sample(dic))
        t_mean = (datetime.now() - begin)/(i+1)
        if i%10 == 9:
            print(i+1,'on', len(data), '| id:', imgs[-1]._Id, '|',
                 (t_mean*(len(data) - i-1) + datetime.now()).strftime('%H:%M'))
    return imgs

def main():
    inf = 2668973
    sup = 2700000
    tags = 'id:<='+str(sup)+" -animated* -comic breasts -flat_chest -small_breasts -medium_breasts -large_breasts -huge_breasts -gigantic_breasts order:id id:>"
    limit = 1600
    data = []
    res = []

    # Asking data from website
    for i in range((limit-1)//100+1):

        print('Searching for picts:', i+1, 'on', (limit-1)//100+1, '|', inf)
        data += ListUrl(tags+str(inf))
        inf = data[-1]['id']
        if inf>sup:
            break

    begin = datetime.now()
    imgs = ListImgs(data)
    print(datetime.now() - begin)
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

    r_file = open('res.txt', 'w')
    r_file2 = open('res2.txt', 'w')
    for img in res:
        r_file.write('1 - ' + str(img._Id) + '\n\n' + str(img._adds) + '\n')
        r_file2.write(str(img._Id) + ' ' + str(img._adds) + '\n')
    r_file.close()
    # Launch the modifications to danbooru
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
