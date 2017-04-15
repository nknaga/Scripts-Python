# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 14:58:32 2017

@author: Rignak
"""

import tkinter as tk
from os import remove, rename, walk, makedirs
from os.path import join, dirname, realpath, exists
import sys
import codecs
import time
import random

result = [0, 0]
index = 0

standart_root = dirname(realpath(__file__))
standart_file = join(standart_root, 'verbes.txt')

class Word:
    def __init__(self, line):
        l = line[:-2].split('\t')
        self.kana = l[0]
        self.translation = l[2]
        self.romaji = l[1]
        self.all = l
        return

class Word_Canvas(tk.Tk):
    def __init__(self, word):
        global index
        self.word = word
        self.fenetre=tk.Tk.__init__(self)
        self.canvas = tk.Canvas(self.fenetre, width=300, height=100)
        if index == 1:
            self.canvas.create_text(150, 20, text=self.word.translation, font="Arial 25")
        elif index == 2:
            self.canvas.create_text(150, 20, text=self.word.kana, font="Arial 25")
        self.canvas.pack()
        self.entry = tk.Entry(self.fenetre, textvariable="Enter the answer", width=15)
        self.entry.pack()
        self.button_check = tk.Button(self, text="Check", command=self.on_button_check, width=10)
        self.button_check.pack()
        self.button_pass = tk.Button(self, text="Pass", command=self.on_button_pass, width=10)
        self.button_pass.pack()
        self.button_break = tk.Button(self, text="Break", command=self.on_button_break, width=10)
        self.button_break.pack()

    def on_button_check(self):
        global result
        global index
        if self.entry.get() == self.word.all[index]:
            print('Right : ', self.word.all)
            self.destroy()
            result[0] += 1
        else:
            print('False', self.word.all[index])
            result[1] += 1
        sys.stdout.flush()
        return

    def on_button_pass(self):
        print(self.word.all)
        sys.stdout.flush()
        self.destroy()
        return

    def on_button_break(self):
        self.destroy()
        termination()

def termination():
        global result
        print()
        print("The number of good answer:", result[0])
        print("The number of bad answer:", result[1])
        print()
        sys.exit()

def ListWord(file = standart_file):
    f = codecs.open(file, encoding='utf-16')
    list_word = []
    for line in f:
        list_word.append(Word(line))
    return list_word

if __name__ == '__main__':
    file = input('Which file contain the words? ')
    while index != '3' and index != '2' and index != '1':
        index = input('Do you want to input F->J (1) or J->F(2) ? ')
    index = int(index)

    list_word = ListWord(file = file)
    print('You have', len(list_word),'words')
    sys.stdout.flush()
    list_word = list_word[0:20]
    random.shuffle(list_word)
    while True:
        word = random.choice(list_word)
        window = Word_Canvas(word)
        window.mainloop()
    termination()