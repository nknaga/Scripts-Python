# -*- coding: utf-8 -*-
"""
    Author: Rignak
    Python version: 3.5
"""
from datetime import datetime
import bs4 as BeautifulSoup
from threading import Thread
import browsercookie
cj = browsercookie.chrome()
import requests
import threading
import time
import json
import os
from os.path import join
#from pixivpy3 import AppPixivAPI
from io import BytesIO
from PIL import Image
import urllib
from lib.progress import Progress
from lib.Proxy import renew_tor
import io
import re

with open("../Danbooru_Codes.txt", 'r') as f:
    api_key = f.readline().split()[1]
    dan_username = f.readline().split()[1]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
api_url = 'http://danbooru.donmai.us/posts.json'
prefix = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
global score
score = 0

class Sample:
    """Depict a sample with:
    - the Id of the image on pixiv (an str(int))
    - the data of the image (BytesIO(urllib.request.urlopen))
    - the tags corresponding to the image (a str)"""

    def __init__(self, url):
        ok = 0
        self._url = url
        self._adds = ''
        self._data = None
        while ok <7 :
            try:
                req = urllib.request.Request(url)
                req.add_header('Referer', 'https://www.pixiv.net/')
                self._data = BytesIO(urllib.request.urlopen(req).read())
                ok = 7
            except Exception as e:
                print("\nSample init - error on", self._url, e)
                ok+=1


def GetInfo(index, pages = False):
    global res
    retry = 0
    while retry < 4:
        try:
            url = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id="+str(index)
            page = urllib.request.urlopen(url)
            code = page.getcode()
            if code in [403, 404]:
                return []
            elif code != 200:
                retry += 1
                continue
            else:
                retry = 4
            soup = BeautifulSoup.BeautifulSoup(page, "lxml")
            tags = soup.find("meta", {'name':"keywords"}).get('content').split(',')

            if pages:
                pages = [img.get('src') for img in soup.find_all('img') if \
                        'master' in img.get('src') and not 'square' in img.get('src')]
                if 'R-18'in tags:
                    page = requests.get(url, cookies=cj)
                    soup = BeautifulSoup.BeautifulSoup(page.content, "lxml")
                    pages = [soup.find_all('script')[-3].\
                             text.split('"regular"')[1].split('"')[1].replace("\/", "/")]
                else:
                    pages_bis = GetPagesMode0(index)
                    if len(pages_bis) > 1:
                        pages = pages_bis
                pages = list(set(pages))
                return pages

            user = soup.find('div', {'class':'usericon'})
            user = user.find('a').get('href').split('=')[-1]
            tags.append(user[:-2])
            total_bookmarks = soup.find_all('li', {'class':'info'})[1]
            total_bookmarks = int(total_bookmarks.find_all('span')[-1].text)

            if total_bookmarks > score:
                res[index] = {'t':tags, 's':total_bookmarks}
            return
        except Exception:
            retry+=1
    return []

def FinalJPGorPNG():
    with open('3-final.html', 'r') as file:
        lines = file.readlines()
        urls = lines[0].split('<br/>')
        urls = [link.split('"')[1] for link in urls[:-1]]
        if not urls and lines:
            urls = lines
    pages = []
    for url in urls:
        if url is None:
            continue
        elif '600x600' in url:
            url = url.replace('c/600x600/img-master', 'img-original').replace('_master1200', '')
        elif 'img-master' in url:
            url = url.replace('img-master', 'img-original').replace('_master1200.jpg', '.jpg')
        if url not in pages:
            pages.append(url)

    begin = datetime.now()
    l = len(pages)
    for i, url in enumerate(pages):
        try:
            req = urllib.request.Request(url)
            req.add_header('Referer', 'https://www.pixiv.net/')
            urllib.request.urlopen(req)
        except Exception:
            pages[i] = url.replace('.jpg', '.png')

        ending = ((datetime.now() - begin) / (i+1) * l + begin).strftime('%H:%M')
        Progress(f"{i+1}/{l} | {ending}")
    with open('3-final.html', 'w') as file:
        for url in pages:
            file.write('<A HREF="' + url + '"> ' + url + '<br/>')

