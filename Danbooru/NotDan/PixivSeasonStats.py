# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 20:53:27 2018

@author: Rignak
"""


import matplotlib.pyplot as plt
from os.path import join, exists
from os import listdir
import json
from lib.progress import Progress

def convertRequest(request):
    prefix = request.split()[-1]
    if 'winter' in request:
        suffix = '4'
    elif 'spring' in request:
        suffix = '1'
    elif 'summer' in request:
        suffix = '2'
    elif 'fall' in request:
        suffix = '3'
    return prefix + "-" + suffix + ".txt"

def GetRequest(request):
    requests = {}
    with open(join('season', request), "r", encoding="utf-8") as file:
        for line in file.readlines():
            line = line.split()
            if line[1:]:
                requests[line[0]] = line[1:]
    return requests

def Flatten(lst):
    res = []
    for ele in lst:
        if type(ele) == list:
            res += Flatten(ele)
        else:
            res.append(ele)
    return res

def JsonReading(requests):
    res = {key:[] for key in requests.keys()}
    files = [file for file in listdir('pixiv') if file.endswith('.json')]
    t = 0
    for j, file in enumerate(files):
        Progress(f"read : {j}/{len(files)} | {t}")
        with open(join('pixiv',file), 'r') as file:
            temp = json.load(file)
        for i, v in temp.items():
            for key, tags in requests.items():
                if any(tag in v['t'] for tag in tags):
                    res[key].append(int(i))
                    t+=1
    return res
    
def Convert2Histo(response, width):
    print()
    for key, value in response.items():
        print(key, len(value))
    allEntries = Flatten(response.values())
    rangeEntries = min(allEntries)//width*width, (max(allEntries)//width+1)*width
    rangeEntries = range(rangeEntries[0], rangeEntries[1], width)
    res = {}
    for key, values in response.items():
        res[key] = []
        for mini in rangeEntries:
            maxi = mini + width
            res[key].append(len([ele for ele in values if ele < maxi and ele > mini]))
    return res
    
def Plot(response):
    data = Convert2Histo(response, 1000000)
    fig, ax1 = plt.subplots()
    legend = []
    sort = [(sum(y), x) for x, y in data.items()]
    for x, label in sorted(sort, reverse=True):
        ax1.plot(data[label])
        legend.append(label+' : '+str(x))
    ax1.set_xlabel('id')
    ax1.set_ylabel('nb')
    plt.legend(legend, loc="best")

def main():
    request = "spring 2018"
    request = convertRequest(request)
    requests = GetRequest(request)
    response = JsonReading(requests)
    Plot(response)
    

if __name__=="__main__":
    main()
