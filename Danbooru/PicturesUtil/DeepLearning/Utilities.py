# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 15:46:50 2018

@author: Rignak
"""

from  glob import glob
from PIL import Image
from os.path import join
from os import walk

def Checker():
    """Check if all picture are correctly downloaded (no truncated, no 0 size)"""
    files = glob.glob(join('imgs', 'illus2', '**', '*.jpg'), recursive=True)
    for i, file in enumerate(files):
        try:
            img = Image.open(file)
            img.load()
        except Exception as e:
            print('\n-------\n',e, file,'\n-------\n')
            
def CountFiles():
    folder = 'illustrations'
    
    for root, directories, filenames in walk(join('imgs', folder)):
        for directory in directories:
            print(directory, len(glob(join('imgs', folder, '**', directory, '**', '*.jpg'), recursive = True)))
            
if __name__ == '__main__':
    CountFiles()