# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 09:59:02 2018

@author: Rignak
"""


import os
from os import remove, rename
from os.path import join, getsize
import subprocess
from datetime import datetime
from sys import stdout
from threading import Thread
import threading
import time

def Progress(s):
    stdout.write('\r')
    stdout.write(s+'            ')
    stdout.flush()

def GetBitRate(file):
    command = 'ffprobe -v error -show_entries stream=bit_rate "' + file+'"'
    res = subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8')
    try:
        res = res.split()[1].split('=')[1]
        return res
    except Exception as e:
        print(e, file, res)
        return 0
        
def ListFiles():
    data = []
    fs = list(os.walk('.'))
    t = sum([len([file for file in files if  file.endswith('.mp3') or file.endswith('.wav')]) for root, folders, files in fs])
    j = 0
    begin = datetime.now()
    for root, folders, files in fs:
        for file in files:
            if file.endswith('.mp3') or file.endswith('.wav'):
                bitRate = GetBitRate(join(root, file))
                kbs = int(int(bitRate)/1024)
                if kbs > 190:
                    data.append(join(root, file))
                j+=1
                eta = (datetime.now()-begin)/j*t+begin
                Progress(str(j)+'/'+str(t)+' | '+eta.strftime('%H:%M'))
    return data

def Reduce175(data, nb):
    limit_active = nb
    begin = datetime.now()
    t = len(data)
    for i, file in enumerate(data):
        while threading.active_count() > limit_active:
            time.sleep(0.1)
        newfile = file[:-4]+' 175.mp3'
        command = 'ffmpeg -i  "' + file+'" -codec:a libmp3lame -qscale:a 3 "'+newfile+'"'
        Thread(target=os.system, args=(command, )).start()
        if not i%10:
            eta = (datetime.now()-begin)/(i+1)*t+begin
            Progress(str(i+1)+'/'+str(t)+' | '+eta.strftime('%H:%M'))

def Replace(data):
    for file in data:
        newfile = file[:-4]+' 175.mp3'
        if getsize(newfile)>5:
            remove(file)
            rename(newfile, file[:-4]+'.mp3')
        else:
            print(newfile)
            
def main():
    data = ListFiles()
    nb = threading.active_count() + 5
    Reduce175(data, nb)
    while threading.active_count() > nb-5:
        time.sleep(1)
    Replace(data)


if __name__ == '__main__':
    main()