def GetPagesMode0(index):
    retry = 0
    while retry < 4:
        try:
            url = "https://www.pixiv.net/member_illust.php?mode=manga&illust_id="+str(index)
            page = urllib.request.urlopen(url)
            code = page.getcode()
            if code in [403, 404]:
                return []
            elif code != 200:
                retry += 1
            elif code == 200:
                retry = 7
            soup = BeautifulSoup.BeautifulSoup(page, "lxml")
            pages = [img.get('data-src') for img in soup.find_all('img')]
            return pages
        except Exception:
            retry += 1
    return []

def GetPagesMode1(index):
    global res
    res.append(GetInfo(index, pages = True))

def CheckOnDan(pixivId):
    if False:
        return True
    else:
        global file
        url = prefix + str(pixivId)
        res.append(pixivId)
        file.write('<A HREF="' + url + '"> ' + url + '<br/>')
        return False


def GetHierarch():
    with io.open("hierarch.txt", 'r', encoding='utf8') as f:
        lines = f.readlines()[1:]

    cor = {}
    hierarch = {}
    for line in lines:
        line= line[:-1]
        tagsHierarch = '\t'.join(line.split('\t'))
        tagsHierarch = [word for word in tagsHierarch.split() if word]
        if tagsHierarch:
            if not line.startswith('\t'):
                copy = tagsHierarch[-1].lower()
            for tag in tagsHierarch:
                hierarch[tag] = copy

        tagsCor = ' '.join(line.split('\t'))
        tagsCor = [word for word in tagsCor.split() if word]
        for tag in tagsCor:
            cor[tag] = copy
    return hierarch, cor


def JsonReading():
    r = input("score range ? ")
    if ':' in r:
        scm, scM = r.split(':')
    elif r:
        scm, scM = r, 99999999
    else:
        scm, scM = 0, 99999999
    lotFiles = input('files number ? ').split("|")  # ex: 0:697|698
    for i, files in enumerate(lotFiles):
        if ':' in files:
            r = files.split(':')
            lotFiles[i] = [str(x) for x in list(range(int(r[0]), int(r[1])+1))]
        else:
            lotFiles[i] = files.split()
    with io.open("blacklist.txt", 'r', encoding='utf8') as f:
        blacklist = []
        for line in f:
            blacklist.append(line[:-1])
    lotTag = input('tags? ').split('|')

    tag_f = input('Enforce tags? : ').split()
    tag_rem = input("Tags to blacklist ? ")
    hierarch, cor = GetHierarch()
    hierarchIm = {k:[] for k in cor.values()}
    for tag in tag_rem.split():
        blacklist.append(tag)
    print('----------------------------\n---- BEGIN JSON READING ----')
    for files, tags_user in zip(lotFiles, lotTag):
        score = [int(scm), int(scM), tags_user]
        scm, scM, tags = score
        tags = set(tags.split())
        for j, file in enumerate(files):
            Progress("read : " + str(j) + '/' + str(len(files)))
            with open('pixiv/' + file + '.json', 'r') as file:
                temp = json.load(file)
            for i, v in temp.items():
                i, s, t = int(i), v['s'], v['t']
                if (s > scm and s < scM) \
                and (not tag_f or any(tag in t for tag in tag_f))\
                and (not any(tag in t for tag in blacklist))\
                and (not tags or any(tag in t for tag in tags)):
                    for tag in tags.intersection(set(t)):
                        try:
                            a = hierarch[tag]
                            hierarchIm[a].append(i)
                        except Exception as e:
                            print(e,tag)
    data = []
    print()
    for k,l in sorted(hierarchIm.items()):
        if l:
            print(k, ':', len(l))
            for i in l:
                data.append(i)
    seen = {}
    data = [seen.setdefault(x, x) for x in data if x not in seen]
    print('----------------------------')
    print('total:', len(data))
    if input('Continue to extract urls ? (y/n) : ') == 'y':
        ShowPixiv(data=data)


