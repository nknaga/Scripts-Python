# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 13:30:06 2017

@author: Rignak
"""
import urllib
import bs4 as BeautifulSoup
from time import sleep
from sys import stdout
from datetime import datetime

def Progress(s):
    stdout.write('\r')
    stdout.write(s+'            ')
    stdout.flush()

def Request(verbs):
    res = []
    global tags
    base = "http://www.dictionnaire-japonais.com/w/"
    begin = datetime.now()
    for i, verb in enumerate(verbs):
        res.append({verb:{}})
        url = base+str(verb)+'/'
        ok = False
        while not ok:
            try:
                page = urllib.request.urlopen(urllib.parse.quote(url.encode('utf8'), ':/'))
                soup = BeautifulSoup.BeautifulSoup(page, "lxml")
                ok = True
                sleep(1)
            except Exception as e:
                print(e)
            break
        for h1 in soup.find_all('h1'):
            if h1.get('class')[0] == 'jp':
                res[i][verb]['kanji'] = h1.text.split(',')[0]
        for h2 in soup.find_all('h2'):
            try:
                if h2.get('class')[0] == 'fr':
                    res[i][verb]['français'] = h2.text.split(',')[0].split(';')[0]
            except:
                pass
        for li in soup.find_all('li'):
            for div in li.find_all('div'):
                if div.get('class')[0] == 'name':
                    key1, key2 = verb, ' '.join(div.text.split())
                    for s in ['未然形 ', '終止形 ', '仮定形 ', 'て形 ',
                              '連用形 ', '連体形 ', '命令形 ', 'た形 ']:
                        key2 = key2.replace(s, '')
                    key2 = key2.replace('fome', 'forme')
                elif div.get('class')[0] == 'verbe':
                    res[i][key1][key2] = div.text.split()[-1]

        p = int((i+1) / len(verbs) * 10000) / 100
        mean_time = (datetime.now() - begin) / (i + 1)
        ending = (mean_time * len(verbs) + begin).strftime('%D-%H:%M')
        Progress(str(p) + '% | ' + ending + ' | ' + str(mean_time))
    return res


if __name__ == '__main__':
    verbs = list(set([168, 155, 292, 618, 1585, 279,287, 1641, 1671, 2765, 1597,
             36983, 291, 742, 1629, 1828, 120, 791, 794, 267, 1556,
             2610, 3398, 281, 288, 7, 1628, 323, 2656, 1565, 4283, 324,
             33288, 868, 148, 3085, 39554, 7313, 17738, 616, 1947,
             1528, 11587, 1570, 122, 120, 1612, 1196, 3595, 501, 121, 123, 1535,
             27132, 290, 3744, 1609, 21961, 120, 2656, 2472, 1576, 5164, 43455,
             6482, 17259, 330, 6680, 2529, 1611, 16842, 294, 8730, 28278, 1570,
             5149, 2924, 6740, 2400, 2269, 2425, 2047, 2405, 8868]))
    keys = ['français', 'kanji', 'affirmatif intemporel poli', 'affirmatif passé poli', 'affirmatif intemporel neutre',
            'affirmatif passé neutre', 'progressif intemporel neutre', 'négatif intemporel poli',
            'négatif passé poli', 'négatif intemporel neutre', 'négatif passé neutre',
            'forme inaccomplie', 'forme terminale', 'forme hypothétique', 'forme en TE',
            'forme conjonctive', 'forme attributive', 'forme impérative', 'forme en TA']
    header = ''
    for i, key in enumerate(keys):
        header += key + '|'
#        if i < 2:
#            header += key + '|'
#        else:
#            header += key + '!|' + key + '|'
    print(header)
    print(len(verbs), 'verbs')
    print()
    r = Request(verbs)
    print()
    for i,dic in enumerate(r):
        verb = verbs[i]
        line = ''
        ok = True
        for i, key in enumerate(keys):
            if key in dic[verb]:
                line += dic[verb][key] + '|'
            else:
                ok = False
        if ok:
            print(line)