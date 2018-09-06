# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 21:10:41 2018

@author: Rignak
"""
from os.path import join, exists
from os import makedirs, listdir
unknowns = []

class Arc():
    def __init__(self, line):
        if line:
            self.level = int(line[0])
            self.name = line[1]
            self.episodes = line[2:4]
            try:
                self.length = abs(int(line[3])-int(line[2]))
            except Exception as e:
                self.length = 1
                print(line)
            self.childs = []
            self.mother = Arc([])
            self.lines = [0,0]
            self.characters = []
            self.file = None
        else:
            self.name = ''

    def Write(self, maxLevel):
        if self.childs:
            self.length-=1
        size = str(2*self.length)
        if self.level == 1:
            newlines =  ['<tr>\n']
        else:
            newlines = []
        newline = '<td style="width: '+str(int(100/maxLevel))+'%; border-right:2px solid #FFF;'+\
                'font-size:'+str(min(20,2*self.length))+'"; rowspan="'+ size +\
                 '" bgcolor='
        newline += '"'+self.background+'">'
        if self.file:
            newline += '<a href="'+self.name+'" onclick="window.open(\''+self.file+'\', \'newwindow\', \'width=1500,height=800\'); return false;\">'+self.name+'</a>\n'
        else:
            newline += self.name+'</td>\n'
        newlines.append(newline)
        if self.childs:
            for i, child in enumerate(self.childs):
                if i != 0:
                    newlines.append('<tr>\n')
                newlines += child.Write(maxLevel)
        else:
            i = self.level
            while i < maxLevel:
                newline = '<td style="width: 30%;" rowspan="'+ size+ '" bgcolor='
                newline += '"'+'#FFFFFF'+'"></td>\n'
                newlines.append(newline)
                i+=1
            for i in range(int(size)+1):
                newlines.append('<tr>\n<td> </td>\n</tr>\n')
            newlines.append('</tr>\n')

        return newlines

    def WriteArcHTML(self):
        newlines = ['<html>\n<body>\n']
        newlines.append('<h1>'+self.name+' ('+self.episodes[0]+', '+self.episodes[1]+') </h1>')
        for line in self.lines:
            newlines.append('<h2>'+line[0]+'</h2>\n')
            for character in [character for character in line[1:] if character]:
                die = False
                joinC = False
                if character.endswith('-die-'):
                    die = True
                    character = character[:-5]
                elif character.endswith('-join-'):
                    joinC = True
                    character = character[:-6]
                newlines.append('\n<img src='+'characters/'+character+'.jpg width="169" height="263"" alt="'+character+'" ')
                if die:
                    newlines[-1]+= 'style="border:4px solid red '
                elif joinC:
                    newlines[-1]+= 'style="border:4px solid green'
                newlines[-1]+='">\n\n'

                if not exists(join(root, 'res', 'characters', character +'.jpg')) and character not in unknowns:
                    unknowns.append(character)

                pass
        with open(join(root, 'res', 'arc'+self.name+'.html'), 'w') as file:
            for newline in newlines:
                file.write(newline)
            file.write('</body>\n</html>')
        self.file = 'res/arc'+self.name+'.html'

def getMaxLevel(lines):
    maxLevel = 0
    for line in lines:
        if line[0] in ['1', '2','3', '4'] and int(line[0]) > maxLevel:
            maxLevel = int(line[0])
    return maxLevel

def iniArcs(lines):
    arcs = []
    currentArc = None
    for i, line in enumerate(lines):
        if not line:
            continue
        if line[0] in ['1', '2','3', '4']:
            if currentArc:
                currentArc.lines[1] = i-1
                arcs.append(currentArc)
            currentArc = Arc(line)
            currentArc.lines = [i, i]
    currentArc.lines[1] = i
    arcs.append(currentArc)
    for arc in arcs:
        if  arc.lines[1] != arc.lines[0]:
            arc.lines = [lines[i] for i in range(arc.lines[0]+1, arc.lines[1]+1)]
            arc.WriteArcHTML()

    return arcs

def makeFamilies(arcs, maxLevel):
    mothers = {key:'' for key in range(maxLevel+1)}
    for arc in arcs:
        if not mothers[arc.level]:
            mothers[arc.level] = arc
        if arc.level != 1:
            mothers[arc.level-1].childs.append(arc)
            arc.mother = mothers[arc.level-1]
        mothers[arc.level] = arc


def AlternBackground(arcs, maxLevel):
    backgrounds = ["#D8BFD8","#FFB2B2"]
    for i in range(maxLevel+1):
        arcAtLevel = [arc for arc in arcs if arc.level == i]
        for j, arc in enumerate(arcAtLevel):
            arc.background = backgrounds[j%2]
    return newlines

if __name__ == '__main__':
    #root = input('Which folder run ? ')
    for root in listdir():
        print(root)
        if root in ['index.html', 'ListArcs.py']:
            continue
        if not exists(join(root, 'res')):
            makedirs(join(root,'res'))
        with open(join(root, root+'.txt'), 'r') as file:
            lines = file.readlines()
            lines = [line.replace('\n', '').split('\t') for line in lines]

        newlines = ['<html>\n<body>\n']
        series = []
        for line in lines:
            if line[0] == '0':
                series.append([])
            series[-1].append(line)
        for lines in series:
            maxLevel = getMaxLevel(lines)
            newlines+=['<h1 style="text-align:center">'+lines[0][1]+'</h1>\n']
            newlines+=['<table class="wikitable" cellspacing=0 style="width: 100%; text-align: center; ">\n',
                    '<th style="width: '+str(int(100/maxLevel))+'%;">Sagas</th>\n',
                    '<th style="width: '+str(int(100/maxLevel))+'%;">Arcs</th>\n',
                    '<th style="width: '+str(int(100/maxLevel))+'%;">Segment</th>\n',
                    '<th style="width: '+str(int(100/maxLevel))+'%;">Chapitre</th>\n'][:maxLevel+1]
            arcs = iniArcs(lines)
            makeFamilies(arcs, maxLevel)
            AlternBackground(arcs, maxLevel)

            for arc in [arc for arc in arcs if arc.level == 1]:
                newlines += arc.Write(maxLevel)

            newlines.append('\n</table>')
        with open(join(root, root+'.html'), 'w') as file:
            for newline in newlines:
                file.write(newline)
            file.write('</body>\n</html>')

    with open('index.html', 'w') as file:
        file.write('<html>\n<body>\n')
        for serie in listdir():
            if serie not in ['index.html', 'ListArcs.py']:
                file.write('<div><h1><a href="'+join(serie, serie+'.html')+'">'+ serie+'</a></h1></div>\n')

    for character in unknowns:#sorted(unknowns):
        print('unknown character:', character)
    print(len(unknowns))