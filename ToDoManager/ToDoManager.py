# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 15:03:58 2017

@author: Rignak
"""
import os
from os.path import join, exists, getsize, split, splitext
import subprocess
import pytube


local = "D:\Telechargements\Anime\\to_do"
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
    if int3 < 0:
        print('ERROR : end time < begin time')
        int3 = 1
    a, b, c = str(int3//3600), str(int3%3600//60), str(int3%60)
    for o in [a, b, c]:
        if len(o) < 2:
            o = '0'+o
    str3 = f'{a}:{b}:{c}'
    return str3

def FromYoutube(line, mode = 1):
    line = line.split('\t')
    if len(line) in [0, 1, 2, 4]:
        print('Youtube ERROR : check TODO file (not enough values)')
        return '', '', True
    if len(line) == 3:
        name, link, ext = line[:3]
        begin, end = '0000', '0000'
    else:
        name, link, ext, begin, end = line[:5]
    link = link.replace('\\', '/')
    name = name.replace('/', '\\')
    try:
        yt = pytube.YouTube(link)
        MakeOutputPath(join(local,"input", name))
        name = yt.streams.first().download(join(local,"input"), filename=name)
        newname = splitext(name.replace('input', 'output'))[0]
    except Exception as e:
        print(e)
    if ext == 'mp3':
        return ToMP3(f"{newname}.mp3\t{begin}\t{end}\t{name}", mode=mode)
    else:
        return CutVideo(f'{newname}\t{begin}\t{end}\t0\t{name}', mode=mode)


def CutVideo(line, mode = 1):
    error = False
    l1 = line.split('\t')
    l2 = []
    for x in l1:
        if x:
            l2.append(x)
    if len(l2)<5:
        print('Video ERROR : check TODO file (not enough values)', l2)
        return '', '', True
    res_name, begin, end, epi, path = l2[:5]
    res_name = join(local, 'output', res_name +'.mkv')
    MakeOutputPath(res_name)
    path = join(local, 'input', path)
    begin, end = [ConvertTime(d) for d in [begin, end]]
    if end != '00:00:00':
        end = SubDate(begin, end)
        end =  "-t " + end
    else:
        end = ""

    command = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "{path}"'
    opt = "-c:v libx265 -c:s copy -map 0:a -map 0:v -map 0:s? -force_key_frames 0 -crf 23"
    if '1080' in subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8'):
        opt +=  " -vf scale=-1:720 "
    line = f'ffmpeg -ss {begin} -i "{path}" {end} {opt} "{res_name}"'
    print(line)
    if exists(res_name):
        error = True
        print('ERROR : file already exist')
    elif not exists(path):
        error = True
        print('ERROR : no source file')
    elif mode:
        os.system(line)
    return res_name, line, error

def FuseVideo(line, mode = 1):
    error = False
    line = line.split('\t')
    res_name = line[0]
    global generated
    for file in line[1:]:
        full_path = join(local, 'output', file)
        cond = [full_path in generated, exists(full_path)][mode]
        if not cond:
            error = True
            print('Fuse ERROR : no source file', file)
            return '', '', True
    if mode:
        with open('concat.txt', "w") as files:
            for file in line[1:]:
                os.rename(join(local, 'output', file), file)
                files.write(f'file {file}\n')
    res_name = join(local, 'output', res_name +'.mkv')
    MakeOutputPath(res_name)
    cmd = f'ffmpeg -f concat -safe 0 -i concat.txt -c copy  -map 0:a? -map 0:v -map 0:s? -fflags +genpts "{res_name}"'
    if exists(res_name):
        error = True
        print('ERROR : file already exist')
    if not error and mode:
        os.system(cmd)
        for file in line[1:]:
            os.rename(file, join(local, 'input', file))
    return res_name, cmd, error


def ToMP3(line, mode = 1):
    error = False
    l1 = line.split('\t')
    l2 = []
    for x in l1:
        if x:
            l2.append(x)
    if len(l2) not in [2, 4]:
        print('Audio ERROR : check TODO file', l2)
        return '', '', True
    elif len(l2) == 2:
        name = l2[0]
        begin, end = '0000', '0000'
    else:
        name, begin, end, old = l2[:4]
    old = join(local, 'input', old)
    name = join(local, 'output', name)
    MakeOutputPath(name)
    MakeOutputPath(old)
    begin, end = [ConvertTime(d) for d in [begin, end]]
    if end != '00:00:00':
        end =  " -to " + end
    else:
        end = ""
    if not name.endswith('.mp3'):
        name += '.mp3'
    line = f'ffmpeg -i "{old}" -codec:a libmp3lame -qscale:a 3 -ss {begin} {end} "{name}"'
    if exists(name):
        error = True
        print('ERROR : file already exist')
    elif not exists(old):
        error = True
        print(old)
        print(line)
        print('ERROR : no source file')
    elif mode:
        os.system(line)
    return name, line, error

def ConvertTime(d):
    if d == '0':
        d = '0000'
    res = d[0:2] + ':' + d[2:4]
    if len(d) == 6:
        res += ':' + d[4:6]
    else:
        res = '00:'+res
    return res

def SwitchIni(youtube, video, mp3, fusion, line):
    change = True
    if line.startswith('youtube'):
        youtube = True
    elif line.startswith('video'):
        print(line)
        youtube = False
        video = True
    elif line.startswith('fusion'):
        video = False
        fusion = True
    elif line.startswith('audio'):
        fusion = False
        mp3 = True
    else:
        change = False
    return youtube, video, mp3, fusion, change

def SwitchLaunch(youtube, video, mp3, fusion):
    if youtube:
        return FromYoutube
    elif video:
        return CutVideo
    elif fusion:
        return FuseVideo
    elif mp3:
        return ToMP3

def Loop(lines, mode = 1):
    youtube, video, mp3, fusion = False, False, False, False
    begin = 0
    end = 1000
    global generated
    generated = []
    if mode:
        choice = input("Begin at line ? ")
        if choice:
            begin = int(choice)
    for i, line in enumerate(lines):
        line = '\t'.join([e for e in line.split('\t') if e])
        youtube, video, mp3, fusion, change = SwitchIni(youtube, video, mp3, fusion, line)
        if change or line.startswith('--') or not (video or mp3 or youtube or fusion) or i<begin or i > end:
            continue
        function = SwitchLaunch(youtube, video, mp3, fusion)
        if mode or (function != FromYoutube):
            name, cmd, error = function(line, mode)
            if not error:
                if mode and not exists(name):
                    print('ERROR : no file created')
                    print('command:', cmd)
                elif mode and getsize(name) < 1024:
                    print('ERROR : very small file created')
                    print('command:', cmd)
                else:
                    advance = f'({i}|{len(lines)})'
                    generated.append(name)
                    print('OK:', advance, line.split('\t')[0])

def MakeOutputPath(name):
    localLength = len(split(local))
    splited = split(name)[localLength:]
    todo = [join(split[:i]) for i in range(1,len(splited))]
    for ele in todo:
        if not os.path.exists(join(local, ele)) and '.' not in ele:
            os.makedirs(join(local, ele))
        if not os.path.exists(join(local, ele)) and '.' not in ele:
            os.makedirs(join(local, ele))

if __name__ == '__main__':
    with open(join(local, 'To Do.txt'), 'r') as file:
        lines = [line.replace('\n', '') for line in file.readlines()]

    Loop(lines, mode = 0)
    if input('Continue ? (y/n) : ') == 'y':
        Loop(lines, mode = 1)