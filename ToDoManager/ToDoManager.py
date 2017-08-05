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
    yt.filter('mp4')[-1].download(join(local, ext))
    if ext == 'mp3':
        line = name + '.mp4\t' + begin + '\t' + end
        ToMP3(name + '.mp4\t' + begin + '\t' + end)

def CutVideo(line):
    l1 = line.split('\t')
    l2 = []
    for x in l1:
        if x:
            l2.append(x)
    res_name, begin, end, epi, path = l2
    res_name = join(local, 'ok', res_name +'.mkv')
    path = join(local, 'mkv', path)
    begin, end = [ConvertTime(d) for d in [begin, end]]
    if end != '00:00:00':
        end =  " -to " + end
    else:
        end = ""
    opt = " -c:v libx265 -map 0 -force_key_frames 0  -crf 23 "
    line = 'ffmpeg.exe -i "' + path + '" -ss ' + begin + end \
                + opt +'"' + res_name + '"'
    os.system(line)

def ToMP3(line):
    name, begin, end = line.split('\t')
    name = join(local, 'mp3', name)
    res = name.replace(name.split('.')[-1], 'mp3').replace('\mp3\\', '\ok\\')

    begin, end = [ConvertTime(d) for d in [begin, end]]
    if end != '00:00:00':
        end =  " -to " + end
    else:
        end = ""
    while os.path.exists(res):
        res+='1'
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
    youtube, video, mp3 = False, False, False
    for line in lines:
        if line.startswith('youtube'):
            youtube = True
            continue
        elif line.startswith('video'):
            youtube = False
            video = True
            continue
        elif line.startswith('audio'):
            video = False
            mp3 = True
            continue
        elif line.startswith('--') or not (video or mp3 or youtube):
            continue
        if youtube:
            FromYoutube(line)
        elif video:
            CutVideo(line)
        elif mp3:
            ToMP3(line)
        print(line.split('\t')[0])