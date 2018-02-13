# -*- coding: utf-8 -*-
"""
    Author: Rignak
    Python version: 3.5
"""
from datetime import datetime
import bs4 as BeautifulSoup
from threading import Thread
import threading
import time
import requests
import json
from pixivpy3 import AppPixivAPI
from io import BytesIO
from PIL import Image
from os import system
import urllib
from lib.progress import Progress
from lib.Proxy import SetProxy, TestProxy, renew_tor
import io


with open("../Danbooru_Codes.txt", 'r') as f:
    api_key = f.readline().split()[1]
    dan_username = f.readline().split()[1]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
api_url = 'http://danbooru.donmai.us/posts.json'
prefix = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='


class Sample:
    """Depict a sample with:
    - the Id of the image on danbooru (an str(int))
    - the data of the image (BytesIO(urllib.request.urlopen))
    - the tags corresponding to the image (a str)"""

    def __init__(self, url):
        ok = 0
        self._url = url
        self._adds = ''
        while ok <7 :
            try:
                req = urllib.request.Request(url)
                req.add_header('Referer', 'https://www.pixiv.net/')
                self._data = BytesIO(urllib.request.urlopen(req).read())
                ok = 7
            except Exception as e:
                print("\nSample init - error on", self._url, e)
                ok+=1

    def InputTags(self):
        """Display a sample, and ask an input to add tags"""
        try:
            Image.open(self._data).show()
        except BaseException:
            return 'pass'
        while self._adds == '':
            self._adds = input('tags ? ')
        system("taskkill /f /im dllhost.exe")
        return self._adds


def AddEntry(index):
    try:
        retry = 0
        while retry < 6:
            try:
                json = illust_detail(index, req_auth=True)
                while 'error' in json and 'Rate Limit' == json['error']['message']:
                    time.sleep(60)
                    json = illust_detail(index, req_auth=True)
                if 'reason' not in json:
                    retry = 7
                else:
                    retry += 1
            except BaseException:
                retry += 1
        if 'illust' in json:
            json = json.illust
            if json.total_bookmarks > score and json.page_count < 10:
                global res
                res[index] = {}
                res[index]['t'] = [tag.name for tag in json.tags] + \
                                [str(json.user.id)]
                #res[index]['u'] = json.image_urls.medium
                res[index]['n'] = json.page_count
                #res[index]['d'] = json.create_date
                res[index]['s'] = json.total_bookmarks
                res[index]['r'] = json.height / json.width
        elif 'error' in json and 'ID' not in json.error.user_message:
            print(json.error)
    except Exception as e:
        print(e, '\n')


def CheckOnDan(pixivId):
    payload = {'limit': '1',
               'tags': 'pixiv:' + str(pixivId),
               'api_key': api_key,
               'login': dan_username}
    req = requests.get(api_url, data=payload, headers=headers, stream=True)
    t = 0
    while req.status_code != 200 and t < 5:
        req = requests.get(api_url, data=payload, headers=headers, stream=True)
        t += 1
    if len(req.content) >= 100 or t == 5:
        return True
    else:
        global file
        url = prefix + str(pixivId)
        res.append(pixivId)
        file.write('<A HREF="' + url + '"> ' + url + '<br/>')
        return False


def JsonReading(files):
    with io.open("blacklist.txt", 'r', encoding='utf8') as f:
        blacklist = []
        for line in f:
            blacklist.append(line[:-1])
    print('----------------------------\n---- BEGIN JSON READING ----')
    r = input("score range ? ")
    if ':' in r:
        scm, scM = r.split(':')
    elif r:
        scm, scM = r, 99999999
    else:
        scm, scM = 0, 99999999
    tags_user = input('tags? ')
    score = [int(scm), int(scM), tags_user]

    with io.open("tags.txt", 'r', encoding='utf8') as f:
        nb = {}
        cor = {}
        tags = f.readlines()
    for line in tags:
        for tag in line.split():
            if tag in tags_user:
                nb[line.split()[-1]] = 0
                cor[tag] = line.split()[-1]

    tag_f = input('Enforce tags? : ').split()
    tag_rem = input("Tags to blacklist ? ")
    for tag in tag_rem.split():
        blacklist.append(tag)
    data = []
    scm, scM, tags = score
    for j, file in enumerate(files):
        Progress("read : " + str(j) + '/' + str(len(files)))
        with open('pixiv/' + file + '.json', 'r') as file:
            temp = json.load(file)
        for i, v in temp.items():
            if (v['s'] > scm and v['s'] < scM) \
            and (not tag_f or any(tag in v['t'] for tag in tag_f))\
            and (not any(tag in v['t'] for tag in blacklist))\
            and (not tags or any(tag in v['t'] for tag in tags.split())):
                data.append(int(i))
                for tag in set(tags.split()).intersection(set(v['t'])):
                    nb[cor[tag]] += 1
    print()
    for k, v in sorted([(v, k) for (k, v) in nb.items()]):
        print(k, ':', v)
    print('----------------------------')
    if input(str(len(data)) + ' images found. Check on Dan ? (y/n) ') == 'y':
        Routeur123(mode=1, data=data)
        if input('Continue to extract urls ? (y/n) : ') == 'y':
            ShowPixiv()


