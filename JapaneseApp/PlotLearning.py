# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 23:25:51 2018

@author: Rignak
"""


import matplotlib.pyplot as plt
import codecs

def PlotLearning(timeline):
    delta = [-0.001]
    mean = [0]
    for event in timeline:
        if event:
            delta.append(1)
        else:
            delta.append(0)
        mean.append(sum(delta[int(len(delta)/2):])/len(delta[int(len(delta)/2):]))
    delta.append(1.001)
    plt.figure()
    plt.plot(mean, c='red')
    plt.plot(delta)

with codecs.open('text1.txt', encoding='utf-16') as f:
    lines = f.readlines()
delta = [-0.001]
mean = [0]
for line in lines:
    if line.startswith('Right'):
        delta.append(1)
    elif line.startswith('False'):
        delta.append(0)
    mean.append(sum(delta[int(len(delta)/2):])/len(delta[int(len(delta)/2):]))
delta.append(1.001)
plt.figure()
plt.plot(mean, c='red')
plt.plot(delta)