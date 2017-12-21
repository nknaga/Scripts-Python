# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 17:34:58 2017

@author: Rignak
"""

from py_functions.myanimelist import UserList, LoadDic, ReduceDic, ReduceOnConditions


def GetData(conditions, username):
    conditions = ['type:TV', conditions+'&type:TV'][conditions!='']
    data0 = LoadDic()
    conditions = [c.split(':') for c in conditions.split('&')]
    ul = UserList(username, 2)
    res = ReduceDic(data0, ul)
    res = ReduceOnConditions(res, conditions)
    order = [id_ for id_ in ul if str(id_) in res.keys()]
    return res, order

conditions = input("Conditions (split on '&') ? ")
username = input('Username ? ')

res, order = GetData(conditions, username)

data = []
for id_ in order:
    dic = res[str(id_)]
    try:
        data.append((dic['begin'][0].split('/')[-1], dic['episodes'], dic['name']))
    except Exception as e:
        print('\nError on:',id_, e, ':', dic, '\n',)
for i, t in enumerate(data):
    prefix = ['', '0'][len(str(i+1)) < 2]
    a, e, n = t
    print(prefix+str(i+1),a,e,n)
