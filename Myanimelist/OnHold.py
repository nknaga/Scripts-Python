# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 14:03:51 2017

@author: Rignak
"""

from py_functions.myanimelistf import UserList, LoadDic, ReduceDic, ReduceOnConditions
import random

def GetData(conditions, username):
    conditions = ['type:TV', conditions+'&type:TV'][conditions!='']
    data0 = LoadDic()
    conditions = [c.split(':') for c in conditions.split('&')]
    res = ReduceDic(data0, UserList(username, 3))
    return ReduceOnConditions(res, conditions)


if __name__ == '__main__':
    data0 = LoadDic()
    print('You can choose conditions from :', '\n'+'\n'.join(list(data0['1'].keys())))
    print("Multiples searches split by '|'")
    print("and conditions applied with &")
    print("Example: genres:Sci-fi&Type:TV|genres:Mecha")
    conditions = input("Conditions (split on '&') ? ")
    username = input('Username ? ')
    res = {}
    for condition in conditions.split('|'):
        res.update(GetData(condition, username))
    data = []
    for id_, dic in res.items():
        try:
            data.append((dic['year'], dic['episodes'], dic['title']))
        except Exception as e:
            print('\nError on:',id_, e, ':', dic, '\n',)
    random.shuffle(data)
    for i, t in enumerate(data):
        prefix = ['', '0'][len(str(i+1)) < 2]
        y, e, n = t
        print(prefix+str(i+1),y,e,n)
