# -*- coding: utf-8 -*-
"""
Created on Thu May  3 14:29:24 2018

@author: Rignak
"""

import pickle
from os.path import join
from os import walk, listdir

filename = '1illustrations123'

confuse = pickle.load(open(join('confuse', filename+'.p'), "rb" ))
header = pickle.load(open(join('confuse', filename+'_header.p'), "rb" ))

with open('test.txt', 'w') as file:
    file.write(filename+'\t'+'\t'.join(header)+'\n')
    for i, label in enumerate(header):
        new = [str(v) for v in confuse[i]]
        line = label+'\t'+'\t'.join(new).replace('.', ',')
        file.write(line)
        file.write('\n')
        
    line = 'success_char\t'+'\t'.join([str(confuse[i][i]) for i in range(len(confuse))]).replace('.', ',')
    file.write(line+ '\n')
    

with open('test.txt', 'r') as file:
    for line in file.readlines():
        print(line[:-1])