# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 15:52:06 2017

@author: Rignak
"""
import os
if __name__ == '__main__':
    folder = ".\_Epic"
    print("apply h265")
    begin = False
    for directory, subdirectories, files in os.walk(folder):
        for file in files:
            if not begin:
                if "." in file:
                    begin = True
                else:
                    continue
            n1 = os.path.join(directory, file)
            ext = n1[-3:]
            print(n1)
            if ext in ['avi', 'AVI']:
                n2 = n1[:-4]+'.mp4'
                line = 'ffmpeg.exe -i "'  + n1 + '" -codec copy "' + n2 + '"'
                os.system(line)
                if os.path.exists(n2):
                    os.remove(n1)
                    n1 = n2
                    ext = 'mp4'
            if ext in ['mkv', 'mp4']:
                n2 = n1[:-4]+'_temp'+n1[-4:]
                line = 'ffmpeg.exe -i "'  + n1 + '" -c:v libx265 -crf 23 "' + n2 + '"'
                os.system(line)
                if os.path.exists(n2):
                    os.remove(n1)
                    os.rename(n2, n1)
                else:
                    print("Error on :", n1, ':', n2, "doesn't exist")