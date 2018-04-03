# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 11:27:34 2017

@author: Rignak
"""

import matplotlib.pyplot as plt
from datetime import date
from py_functions.myanimelistf import UserList, LoadDic, ReduceDic, ReduceOnConditions

def CountYear(dic, years, episodes):
    nbs = []
    for year in years:
        nb = 0
        for key, value in dic.items():
            try:
                if 'year' in value and int(value['year'])==year:
                    if episodes:
                        nb+=int(value['episodes'])
                    else:
                        nb+=1
            except Exception as e:
                print(e)
        nbs.append(nb)
    return nbs

def GetData(conditions, username, mode, episodes):
    years = range(1970, date.today().year-1)
    data0 = LoadDic()
    nbs_total = CountYear(data0, years, episodes)
    if conditions:
        conditions = [c.split(':') for c in conditions.split('&')]
        nbs_all = CountYear(ReduceOnConditions(data0, conditions), years, episodes)
        if mode == '%':
            ylabel = '%'
            p_all = GetProportion(nbs_all,nbs_total)
            data = [p_all]
        else:
            ylabel = 'nb'
            data = [nbs_all]
        legend = ['all']

        if username:
            data_user = ReduceDic(data0, UserList(username, 2))
            nbs_user = CountYear(ReduceOnConditions(data_user, conditions), years, episodes)

            if mode == '%':
                p_user = GetProportion(nbs_user,nbs_total)
                p_relatif = GetProportion(nbs_user,nbs_all)
                data += [p_user, p_relatif]
                legend += ['user', 'relatif']
            else:
                data += [nbs_user]
                legend += ['user']
    else:
        ylabel = 'nb'
        data, legend = [nbs_total], ['all']
    Plt(years, data, legend, ylabel, conditions)

def GetProportion(l1, l2):
    p = []
    for i in range(len(l2)):
        if l2[i]:
            p.append(l1[i]/l2[i]*100)
        else:
            p.append(0)
    return p

def Plt(x, data, legend, ylabel, conditions):
    fig, ax1 = plt.subplots()
    for y in data:
        ax1.plot(x, y)
    ax1.set_xlabel('Years')
    ax1.set_ylabel(ylabel)
    plt.legend(legend, loc="best")
    plt.title(conditions)

if __name__ == '__main__':
    data0 = LoadDic()
    print('You can choose conditions from :\n', '\n'.join(list(data0['1'].keys())))
    print("Multiples searches split by '|'")
    print("and conditions applied with &")
    print("Example: genres:Sci-fi&type:TV|genres:Mecha")
    conditions = input("Conditions (split on '&') ? ")
    mode = input('Result in nb or in % ? ')
    username = input('Username ? ')
    episodes = input('Count episode ? (y/n) ') == 'y'
    for condition in conditions.split('|'):
        GetData(condition, username, mode, episodes)