def JsonSpliting(files):
    l = 1000000
    data = {}
    dic = {}
    for file in files:
        with open('pixiv/' + file + '.json', 'r') as file:
            data.update(json.load(file))
    for key, value in data.items():
        if int(key) // l not in dic.keys():
            dic[int(key) // l] = {}
        dic[int(key) // l][key] = value
    for key, value in dic.items():
        name = 'pixiv/' + str(key) + '.json'
        with open(name, 'w') as file:
            json.dump(value, file, sort_keys=True, indent=4)
        Progress('Done on ' + str(key))


def Index():
    file = open('1-NotDanbooru_Result.html', 'r')
    r = input('Range ? ')
    lines = file.readline().split('<br/>')[:-1]
    if 'pximg' not in lines[0]:
        index = [int(ele.split('=')[-1]) for ele in lines]
    else:
        index = [int(ele.split('/')[-1].split('_')[0]) for ele in lines]

    if ':' in r:
        begin, end = r.split(':')
        return index[index.index(int(begin)):index.index(int(end))]
    else:
        return index


def ShowPixiv():
    n = int(input('Proxy number ? '))
    if not n:
        m = input('import url from file ? (y/n) : ')
    else:
        m = False
    if m != 'y':
        if n:
            SetProxy(n)
        urls = Routeur123(mode=3, data=Index())
        file = open('2-directlink.html', 'w')
        for url in urls:
            file.write(url)
    else:
        urls = [
            'https' +
            url for url in open(
                '2-directlink.html',
                'r').readline().split('https')]
    if not n:
        ShowImgs(Routeur123(mode=2, data=urls[1:]))


def PixivId2Url(i):
    try:
        res1 = illust_detail(i, req_auth=True)
        while 'error' in res1 and 'Rate Limit' == res1['error']['message']:
            time.sleep(60)
            res1 = illust_detail(i, req_auth=True)
        if 'illust' in res1:
            res2 = [dic.image_urls.original for dic in res1.illust.meta_pages]
            if not res2:
                res2 = [res1.illust.meta_single_page.original_image_url]
            res[i] = res2
    except Exception as e:
        print('IndividualUrl - error on :', i, e)


def Url2Data(url):
    res.append(Sample(url))


def ShowImgs(imgs):
    input('Press a key to begin')
    begin = datetime.now()
    print('-----------------------\n--- BEGIN SHOW IMGS ---')
    print('Begin at', begin.strftime('%H:%M'), len(imgs))
    i, l = 0, len(imgs)
    file = open('3-final.html', 'w')
    while imgs:
        img = imgs[0]
        imgs = imgs[1:]
        img.InputTags()
        if img._adds == 'y':
            file.write('<A HREF="' + img._url + '"> ' + img._url + '<br/>')
        elif img._adds == 'exit':
            break
        i += 1
        ending = ((datetime.now() - begin) / i * l + begin).strftime('%H:%M')
        s = str(i) + '/' + str(l) + ' | ' + ending + \
            ' | ' + img._url.split('/')[-1]
        Progress(s)
    print()
    print('-----------------------')


def IndividualIQDB(url, mode):
    global file
    global find
    if mode == 4:
        link = YanUrl2Sample(url)
    else:
        link = url
    try:
        if not IQDBreq(link, to_append=url):
            find += 1
            file.write('<A HREF="' + url + '"> ' + url + '<br/>')
    except Exception as e:
        print(e)


def IQDBreq(url_sample, to_append=False):
    global file
    global links
    try:
        if 'yande.re' in url_sample:
            url_sample = '/'.join(url_sample.split('/')[:-1]) + '/yande.re' + url_sample[-4:]
        url = 'http://danbooru.iqdb.org/?url=' + url_sample
        page = urllib.request.urlopen(url)
        strpage = page.read().decode('utf-8')
    except Exception as e:
        links.append(to_append)
        return True
    if 'Best match' in strpage and page.getcode() == 200:
        return True
    else:
        return False


def YanTags2Urls(tags, limit, tag_add):
    tags = tags.split(' ')
    urls = []
    for tag in tags:
        i = 1
        if len(tag) < 3:
            continue
        print(tag, len(urls))
        tag = tag + "+" + tag_add  # Add a tag for all search
        while i <= int(limit / 1000) + 1:
            # do it for each page
            url = 'https://yande.re/post?page=' + str(i)
            url = url + '&tags=' + tag + '+limit%3A' + str(limit)
            page = urllib.request.urlopen(url)
            soup = BeautifulSoup.BeautifulSoup(page, "lxml")
            temp = soup.find_all("span", class_="plid")
            if len(temp) == 0:
                break
            for turl in temp:
                turl = turl.get_text()[3:]
                if turl not in urls:
                    urls.append(turl)
            Progress(str(i) + '/' + str(limit // 1000 + 1))
            i = i + 1
    print()
    return urls


def YanUrl2Sample(url_yan):
    ok = False
    while not ok:
        try:
            page = urllib.request.urlopen(url_yan)
            ok = True
            soup = BeautifulSoup.BeautifulSoup(page, "lxml")
            url = soup.find('meta', {"property": 'og:image'}).get('content')
        except Exception as e:
            print(e)
    return url

def GetPixApi(id_mail, mails, password):
    id_mail = (id_mail+1)%len(mails)
    api = AppPixivAPI()
    api.login(mails[id_mail], password)
    return api, id_mail, api.illust_detail

def Routeur123(mode=0, data=None):
    global file, res, illust_detail
    index = data
    res = []
    if mode == 0:
        print('--------------------------\n--- BEGIN JSON WRITING ---')
        global score
        score = int(input('Minimum score? '))
        ran = input('Range? ').split()
        index = []
        for ele in ran:
            x, y = ele.split(':')
            index += list(range(int(x), int(y)))
        res = {}
    elif mode == 1:
        print('--------------------------\n--- BEGIN CHECK ON DAN ---')
        file = open('1-NotDanbooru_Result.html', 'w')
        data.sort()
        index = data
    elif mode == 2:
        print('--------------------------\n------ DOWNLOAD IMG ------')
    elif mode == 3:
        print('--------------------------\n---- PIXIV ID TO URL -----')
        res = {}
    limit = len(index)
    limit_active = int(input('Number of threads ? ')) + \
        threading.active_count()
    function = [AddEntry, CheckOnDan, Url2Data, PixivId2Url][mode]
    begin = datetime.now()
    if mode in [0, 3]:
        with open("../Pixiv_Codes.txt", 'r') as f:
            mails = f.readline().split()[1:]
            password = f.readline().split()[1]
        lastLogin = begin
        id_mail = -1
        n = -1
    print('Begin at', begin.strftime('%H:%M'))
    p = 0.0
    try:
        for i, x in enumerate(index):
            m = 0
            while threading.active_count() > limit_active:
                time.sleep(0.1)
                m += 1
                if m == 50 and mode in [0, 3]:
                    # Can stop because of proxy, or because of rate limit
                    test = illust_detail(i, req_auth=True)
                    if 'error' in test and test['error']['message'] == 'Rate Limit':
                        api, id_mail, illust_detail = GetPixApi(id_mail, mails, password)
                        n = 0
                        #print('\nSwitch account to', mails[id_mail])
                        time.sleep(20)
                    else:
                        pass
                        #print('\nWill proced to change the proxy')
                        #SetProxy(TestProxy())
            if mode in [0,3]:
                n+= 1
                if not n%800:
                    api, id_mail, illust_detail = GetPixApi(id_mail, mails, password)
                elif (datetime.now() - lastLogin).seconds > 3590:
                    lastLogin = datetime.now()
                    api, id_mail, illust_detail = GetPixApi(id_mail, mails, password)
                    n = 0
            Thread(target=function, args=(x, )).start()
            if p != int(i / limit * 10000) / 100:
                mean_time = (datetime.now() - begin) / (i + 1)
                ending = (mean_time * limit + begin).strftime('%D-%H:%M')
                Progress(str(p) + '% | ' + ending + ' | ' + str(mean_time))
                p = int(i / limit * 10000) / 100
        time.sleep(10)
    except Exception as e:
        print('\n',mails[id_mail], e, 'Stop at', i,'\n--------------------------')
    finally:
        if mode in [0, 1]:
            if not mode and res:
                name = 'pixiv/temp' + str((index[0]) // 1000000) + '.json'
                temp = res
                with open(name, 'w') as file:
                    json.dump(temp, file, sort_keys=True, indent=4)
            file.close()
        elif mode == 3:
            rt = res
            res = []
            for value in rt.values():
                for url in value:
                    res.append(url)
            res.sort()
            print('\nFOUND:', len(res),'\n--------------------------')
            return res
        elif mode == 2:
            print('\nFOUND:', len(res),'\n--------------------------')
            return res
        print('\nFOUND:', len(res),'\n--------------------------')


def Routeur456(mode):
    global file
    global find
    global links
    nb, k, i, find, ts = 24, 0, 0, 0, []
    file = open('1-NotDanbooru_Result.html', 'w')
    if mode == 4:
        tags = input("Write some tags (split search with blanck): ")
        tag_add = input("Perhaps a tag for all searchs ? ")
        limit = int(input("Choose a limit: "))
        links = YanTags2Urls(tags, limit, tag_add)
        print("The number of url is :", len(links))
    elif mode == 5:
        links = open('3-final.html', 'r').readlines()[0].split('<br/>')
        links = [link.split('"')[1] for link in links[:-1]]
    elif mode == 6:
        links = open('2-directlink.html', 'r').readline().split('https')
        links = ['https' + link for link in links]
    try:
        begin = datetime.now()
        l = len(links)
        while i < int(l / nb) + 1:
            l = len(links)
            time.sleep(2)
            renew_tor()
            time.sleep(2)
            for j in range(nb):
                if k < l - 1:
                    k += 1
                    ts.append(Thread(target=IndividualIQDB,
                                     args=(links[k], mode)))
                    ts[-1].start()
            [t.join() for t in ts]
            ending = (datetime.now() - begin) / k * l + begin
            Progress(str(k) + ' on ' + str(l) + ' | ' +
                     ending.strftime('%H:%M') + ' | ' + str(find))
            i += 1
    except Exception as e:
        print(e)
    print()
    print('MEAN TIME:', (datetime.now() - begin) / len(links))
    file.close()

def SplitDirectLink():
    nb = int(input('Number of url in each file ? '))
    links = open('2-directlink.html', 'r').readline().split('https')
    links = ['https' + link for link in links]
    nbFile = len(links)//nb+1
    for i in range(nbFile):
        with open('2-directlink'+str(i)+'.html', 'w') as file:
            for j in range(nb):
                if i*nb+j+1 > len(links):
                    break
                file.write(links[i*nb+j])
    print(nbFile, 'files created')

if __name__ == '__main__':
    print('mode 0 : Go to pixiv and write a .json')
    print('mode 1 : Read .json and check on dan')
    print('mode 2 : Split .json')
    print('mode 3 : Show images')
    print('mode 4 : Check Yandere')
    print('mode 5 : Check from 3-final')
    print('mode 6 : Check from 2-directlink')
    print('mode 7 : split 2-directlink')
    mode = int(input('Which mode ? '))
    if mode in [1, 2]:
        files = input('File numbers ? ')
        if ':' in files:
            r = files.split(':')
            files = [str(x) for x in list(range(int(r[0]), int(r[1])+1))]
        else:
            files = files.split()
    if mode == 0:
        n = int(input('Proxy number ? '))
        if n:
            SetProxy(n)
        Routeur123(mode=0)
    elif mode == 1:
        JsonReading(files)
    elif mode == 2:
        JsonSpliting(files)
    elif mode == 3:
        ShowPixiv()
    elif mode in [4, 5, 6]:
        Routeur456(mode)
    elif mode == 7:
        SplitDirectLink()