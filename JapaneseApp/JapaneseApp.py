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


class Question:
    def __init__(self, line, question, answer):
        l = line.split('\t')
        self.question = l[int(question)].replace(u'\xa0', u'')
        self.answer = l[int(answer)].replace(u'\xa0', u'')
        self.all = [l[i].replace(u'\xa0', u'') for i in range(len(l))]
        return

class Question_Canvas(tk.Tk):
    def __init__(self):
        self.fenetre=tk.Tk.__init__(self)
        self.bind('<Return>', self.on_button_check)
        self._update = False
        self.canvas = tk.Canvas(self.fenetre, width=300, height=100)
        self._text = self.canvas.create_text(150, 20, text='Hello World', font="Arial 25")
        self.canvas.pack()
        self.entry = tk.Entry(self.fenetre, textvariable="Enter the aswer", width=15)
        self.entry.pack()
        self.button_check = tk.Button(self, text="Check", command=self.on_button_check, width=10)
        self.button_check.pack()
        self.button_pass = tk.Button(self, text="Pass", command=self.on_button_pass, width=10)
        self.button_pass.pack()
        self.button_break = tk.Button(self, text="Break", command=self.on_button_break, width=10)
        self.button_break.pack()
        self._result = [0, 0]

    def Init(self, question):
        self.question = question
        self.canvas.delete(self._text)
        self._text = self.canvas.create_text(150, 20, text=self.question.question, font="Arial 25")
        self.canvas.pack()
        self._update = False

    def on_button_check(self, event = None):
        if self.entry.get() in  self.question.answer.split(', '):
            print('Right : ', self.question.all)
            sys.stdout.flush()
            self._result[0] += 1
        else:
            print('False', self.question.all)
            self._result[1] += 1
        self._update = True
        sys.stdout.flush()
        self.entry.delete(0, "end")
        self.entry.insert(0, "")
        self.entry.pack()
        return

    def on_button_pass(self):
        print(self.question.all)
        sys.stdout.flush()
        self._update = True
        return

    def on_button_break(self):
        frame.destroy()

def FileSelection():
    print("Vocabulaire par cours : 1")
    print("Verbes : 2")
    print("Kanjis : 3")
    choice = int(input("Selectionner le mode : "))
    if choice == 1:
        namefiles = [join('res', 'cours', x + '.txt') for x in input("Numéro (ex : 1 2 5) : ").split()]
        header = join('res', 'cours', 'header.txt')
        r = (0, -1)
    elif choice in [2,3]:
        if choice  == 2:
            namefiles = [join('res', 'verbes.txt')]
            header = join('res', 'verbes_header.txt')
        elif choice == 3:
            namefiles = [join('res', 'kanjis.txt')]
            header = join('res', 'kanjis_header.txt')
        r = [int(x) for x in input("Range (ex : 10:20) : ").split(':')]
    return namefiles, header, r
    
if __name__ == '__main__':
    namefiles, header, r = FileSelection()
    head = codecs.open(header, encoding='utf-16').readline().split('\t')
    print('Quel binôme question/réponse ? (ex : 1 3)')
    print('! signifie symboles non-alphabétiques')
    question, answer = [int(x) for x in (input(' | '.join([str(i) + ': ' + head[i] for i in range(len(head))]) + ' : ').split())]
    if head[answer].startswith('!'):
        answer += 1
    worklist = []
    for namefile in namefiles:
        file = codecs.open(namefile, encoding='utf-16')
        for line in file:
            if line:
                worklist.append(Question(line[:-2], question, answer))
    worklist = worklist[r[0]:r[1]]
    print('You have', len(worklist),'questions')
    sys.stdout.flush()
    frame = Question_Canvas()
    while True:
        question = random.choice(worklist)
        try:
            frame.Init(question)
            while True:
                    frame.update()
                    if frame._update:
                        frame.canvas.delete(frame._text)
                        break
        except:
            print()
            print('--------------------------------')
            print("Nombre de bonnes réponses :   ", frame._result[0])
            print("Nombre de mauvaise réponses : ", frame._result[1])
            print('Terminaison du programe')
            print('--------------------------------')
            break