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
standart_file = join(standart_root, 'kanjis.txt')

class Kanji:
    def __init__(self, line):
        l = line[:-2].split('\t')
        self.symbol = l[0]
        self.translation = l[1]
        self.onyomi = l[2]
        self.kunyomi = l[3]
        self.all = l
        return

class Kanji_Canvas(tk.Tk):
    def __init__(self, kanji):

        self.kanji = kanji
        self.fenetre=tk.Tk.__init__(self)
        self.canvas = tk.Canvas(self.fenetre, width=300, height=100)
        self.canvas.create_text(150, 20, text=self.kanji.symbol, font="Arial 25")
        self.canvas.pack()
        self.entry = tk.Entry(self.fenetre, textvariable="Enter the aswer", width=15)
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
        if self.entry.get() in  self.kanji.all[index].split(', '):
            print('Right : ', self.kanji.all)
            self.destroy()
            result[0] += 1
        else:
            print('False')
            result[1] += 1
        sys.stdout.flush()
        return

    def on_button_pass(self):
        print(self.kanji.all)
        sys.stdout.flush()
        self.destroy()
        return

    def on_button_break(self):
        self.destroy()
        termination()

def termination():
        global result
        print("The number of good answer:", result[0])
        print("The number of bad answer:", result[1])
        sys.exit()

def ListKanji(file = standart_file):
    f = codecs.open(file, encoding='utf-16')
    list_kanji = []
    for line in f:
        list_kanji.append(Kanji(line))
    return list_kanji

if __name__ == '__main__':
    file = input('Which file contain the kanjis? ')
    while index != '3' and index != '2' and index != '1':
        index = input('Do you want to input translation (1), onyomi (2) or kunyomi (3)? ')
    index = int(index)

    list_kanji = ListKanji(file = file)
    print('You have', len(list_kanji),'kanjis')
    sys.stdout.flush()
    random.shuffle(list_kanji)
    while True:
        kanji = random.choice(list_kanji)
        window = Kanji_Canvas(kanji)
        window.mainloop()
    termination()