# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 15:08:02 2018

@author: Rignak
"""
import urllib
import requests
import bs4 as BeautifulSoup
from lib.Proxy import renew_tor
from datetime import datetime
import socks
from sys import stdout


with open("../Danbooru_Codes.txt", 'r') as f:
    api_key = f.readline().split()[1]
    dan_username = f.readline().split()[1]
    
    
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}


def Progress(s):
    stdout.write('\r')
    stdout.write(s+'            ')
    stdout.flush()
    
def GetTag(i):
    url = 'http://danbooru.donmai.us/posts/' + i + '.json'
    payload = {'api_key':api_key,
               'login': dan_username}

    req = requests.get(url, data=payload, headers=hdr, stream=True)
    data = req.json()
    return data["tag_string"]
        
def IQDBreq(url):
    try:
        url = 'http://danbooru.iqdb.org/?url=' + url
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup.BeautifulSoup(page, "lxml")
    except Exception as e:
        return 'error'
    return soup
    
def GetRelevent(soup):
    try:
        data = soup.find_all('div')
        for ele in data[1:]:
            s = str(ele)
            if 'Best match' in s:
                return ele
    except:
        pass
    
def ReleventToProx(releventData):
    reduced = []
    try:
        divs = releventData.find_all('div')[1:]
        for div in divs:
            s = str(div)
            index = s.index('% similarity')
            proximity = s[index-2:index]
            if proximity in ['97', '98', '99', '00']:
                reduced.append(div)
        return reduced
    except:
        return []
            
    
def GetStrings(releventData):
    dic = {}
    
    for ele in releventData:
        aS = ele.find_all('a')
        for a in aS:
            index = a.get('href').split('/')[-1]
            s = GetTag(index).split()
            dic[index] = s
    return dic
            
def DifDic(dic):
    totalTags = []
    for tags in [s for s in dic.values()]:
        for tag in tags:
            if tag not in totalTags:
                totalTags.append(tag)
    for key, tags in dic.items():
        dic[key] = [tag for tag in totalTags if tag not in tags]
    return dic
  
def Full1Pic(url):
        
    soup = IQDBreq(url)
    releventData = GetRelevent(soup)
    reduced = ReleventToProx(releventData)
#    
#    dic = GetStrings(reduced)
#    addTags = DifDic(dic)
    return reduced
    
def ListUrl(tags):
    """Make a rqst to danbooru in order to get the data"""
    payload = {'limit ': 100, 'tags' : tags,
               'api_key':api_key,
               'login': dan_username}
    req = requests.get('https://danbooru.donmai.us/posts.json',
                        data=payload, headers=hdr, stream=True)
    data = req.json()
    return data
    
def ListId():
    inf = 1000000
    sup = 3000000
    tags = "child:any score:>50 order:id id:>"
    limit = 2000
    data = []
    for i in range((limit-1)//100+1):
        print('Searching for picts:', i+1, 'on', (limit-1)//100+1, '|', inf)
        data += ListUrl(tags+str(inf))
        if inf == data[-1]['id']:
            break
        inf = data[-1]['id']
        if inf>sup:
            break
    for i in range(len(data)):
        data[i] = (data[i]['id'], data[i]['large_file_url'])
    return data

def GetAddTags():
    data = ListId()
    addTags = {}
    j = 1
    print('STEP1')
    begin1 = datetime.now()    
    data = data
    for i, url in data:
        if not (j-1)%24:
            renew_tor()
        res = Full1Pic(url)
        if len(res)>1:
            addTags[i] = res
        ETA = (datetime.now()-begin1)/j*len(data)+begin1
        Progress(str(j)+'/'+str(len(data))+' | '+ETA.strftime('%H:%M'))
        j+=1
    
    print('\nSTEP2')
    begin2 = datetime.now()    
    socks.set_default_proxy()
    j = 0
    for i in addTags:
        j+=1
        addTags[i] = DifDic(GetStrings(addTags[i]))
        ETA = (datetime.now()-begin2)/j*len(addTags)+begin2
        Progress(str(j)+'/'+str(len(addTags))+' | '+ETA.strftime('%H:%M'))
    print('\nMean time:', (datetime.now()-begin1)/len(data))
    return addTags
    
def MakeHTML(addTags):
    with open("addTags.html", 'w') as f:
        for k1, v1 in addTags.items():
            for k2, v2 in v1.items():
                if k2 in addTags:
                    l = '<A HREF="http://danbooru.donmai.us/posts/'+k2+'">' + ' '.join(v1) + '<br></br> \n'
                    f.write(l)
    
def main(): 
    addTags = GetAddTags()
    MakeHTML(addTags)

if __name__ == '__main__':
    res = main()