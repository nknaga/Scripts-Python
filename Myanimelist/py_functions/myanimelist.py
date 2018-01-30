# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 14:05:09 2017

@author: Rignak
"""

from urllib.request import urlopen
import bs4
import json
from os import path

def UserList(username, index):
    if path.isfile(username+str(index)+'.json'):
        with open(username+str(index)+'.json', 'r') as file:
            ids = json.load(file)
    else:
        url = 'https://myanimelist.net/animelist/' + username + '?order=4&status='+str(index)
        soup = bs4.BeautifulSoup(urlopen(url).read(), 'lxml')
        fa = soup.find_all('a')
        ids = []
        for a in fa:
            if 'href' in a.attrs.keys() and a.attrs['href'].startswith('/anime/'):
                ids.append(int(a.attrs['href'].split('/anime/')[1].split('/')[0]))

        with open(username+str(index)+'.json', 'w') as file:
            json.dump(ids, file, sort_keys=True, indent=4)
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

def CheckDate(entry, value):
    date = value[1:]
    is_sup = True
    if int(date[6:10]) < int(entry[6:10]):
        is_sup = False
    elif int(date[6:10]) == int(entry[6:10]):
        if int(date[3:5]) < int(entry[3:5]):
            is_sup = False
        elif int(date[3:5]) == int(entry[3:5]) and int(date[:2]) < int(entry[:2]):
            is_sup = False
    if value[0] == '<':
        return is_sup
    else:
        return not is_sup


def CheckCondition(entry, c):
    key, value = c
    if key not in entry:
        return False
    if value[0] in ['<', '>']:
        return CheckDate(entry[key][0], value)
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