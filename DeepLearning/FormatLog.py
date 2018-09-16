# -*- coding: utf-8 -*-
"""
Created on Sat Apr 14 17:17:37 2018

@author: Rignak
"""
from difflib import SequenceMatcher

"""This a small programm to reduce the log file
example with trainH: 65k lines (7,6 Mo) to 45 (2 ko)"""

with open('logs\\log.txt','r', encoding='utf-16') as f:
    lines = f.readlines()

# ------------------------
# Remove repetion of lines
# ------------------------
previous = lines[0]
noRep = [previous]
for line in lines[1:]:
    line = line[:-1]
    if not line:
        continue
    similarity = SequenceMatcher(a=line, b=previous).ratio()
    if similarity > 0.50:
        noRep[-1] = line
    else:
        noRep.append(line)
    previous = line
    
# ------------------------
# Fuse epoch and results
# ------------------------
formated = []
i = 0
while i in range(len(noRep)):
    line = noRep[i]
    if line.startswith('Epoch '):
        line +=': ' + noRep[i+1]
        i += 2
    else:
        i+=1
    formated.append(line)


# ------------------------
# Remove useless epochs
# ------------------------
previous = formated[0]
stacks = [[previous]]
for line in formated[1:]:
    similarity = SequenceMatcher(a=line, b=previous).ratio()
    if similarity > 0.30:
        stacks[-1].append(line)
    else:
        stacks.append([line])
    
    previous = line
  
res = []
for stack in stacks:
    if len(stack) == 1:
       res.append(stack[0]) 
    else:
        bestV = 10
        for currentL in stack:
            try:
                currentV = float(currentL.split()[15])
            except:
                res.append(currentL)
            if currentV < bestV:
                bestL = currentL
                bestv = currentV
        res.append(bestL)

# ------------------------
# Write the new log
# ------------------------
with open('logs\\formatedLog.txt', 'w') as file:
    for line in res:
        file.write(line+'\n')