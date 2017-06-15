# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 15:03:58 2017

@author: Rignak
"""
import os
from os.path import join

def ConvertTime(d):
    res = d[0:2] + ':' + d[2:4]
    if len(d) == 6:
        res += ':' + d[4:6]
    else:
        res = '00:'+res
    return res

if __name__ == '__main__':
    local = "E:\Telechargements\Anime\\to do"
    with open(join(local, 'To Do.txt'), 'r') as file:
        lines = file.readlines()
    mp4 = False
    commands = []
    for line in lines:
        if line.startswith('video'):
            mp4 = True
        elif mp4:
            l1 = line.replace('\n', '').split('\t')
            l2 = []
            for x in l1:
                if x:
                    l2.append(x)
            res_name, begin, end, epi, path = l2
            res_name = join(local, 'ok', res_name +'.mp4')
            path = join(local, 'mp4', path)
            begin, end = [ConvertTime(d) for d in [begin, end]]
            if end != '00:00:00':
                end =  " -to " + end
            else:
                end = ""
            opt = " -c copy -c:s mov_text "
            opt = " "
            opt = " -c:s mov_text "
            commands.append('ffmpeg.exe -i "' + path + '" -ss ' + begin + end \
                            + opt +'"' + res_name + '"')
    for file in os.listdir(join(local, 'mp3')):
        file = join(local, 'mp3', file)
        res = file.replace(file.split('.')[-1], 'mp3').replace('\mp3\\', '\ok\\')
        commands.append('ffmpeg.exe -i "' + file + '" "' + res + '"')

    for command in commands:
        print(command)
        p = os.system(command)