def JsonSpliting(files):
    l = 100000
    data = {}
    dic = {}
    for filename in files:
        with open(join('pixiv',filename + '.json'), 'r') as file:
            data.update(json.load(file))
        Progress('Load ' + str(filename))
    for key, value in data.items():
        if int(key) // l not in dic.keys():
            dic[int(key) // l] = {}
        dic[int(key) // l][key] = value
    print()
    for key, value in dic.items():
        name = join('pixiv', 'new',str(key) + '.json')
        with open(name, 'w') as file:
            json.dump(value, file, sort_keys=True, indent=4)
        Progress('Done on ' + str(key))


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


def ShowPixiv(data=[]):
    if data:
        urls = Routeur123(mode=3, data=data)
        with open('2-directlink.html', 'w') as file:
            for url in urls:
                file.write(url)
    else:
        with open('2-directlink.html', 'r') as file:
            urls = ['https' +url for url in file.readline().split('https')][1:]

    if input('Check with IQDB ? (y/n) : ') =='y':
        Routeur456(mode=6, linked=urls)
    with open('1-NotDanbooru_Result.html', 'r') as file:
        urls = [url for url in  file.readline().split('"') if url.startswith('http')]

    print(len(urls), 'imgs found')
    imgs = Routeur123(mode=2, data=urls)
    if input('\nCheck if manga ? (y/n) : ') == 'y':
        imgs = IsManga(imgs)
    ShowImgs(imgs)
    FinalJPGorPNG()

def IsManga(imgs):
    finalImgs = []
    import os
    if not os.path.exists('manga'):
        os.makedirs('manga')
    os.environ['TF_CPP_MIN_VLOG_LEVEL'] = '3'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    import numpy as np
    from keras.preprocessing import image as image_utils
    from keras.models import load_model
    model = load_model('flatCat.h5')
    from keras import backend as K
    K.image_dim_ordering()

    begin = datetime.now()
    l = len(imgs)
    size = (150, 150)
    for i,img in enumerate(imgs):
        if not img._data:
            continue
        tempImg = Image.open(img._data)
        tempImg.thumbnail(size)
        x, y = tempImg.size
        newIm = Image.new('RGB', size, (0,0,0))
        newIm.paste(tempImg, (int((size[0] - x)/2), int((size[1] - y)/2)))
        x = image_utils.img_to_array(newIm)
        x = np.expand_dims(x, axis=0)

        preds = model.predict(x)[0]
        if np.argmax(preds)==1:
            finalImgs.append(img)
        else:
            tempImg.save(join('discarded', str(i)+'.jpg'), 'JPEG')


        ending = (datetime.now() - begin) / (i+1) * l + begin
        Progress(f"{i+1} on {l} |  {ending.strftime('%H:%M')}")
    print('\nOut of', str(l)+',', len(finalImgs),'were illustrations')
    return finalImgs


def Url2Data(url):
    res.append(Sample(url))


def ShowImgs(imgs):
    files = []
    imgs = [img for img in imgs if img._data]
    save = {}
    for j,  img in enumerate(imgs):
        filename = join('res', f"{j}.jpg")
        tempImg = Image.open(img._data)
        tempImg.save(filename, 'JPEG')
        files.append(filename)
        save[filename] = img._url
    with open('save.json', 'w') as file:
        json.dump(save, file, sort_keys=True, indent=4)
    input('Press a key to begin')
    begin = datetime.now()
    print('-----------------------\n--- BEGIN SHOW IMGS ---')
    print('Begin at', begin.strftime('%H:%M'), len(imgs))
    ShowFromLocal()
    print('-----------------------')

def IQDBFromLocal():
    with open('save.json', 'r') as file:
        save = json.load(file)
    imgs = os.listdir('res')
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    imgs =  sorted(imgs, key = alphanum_key)

    urls = [save[join('res', file)] for file in imgs]
    Routeur456(mode=6, linked=urls)

    with open('1-NotDanbooru_Result.html', 'r') as file:
        urls = [url for url in  file.readline().split('"') if url.startswith('http')]
    print(len(urls), 'imgs found')
    imgs = Routeur123(mode=2, data=urls)


def ShowFromLocal():
    with open('save.json', 'r') as file:
        save = json.load(file)
    imgs = os.listdir('res')
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    imgs =  sorted(imgs, key = alphanum_key)

    ids = []
    sameIds = {}
    for filename in imgs:
        filename = join('res', filename)
        url = save[filename]
        if 'pximg' in  url:
            id_, page = url.split('/')[-1].split('_')[:2]
            try:
                page = int(page[1:])
            except:
                page = 0
            if id_ in ids:
                sameIds[id_].append((page, filename))
            else:
                sameIds[id_] = [(page, filename)]
                ids.append(id_)
        else:
            sameIds[url] = [('', filename)]
            ids.append(url)
    for key, value in sameIds.items():
        sameIds[key] = [e2 for e1, e2 in sorted(value)]

    i, l, t = 0, len(imgs),0
    begin = datetime.now()
    exit_ = False
    with open('3-final.html', 'w') as file:
        for id_ in ids:
            for filename in sameIds[id_]:
                url = save[filename]
                add = ''
                try:
                    os.system(f'"{filename}"')
                except BaseException as e:
                    add = 'pass'
                    print(e)
                while add == '':
                    add = input('tags ? ')
                splitedName = os.path.splitext(filename)
                os.rename(filename, splitedName[0]+'_done'+splitedName[1])
                if add == 'y':
                    t+=1
                    file.write(f'<A HREF="{url}">{url}<br/>')
                elif add == 'exit':
                    exit_ = True
                    break
                ending = ((datetime.now() - begin) / (i+1) * l + begin).strftime('%H:%M')
                Progress(f"{i}/{str(l)} | {ending} | {url.split('/')[-1]} | {t}")
                i += 1
            if exit_:
                break

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
            file.write(f'<A HREF="{url}">{url}<br/>')
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
    except Exception:
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


def ShowYandere():
    links = open('1-NotDanbooru_Result.html', 'r').readline().split('<')

    links = [link.replace('"', '').replace('>', '') for sublinks in links \
    if len(sublinks.split())>1 for link in sublinks.split() if link.startswith('https')]

    finalLinks = []
    for link in links:
        if link not in finalLinks:
            finalLinks.append(link)

    samples = []
    begin = datetime.now()
    for i, link in enumerate(finalLinks):
        url = YanUrl2Sample(link)
        sample = Sample(url)

        req = urllib.request.Request(url)
        sample._data = BytesIO(urllib.request.urlopen(req).read())
        sample._url = link
        samples.append(sample)

        ending = (datetime.now() - begin) / (i+1) * len(finalLinks) + begin
        Progress(f"{i+1} on {len(finalLinks)} | {ending.strftime('%H:%M')}")
    ShowImgs(samples)


def Routeur123(mode=0, data=None):
    global file, res, illust_detail
    index = data
    res = []
    global score
    if mode == 0:
        print('--------------------------\n--- BEGIN JSON WRITING ---')
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
    elif mode == 2:
        print('--------------------------\n------ DOWNLOAD IMG ------')
    elif mode == 3:
        print('--------------------------\n---- PIXIV ID TO URL -----')
        score = 0
    limit = len(index)
    limit_active = int(input('Number of threads ? ')) + \
        threading.active_count()
    function = [GetInfo, CheckOnDan, Url2Data, GetPagesMode1][mode]
    begin = datetime.now()
    print('Begin at', begin.strftime('%H:%M'))
    p = 0.0
    try:
        for i, x in enumerate(index):
            while threading.active_count() > limit_active:
                time.sleep(0.01)
            Thread(target=function, args=(x, )).start()
            if p != int(i / limit * 1000):
                mean_time = (datetime.now() - begin) / (i + 1)
                ending = (mean_time * limit + begin).strftime('%D-%H:%M')
                Progress(f"{p/10}% | {ending} | {mean_time}")
                p = int(i / limit * 1000)
        time.sleep(10)
    except Exception as e:
        print('\n', e)
    finally:
        if mode in [0, 1]:
            if not mode and res:
                name = 'pixiv/temp' + str((index[0]) // 100000) + '.json'
                temp = res
                with open(name, 'w') as file:
                    json.dump(temp, file, sort_keys=True, indent=4)
            file.close()
        elif mode == 3:
            res2 = []
            for value in res:
                if value is None:
                    continue
                for url in value:
                    if not url is None and url not in res2:
                        res2.append(url)
            print('\nFOUND:', len(res2),'\n--------------------------')
            return res2
        elif mode == 2:
            print('\nFOUND:', len(res),'\n--------------------------')
            return res
        print('\nFOUND:', len(res),'\n--------------------------')

def CheckTweet():
    tweetBase = "https://pbs.twimg.com/media/"
    urlDic = {}
    for file in os.listdir("res"):
        usr = file.split()[0]
        twiId = file.split()[1]
        imgUrl = tweetBase + file.split()[-1]
        twiUrl = f"https://twitter.com/{usr}/status/{twiId}"
        urlDic[imgUrl] = twiUrl
    Routeur456(10, linked=twiUrl.keys())
    with open('1-NotDanbooru_Result.html', 'r') as file:
        lines = file.readline().split('"')
        for line in lines:
            if line in urlDic:
                print(urlDic[line])

def Routeur456(mode, linked=[]):
    global file
    global find
    global links
    links = linked
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
        if not links:
            links = open('2-directlink.html', 'r').readline().split('https')
            links = ['https' + link for link in links]
    try:
        begin = datetime.now()
        l = len(links)
        while i < int(l / nb) + 1:
            l = len(links)
            time.sleep(1.5)
            renew_tor()
            time.sleep(1.5)
            for j in range(nb):
                if k < l:
                    ts.append(Thread(target=IndividualIQDB,
                                     args=(links[k], mode)))
                    k += 1
                    ts[-1].start()
            [t.join() for t in ts]
            ending = (datetime.now() - begin) / k * l + begin
            Progress(f"{k} on {l} | {ending.strftime('%H:%M')} | {find}")
            i += 1
    except Exception as e:
        print(e)
    time.sleep(20)
    print()
    print('MEAN TIME:', (datetime.now() - begin) / len(links))
    file.close()


if __name__ == '__main__':
    print('mode 0 : Go to pixiv and write a .json')
    print('mode 1 : Read .json and check on dan')
    print('mode 2 : Split .json')
    print('mode 3 : Show images')
    print('mode 4 : Check Yandere')
    print('mode 5 : Check from 3-final')
    print('mode 6 : Check from 2-directlink')
    print('mode 7 : split 2-directlink')
    print('mode 8 : Show images from yandere')
    print('mode 9 : png or jpg on 3-final')
    print('mode 10 : check from saved tweets')
    print('mode 11 : show local images')
    print('mode 12 : IQDB from local')
    mode = int(input('Which mode ? '))
    if mode == 0:
#        n = int(input('Proxy number ? '))
#        if n:
#            SetProxy(n)
        Routeur123(mode=0)
    elif mode == 1:
        JsonReading()
    elif mode == 2:
        files = input('File numbers ? ')
        if ':' in files:
            r = files.split(':')
            files = [str(x) for x in list(range(int(r[0]), int(r[1])+1))]
        else:
            files = files.split()
        JsonSpliting(files)
    elif mode == 3:
        ShowPixiv()
    elif mode in [4, 5, 6]:
        Routeur456(mode)
    elif mode == 7:
        SplitDirectLink()
    elif mode == 8:
        ShowYandere()
    elif mode == 9:
        FinalJPGorPNG()
    elif mode == 10:
        CheckTweet()
    elif mode == 11:
        ShowFromLocal()
        FinalJPGorPNG()
    elif mode == 12:
        IQDBFromLocal()