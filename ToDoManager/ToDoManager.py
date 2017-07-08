# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 15:03:58 2017

@author: Rignak
"""
import os
from os.path import join
import pytube

def FromYoutube(line):
    line = line.split('\t')
    if len(line) == 3:
        name, link, ext = line
        begin, end = '0000', '0000'
    else:
        name, link, ext, begin, end = line
    yt = pytube.YouTube(link)
    yt.set_filename(name)
    yt.filter('mp4')[-1].download(join(local, 'mp3'))
    if ext == 'mp3':
        line = name + '.mp4\t' + begin + '\t' + end
        ToMP3(name + '.mp4\t' + begin + '\t' + end)

def CutMP4(line):
    l1 = line.split('\t')
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
    os.system('ffmpeg.exe -i "' + path + '" -ss ' + begin + end \
                + opt +'"' + res_name + '"')

def ToMP3(line):
    name, begin, end = line.split('\t')
    name = join(local, 'mp3', name)
    res = name.replace(name.split('.')[-1], 'mp3').replace('\mp3\\', '\ok\\')

    begin, end = [ConvertTime(d) for d in [begin, end]]
    if end != '00:00:00':
        end =  " -to " + end
    else:
        end = ""
    os.system('ffmpeg.exe -i "' + name + '" -ss ' + begin + end + ' "' + res + '"')

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
        lines = [line.replace('\n', '') for line in file.readlines()]
    youtube, mp4, mp3 = False, False, False
    for line in lines:
        if line.startswith('youtube'):
            youtube = True
            continue
        elif line.startswith('video'):
            youtube = False
            mp4 = True
            continue
        elif line.startswith('audio'):
            mp4 = False
            mp3 = True
            continue
        elif line.startswith('--') or not (mp4 or mp3 or youtube):
            continue
        if youtube:
            FromYoutube(line)
        elif mp4:
            CutMP4(line)
        elif mp3:
            ToMP3(line)
        print(line.split('\t')[0])