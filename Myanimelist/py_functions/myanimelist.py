# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 14:05:09 2017

@author: Rignak
"""

from urllib.request import urlopen
import bs4
import json

def UserList(username, index):
    url = 'https://myanimelist.net/animelist/' + username + '?status='+str(index)
    soup = bs4.BeautifulSoup(urlopen(url).read(), 'lxml')
    fa = soup.find_all('a')
    ids = []
    for a in fa:
        if 'href' in a.attrs.keys() and a.attrs['href'].startswith('/anime/'):
            ids.append(int(a.attrs['href'].split('/anime/')[1].split('/')[0]))
    return ids
    
def LoadDic():
    with open('myanimelist.json', 'r') as file:
        data = json.load(file)
    return data

def ReduceDic(full_dic, ids):
    user_dic = {}
    for key in ids:
        if str(key) in full_dic:
            user_dic[str(key)] = full_dic[str(key)]
    return user_dic

def CheckCondition(entry, c):
    key, value = c
    key += ':'
    if key not in entry:
        return False
    if len(entry[key]) == 1:
        if entry[key] == value:
            return True
        else:
            return False
    elif value in entry[key]:
        return True
    else:
        return False

def ReduceOnConditions(dic, conditions):
    res = {}
    for key, value in dic.items():
        ok = True
        for condition in conditions:
            c = CheckCondition(value, condition)
            if not c:
                ok = False
                break
        if ok:
            res[key] = value
    return res
