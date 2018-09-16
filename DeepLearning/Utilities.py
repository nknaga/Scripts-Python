# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 15:46:50 2018

@author: Rignak
"""

from  glob import glob
from PIL import Image
from os.path import join
from os import walk, rename
import sys

root = 'notComic'
    
def Progress(s):
    """Print a carriage return then a string
    
    Input:
    s -- a string"""
    sys.stdout.write('\r')
    sys.stdout.write(s+'           ')
    sys.stdout.flush()
    
def Checker():
    """Check if all picture are correctly downloaded (no truncated, no 0 size)"""
    files = glob(join('imgs', root, '**', '*.jpg'), recursive=True)
    for i, file in enumerate(files):
        try:
            img = Image.open(file)
            img.load()
            if not i%100:
                Progress(str(i))
        except Exception as e:
            print('\n-------\n',e, file,'\n-------\n')
            
def CountFiles():
    for ini, directories, filenames in walk(join('imgs', root)):
        for directory in directories:
            print(directory, len(glob(join('imgs', root, '**', directory, '**', '*.jpg'), recursive = True)))
            
def CheckNameUnicity():
    allLabels = []
    for ini, folders, files in walk(join('imgs', root)):
        for folder in folders:
            for label in allLabels:
                if label == folder:
                    print(label, 'already exist')
                elif label in folder:
                    print(label, 'in', folder)
                elif folder in label:
                    print(folder, 'in', label)
            allLabels.append(folder)
   
def ResizeAll(size):
    for ini, folders, files in walk(join('imgs', root)):
        for i, file in enumerate(files):
            fullPath = join(ini, file)
            img = Image.open(fullPath)
            
            img.thumbnail(size)
            x, y = img.size
            newIm = Image.new('RGB', size, (0,0,0))
            newIm.paste(img, (int((size[0] - x)/2), int((size[1] - y)/2)))
            newIm.save(fullPath, 'JPEG')
            if not i%100:
                Progress(ini+' '+str(i))


if __name__ == '__main__':
    CheckNameUnicity()
    Checker()
    #ResizeAll((150, 150))