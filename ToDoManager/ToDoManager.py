# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 15:03:58 2017

@author: Rignak
"""
import os
from os.path import join
import pytube


local = "E:\Telechargements\Anime\\to_do"
try:
    os.makedirs(join(local, 'input'))
except:
    pass
try:
    os.makedirs(join(local, 'output'))
except:
    pass

def SubDate(str1, str2):
    int1 = int(str1[0:2])*3600+int(str1[3:5])*60+int(str1[6:8])
    int2 = int(str2[0:2])*3600+int(str2[3:5])*60+int(str2[6:8])
    int3 = int2-int1
    a, b, c = str(int3//3600), str(int3%3600//60), str(int3%60)
    for o in [a, b, c]:
        if len(o) < 2:
            o = '0'+o
    str3 = ':'.join([a, b, c])
    return str3
    
def FromYoutube(line):
    line = line.split('\t')
    if len(line) == 3:
        name, link, ext = line[:3]
        begin, end = '0000', '0000'
    else:
        name, link, ext, begin, end = line[:5]
    yt = pytube.YouTube(link)
    yt.set_filename(name)
    yt.filter('mp4')[-1].download(join(local,"input"))
    if ext == 'mp3':
        ToMP3('\t'.join([name + '.mp4', begin, end]))
    else:
        CutVideo('\t'.join([name, begin, end, '0', name + '.mp4']))
            

def CutVideo(line):
    l1 = line.split('\t')
    l2 = []
    for x in l1:
        if x:
            l2.append(x)
    res_name, begin, end, epi, path = l2[:5]
    res_name = join(local, 'output', res_name +'.mkv')
    path = join(local, 'input', path)
    begin, end = [ConvertTime(d) for d in [begin, end]]
    if end != '00:00:00':
        end = SubDate(begin, end)
        end =  "-t " + end
    else:
        end = ""
    opt = "-c:v libx265 -c:a aac -map 0 -force_key_frames 0 -crf 23"
    line = ' '.join(["ffmpeg", "-ss", begin, '-i', '"'+path+'"', end,  opt, '"'+res_name+'"'])
    print(line)
    os.system(line)
    
def FuseVideo(line):
    line = line.split('\t')
    res_name = line[0]
    files = open('concat.txt', "w")
    for file in line[1:]:
        os.rename(join(local, 'output', file), file)
        files.write('file '+ file + '\n')
    files.close()
    res_name = join(local, 'output', res_name +'.mkv')
    line = 'ffmpeg -f concat -safe 0 -i concat.txt -c copy -fflags +genpts "'+res_name + '"'
    os.system(line)
    for file in line[1:]:
        os.rename(file, join(local, 'input', file))
    

def ToMP3(line):
    name, begin, end = line.split('\t')[:3]
    name = join(local, 'input', name)
    res = (name[:-3]+'mp3').replace('input', 'output')
    begin, end = [ConvertTime(d) for d in [begin, end]]
    if end != '00:00:00':
        end =  " -to " + end
    else:
        end = ""
    while os.path.exists(res):
        res+='1'
    line = " ".join(['ffmpeg -i', '"'+name+'"', "-ss", begin, end, '"'+res+'"'])
    os.system(line)

def ConvertTime(d):
    res = d[0:2] + ':' + d[2:4]
    if len(d) == 6:
        res += ':' + d[4:6]
    else:
        res = '00:'+res
    return res

if __name__ == '__main__':
    with open(join(local, 'To Do.txt'), 'r') as file:
        lines = [line.replace('\n', '') for line in file.readlines()]
    youtube, video, mp3, fusion = False, False, False, False
    for line in lines:
        line = '\t'.join([e for e in line.split('\t') if e])
        if line.startswith('youtube'):
            youtube = True
            continue
        elif line.startswith('video'):
            youtube = False
            video = True
            continue
        elif line.startswith('fusion'):
            video = False
            fusion = True
            continue
        elif line.startswith('audio'):
            fusion = False
            mp3 = True
            continue
        elif line.startswith('--') or not (video or mp3 or youtube or fusion):
            continue
        if youtube:
            FromYoutube(line)
        elif video:
            CutVideo(line)
        elif fusion:
            FuseVideo(line)
        elif mp3:
            ToMP3(line)
        print(line.split('\t')[0])