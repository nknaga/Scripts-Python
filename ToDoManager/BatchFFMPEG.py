# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 15:52:06 2017

@author: Rignak
"""
import os
if __name__ == '__main__':
    for directory, subdirectories, files in os.walk('.'):
        for n1 in files:
            if "." in n1 and '.py' not in n1:
                n2 = n1[:-4]+'_done'+n1[-4:]
                line = f'ffmpeg.exe -i "{n1}" -vf subtitles="{n1}" -acodec copy -map 0:0 -map 0:1 "{n2}"'
                print(n2)
                os.system(line)
                if not os.path.exists(n2):
                    print("Error on :", n1, ':', n2, "doesn't exist")
