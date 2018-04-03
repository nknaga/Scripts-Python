# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 14:05:09 2017

@author: Rignak
"""

import json
from os import path
from myanimelist import session

def UserList(username, index):
    if path.isfile(path.join('save', username+'.json')):
        with open(path.join('save', username+'.json'), 'r') as file:
            li = json.load(file)
    else:
        li = SaveUser(username)
    res = {}
    for key, dic in li.items():
        if dic['status'] == index:
            res[key] = dic
    return res

def SaveUser(name):
    sess = session.Session()
    userList = {}
    a = sess.anime_list(name).list
    for key, dic in a.items():
        entry = {}
        entry['score'] = dic['score']
        status = dic['status']
        if status == 'Watching':
            entry['status'] = 1
        elif status == 'Completed':
            entry['status'] = 2
        elif status == 'On-Hold':
            entry['status'] = 3
        elif status == 'Dropped':
            entry['status'] = 4
        elif status == 'Plan to Watch':
            entry['status'] = 5
        else:
            print('Error on status:', key.title)
        userList[key.id] = entry
    with open(path.join('save', name+'.json'), 'w') as file:
        json.dump(userList, file, sort_keys=True, indent=4)
    return userList

def LoadDic():
    with open(path.join('save', 'myanimelist.json'), 'r') as file:
        data = json.load(file)
    return data

def ReduceDic(full_dic, userList):
    user_dic = {}
    for key, dic in userList.items():
        if str(key) in full_dic:
            user_dic[str(key)] = full_dic[str(key)]
            if dic['score']:
                user_dic[str(key)]['score'] = dic['score']
            else:
                user_dic[str(key)]['score'] = 0

    return user_dic

def CheckDate(entry, value):
    if value[0] == '<':
        return int(value[1:]) > int(entry)
    else:
        return int(value[1:]) < int(entry)


def CheckCondition(entry, c):
    key, value = c
    if key not in entry:
        return False
    if value[0] in ['<', '>']:
        return CheckDate(entry[key], value)
    if type(entry[key]) in [str, int] and str(entry[key]) == str(value):
        return True
    elif type(entry[key]) == list and value in entry[key]:
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
