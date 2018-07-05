# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 11:29:34 2018

@author: Rignak
"""


from datetime import datetime
import urllib
import bs4 as BeautifulSoup
import re
from sys import stdout
import json

class Anime:
    
    def __init__(self, name):
        self.name = name
        self.sales = {}
        self.total = 0
        
    def ComputeTotal(self):
        self.total = 0
        for v in self.sales.values():
            self.total += v
        return self.total
        
    def AddSales(self, sales, item):
        sales = sales.replace(',', '').replace('*', '')
        if item not in self.sales or self.sales[item] < int(sales):
            try:
                self.sales[item] = int(sales)
            except:
                pass
            
    def __lt__(self, anime2):
        return self.total > anime2.total

def Progress(s):
    stdout.write('\r')
    stdout.write(s+'            ')
    stdout.flush()


def OnlyText(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True    

def GetSoup(url):
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup.BeautifulSoup(page, "lxml")
    return soup


def GetRanking(soup):
    data = soup.findAll(text=True)
    result = list(filter(OnlyText,data))
    
    while result:
        ele = result[0].replace('\r', '').replace('\n', '')
        if not (ele.startswith('1.') or ele.startswith('*1.')):
            result.pop(0)
        else:
            break
        
    k = 1
    for i, ele in enumerate(result):
        if i == 0:
            lst = []
        if i == 0 or ele.startswith('\r\n'):
            lst.append(ele.split())
            if i > 1 and lst[-1][0] == '(cut-off':
                lst.append([])
        else:
            lst[-1].append(ele.replace('\n', ''))
            if i> 2 and lst[-2][0] == '(cut-off' and len(lst[-1])>2 :
                lst[-1] = lst[-1][-3].split() + lst[-1][-2:]
                k+=1
    lst = [ele for ele in lst if len(ele) in [4, 5]]
    
    previousRank = 0
    i = 0
    for ele in lst:
        types = ['BD', 'DVD']
        rank=int(ele[0].replace('*', '').replace('.', ''))
        if rank < previousRank:
            i += 1
            if i == 2:
                break
        if len(ele) == 4:
            ele.append(types[i])
        else:
            ele[-1]+=(' '+types[i])
        if ele[-1].startswith(' '):
            ele[-1]=ele[-1][1:]
        previousRank=rank
    return lst

def GetPreviousWeek(soup):
    for a in soup.findAll('a'):
        if 'Previous Week' in a.text:
            return a['href']
    return ''
    
def OnOneNews(url, animes):
    soup = GetSoup(url)
    
    for div in soup.findAll('div', {"class": "text word-break pl8 pr8"}):
        div.decompose()
    try:
        lst = GetRanking(soup)
    except Exception as e:
        print(e, url)
        return 'error', animes
    for anime in lst:
        if anime[3] not in animes:
            animes[anime[3]] = Anime(anime[3])
        if len(anime)== 5:
            animes[anime[3]].AddSales(anime[2], anime[4])
    GetPreviousWeek(soup)
    
    return GetPreviousWeek(soup), animes
    
def GetUrls(p=1):
    url = 'https://myanimelist.net/news/tag/anime_sales?p='+str(p)
    soup = GetSoup(url)
    urls = []
    for a in soup.findAll('a'):
        if "Japan's Weekly Blu-ray" in a.text:
            urls.append(a['href'])
    return urls
    
def main():
    url = "https://myanimelist.net/news/55319411"
    animes = {}
    
    urls = []
    print('Retrieve news urls')
    for i in range(1,13):
        Progress(str(i)+'/'+'12')
        urls += GetUrls(p=i)
    l = len(urls)
        
    begin = datetime.now()
    for i, url in enumerate(urls):
        url, animes = OnOneNews(url, animes)
#        if url not in urls:
#            urls.append(url)
        ending = ((datetime.now() - begin) / (i+1) * l + begin).strftime('%H:%M')
        Progress(str(i+1)+'/'+str(l) + ' | ' + url.split('/')[-1] + ' | ' +ending+\
        ' | ' + str(len(animes)))
    [anime.ComputeTotal() for anime in animes.values()]
    for anime in sorted(list(animes.values())):
        print(anime.name, anime.total)
        
    dic = {anime.name:{'details':anime.sales, 'total':anime.total} for anime in animes.values()}
    with open('sales.json', 'w') as file:
        json.dump(dic, file, sort_keys=True, indent=4)

if __name__ == '__main__':
    main()