# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 11:27:34 2017

@author: Rignak
"""

from urllib.request import urlopen
import bs4
import json
import matplotlib.pyplot as plt

def UserListCompleted(username):
    url = 'https://myanimelist.net/animelist/' + username + '?status=2'
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

def CountYear(dic, years):
    nbs = []
    for year in years:
        nb = 0
        for key, value in dic.items():
            if not 'Aired:' in value or not value['Aired:']:
                continue
            if 'Aired:' in value and value['Aired:'][0].split('/')[-1] == '?':
                continue
            try:
                if 'Aired:' in value and int(value['Aired:'][0].split('/')[-1])==year:
                    nb+=1
            except:
                pass
                #print('error:', value['Aired:'])
        nbs.append(nb)
    return nbs

def GetData():
    years = range(1970, 2018)
    data0 = LoadDic()
    nbs_total = CountYear(data0, years)
    print('You can choose conditions from :\n', '\n'.join(list(data0['1'].keys())))

    conditions = input("Conditions (split on '&') ? ")
    if conditions:
        conditions = [c.split(':') for c in conditions.split('&')]
        nbs_all = CountYear(ReduceOnConditions(data0, conditions), years)

        mode = input('Result in nb or in % ? ')
        if mode == '%':
            ylabel = '%'
            p_all = GetProportion(nbs_all,nbs_total)
            data = [p_all]
        else:
            ylabel = 'nb'
            data = [nbs_all]
        legend = ['all']

        username = input('Username ? ')
        if username:
            data_user = ReduceDic(data0, UserListCompleted('Rignak'))
            nbs_user = CountYear(ReduceOnConditions(data_user, conditions), years)

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
    Plt(years, data, legend, ylabel)

def GetProportion(l1, l2):
    p = []
    for i in range(len(l2)):
        if l2[i]:
            p.append(l1[i]/l2[i]*100)
        else:
            p.append(0)
    return p

def Plt(x, data, legend, ylabel):
    fig, ax1 = plt.subplots()
    for y in data:
        ax1.plot(x, y)
    ax1.set_xlabel('Years')
    ax1.set_ylabel(ylabel)
    plt.legend(legend, loc="best")

if __name__ == '__main__':
    GetData()