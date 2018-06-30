# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 14:58:32 2017

@author: Rignak
"""

import tkinter as tk
from os.path import join
import sys
import codecs
import random
import matplotlib.pyplot as plt
from random import shuffle

class Question:
    def __init__(self, line, question, answer):
        l = line.split('\t')
        self.question = l[int(question)].replace(u'\xa0', u'')
        try:
            self.answer = l[int(answer)].replace(u'\xa0', u'')
        except:
            print('Error:', line)
        self.all = [l[i].replace(u'\xa0', u'') for i in range(len(l))]
        return


class Question_Canvas(tk.Tk):
    def __init__(self, choice, worklist):
        self.fenetre = tk.Tk.__init__(self)
        self.bind('<Return>', self.on_button_check)
        self._update = False
        if choice == 4:
            self._width = 600
        else:
            self._width = 400
        self.canvas = tk.Canvas(self.fenetre, width=self._width, height=100)
        self._text = self.canvas.create_text(
            self._width/2, 20, text='Hello World', font="Arial 25")
        self.canvas.pack()
        self.entry = tk.Entry(
            self.fenetre,
            textvariable="Enter the aswer",
            width=30)
        self.entry.pack()
        self.button_check = tk.Button(
            self, text="Check", command=self.on_button_check, width=10)
        self.button_check.pack()
        self.button_pass = tk.Button(
            self, text="Pass", command=self.on_button_pass, width=10)
        self.button_pass.pack()
        self.button_break = tk.Button(
            self, text="Break", command=self.on_button_break, width=10)
        self.button_break.pack()
        self._result = {'timeline':[], 'count':{}}
        for question in worklist:
            self._result[question.question] = [0, 0]
            self._result['count'][question] = 0

    def Init(self, question, second=False):
        self.question = question
        self.second = second
        self.canvas.delete(self._text)
        if self._width == 300:
            font = 'Arial 25'
        else:
            font = 'Arial 25'
        self._text = self.canvas.create_text(
            self._width/2, 20, text=self.question.question, font=font)
        self.canvas.pack()
        self._update = False

    def on_button_check(self, event=None):
        if self.entry.get() in self.question.answer.split(', '):
            sys.stdout.flush()
            if not self.second:
                self._result[self.question.question][0] += 1
                self._result['timeline'].append(True)
                self._result['count'][self.question] += 1
                print('Right : ', self.question.answer, len(worklist))
            self._update = True
        else:
            if not self.second:
                self._result[self.question.question][1] += 1
                self._result['timeline'].append(False)
                self._result['count'][self.question] = 0
                print('False : ', self.question.question, '->', self.question.answer, len(worklist))
                
            self._update = self.question
        sys.stdout.flush()
        self.entry.delete(0, "end")
        self.entry.insert(0, "")
        self.entry.pack()
        return

    def on_button_pass(self):
        print(self.question.answer)
        sys.stdout.flush()
        self._update = True
        return

    def on_button_break(self):
        print()
        print('--------------------------------')
        PlotLearning(self._result['timeline'])
        PrintCommonError(self._result)
        frame.destroy()

def PrintCommonError(dic):
    temp = {k:v[1]/(v[1]+v[0]) for (k, v) in dic.items() if k not in ['timeline', 'count'] and v[1]+v[0]!=0}
    for k, v in sorted([(v, k) for (k, v) in temp.items()]):
        if k != 0.0:
            print((dic[v][0], dic[v][1]), ':', v)

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

def FileSelection():
    print("Vocabulaire par cours : 1")
    print("Verbes : 2")
    print("Kanjis : 3")
    print("Conjugaison (tous les modes de verbes) : 4")
    print("Numéraux : 5")
    choice = 0
    ok = False
    while choice not in list(range(1, 5)):
        try:
            choice = int(input("Selectionner le mode : "))
        except Exception as e:
            print(e)
    if choice == 1:
        while not ok:
            files = input("Numéro (ex : 1 2 5 ou 2:5) : ")
            try:
                if ':' not in files:
                    print('not in', files)
                    files = files.split()
                else:
                    a, b = files.split(':')
                    files = list(range(int(a), int(b) + 1))
                if any(int(x) > 20 or int(x) < 1 for x in files):
                    print('One of the file is unkown, try again')
            except Exception as e:
                print(e)
            else:
                ok = True
        namefiles = [join('res', 'cours', str(x) + '.txt') for x in files]
        header = join('res', 'cours', 'header.txt')
        r = (0, -1)
    elif choice in [2, 3, 4]:
        mode = ['', '', 'verbes', 'kanjis', 'conjugaison', 'numeraux']
        namefiles = [join('res', mode[choice] + '.txt')]
        header = join('res', mode[choice] + '_header.txt')
        while not ok:
             r = input("Range (ex : 10:20) : ")
             try:
                 if ':' in r:
                     r = [int(x) for x in r.split(':')]
                     r[0] -= 1
                     ok = True
             except Exception as e:
                 print(e)
    return namefiles, header, r,choice


if __name__ == '__main__':
    namefiles, header, r, mode = FileSelection()
    f1 = open(header)
    head = f1.readline().split('\t')
    print('Quel binôme question/réponse ? (ex : 0 1)')
    print('! signifie symboles non-alphabétiques')
    ok = False
    while not ok:
        choice = input(' | '.join([str(i) + ': ' + head[i]
                                   for i in range(len(head))]) + ' : ')
        if len(choice.split()) == 2:
            a, b = choice.split()
            try:
                if int(a) < len(head) and int(b) < len(head):
                    ok = True
            except Exception as e:
                print(e)
    question, answer = [int(x) for x in (choice.split())]
    worklist = []
    for namefile in namefiles:
        f2 = codecs.open(namefile, encoding='utf-16')
        for line in f2:
            if line:
                line = line.replace('\n', '')
                line = line.replace('\r', '')
                worklist.append(Question(line, question, answer))
    if r[1] == -1:
        worklist = worklist[r[0]:]
    else:
        worklist = worklist[r[0]:r[1]]
    shuffle(worklist)
    worklist = worklist[:75]
    worklist = [question for question in worklist if question.answer != '']
    print('You have', len(worklist), 'questions')
    sys.stdout.flush()
    frame = Question_Canvas(mode, worklist)
    while True:
        if type(frame._update) == Question:
            question = frame._update
            frame.Init(question, second=True)
        else:
            if type(question) != int and frame._result['count'][question] > 4: # Param
                worklist.pop(worklist.index(question))
                if not worklist:
                    frame.on_button_break()
                    break
            question = random.choice(worklist)
            frame.Init(question)
        try:
            while True:
                frame.update()
                if frame._update:
                    frame.canvas.delete(frame._text)
                    break
        except BaseException:
            print('Terminaison du programe')
            print('--------------------------------')
            break
    f1.close()
    f2.close()
