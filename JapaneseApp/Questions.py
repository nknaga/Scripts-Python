# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 14:58:32 2017

@author: Rignak
"""

import tkinter as tk
from os.path import join, dirname, realpath
import sys
import codecs
import random

result = [0, 0]
index = 0

standart_root = dirname(realpath(__file__))
standart_file = join(standart_root, 'kanjis.txt')

class Question:
    def __init__(self, line, question, answer):
        l = line.split('\t')
        self.question = l[int(question)]
        self.answer = l[int(answer)]
        self.all = l
        return

class Question_Canvas(tk.Tk):
    def __init__(self):
        self.fenetre=tk.Tk.__init__(self)
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

    def Init(self, question):
        self._result = [0, 0]
        self.question = question
        self.canvas.delete(self._text)
        self._text = self.canvas.create_text(150, 20, text=self.question.question, font="Arial 25")
        self.canvas.pack()
        self._update = False

    def on_button_check(self):
        if self.entry.get() in  self.question.answer.split(', '):
            print('Right : ', self.question.all)
            sys.stdout.flush()
            self._update = True
            self._result[0] += 1
        else:
            print('False')
            self._result[1] += 1
        sys.stdout.flush()
        return

    def on_button_pass(self):
        print(self.question.all)
        sys.stdout.flush()
        self._update = True
        return

    def on_button_break(self):
        self.destroy()
        self.termination()

    def termination(self):
            print("The number of good answer:", self._result[0])
            print("The number of bad answer:", self._result[1])
            sys.exit()

if __name__ == '__main__':
    result = [0, 0]
    file = codecs.open(input('File to work? ')+'.txt', encoding='utf-16')
    head = file.readline()[:-2].split('\t')
    question, answer = input(' | '.join([str(i) + ': ' + head[i] for i in range(len(head))]) + ' : ').split()
    question, answer = int(question), int(answer)
    if head[answer].startswith('!'):
        answer += 1
    worklist = []
    while True:
        line = file.readline()
        if not line:
            break
        worklist.append(Question(line[:-2], question, answer))
    print('You have', len(worklist),'questions')
    sys.stdout.flush()
    frame = Question_Canvas()
    while True:
        question = random.choice(worklist)
        frame.Init(question)
        while True:
            try:
                frame.update()
                if frame._update:
                    frame.canvas.delete(frame._text)
                    break
            except:
                sys.exit()
    frame.termination()