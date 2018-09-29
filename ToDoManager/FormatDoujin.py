# -*- coding: utf-8 -*-
"""
Created on Sat Sep 15 18:38:56 2018

@author: Rignak
"""
import os
import re
iniRoot = 'D:\\Telechargements\\Anime\\Manga - Copie - Copie - Copie - Copie'

def StripTitle(title):
    if '[' in title:
        title = title[:title.find('[')]
    if '(' in title:
        title = title[:title.find('(')]
    if '  ' in title:
        title = title[:title.find('  ')]
    title = title.lstrip().rstrip()


    return title

def FormatName(folder):
    paro = [m.start() for m in re.finditer('\(', folder)]
    parc = [m.start() for m in re.finditer('\)', folder)]
    brao = [m.start() for m in re.finditer('\[', folder)]
    brac = [m.start() for m in re.finditer('\]', folder)]
    if len(paro) > 1 and paro[1] > brao[0] and paro[1] < brac[0]:
        i, j = paro[0], parc[0]
        source = folder[i+1:j].lstrip().rstrip()
        i, j = paro[1], parc[1]
        if "Various" in folder[i+1:j]:
            i, j = brao[0], brac[0]
        author = StripTitle(folder[i+1:j])
        title = StripTitle(folder[j+2:])
        formated = f"({author}) - {title} [{source}]"
        return formated
    elif brao and brao[0] == 0:
        if paro and paro[0] > brao[0] and paro[0] < brac[0]:
            i, j = paro[0], parc[0]
            if "Various" in folder[i+1:j]:
                i, j = brao[0], brac[0]
        else:
            i, j = brao[0], brac[0]

        author = StripTitle(folder[i+1:j])
        title = StripTitle(folder[j+2:])
        formated = f"({author}) - {title}"
        return formated
    elif paro and brac:
        i, j = paro[0], parc[0]
        source = folder[i+1:j].lstrip().rstrip()
        i, j = brao[0], brac[0]
        author = StripTitle(folder[i+1:j])
        title = StripTitle(folder[j+2:])
        formated = f"({author}) - {title} [{source}]"
        return formated
    else:
        print('unknown pattern')
        print(folder)
        print()
        return

def RenameFolders(iniRoot):
    for root, folders, files in os.walk(iniRoot):
        l = os.path.split(root)
        baseRoot = l[:-1]
        endRoot = l[-1]
        if len(files) != 0:
            formated = FormatName(endRoot)
            if formated:
                newPath = os.path.join(*baseRoot, formated)
                try:
                    os.rename(root, newPath)
                except Exception as e:
                    print(e, root)

def IntegerNamefile(iniRoot):
    for root, folders, files in os.walk(iniRoot):
        if files == ['desktop.ini']:
            continue
        for i, file in enumerate(files):
            ext = os.path.splitext(file)[1]
            oldname = os.path.join(root, file)
            if i == 0:
                newname = os.path.join(root, f"{i}cover__done{ext}")
            else:
                newname = os.path.join(root, f"{i}__done{ext}")
            try:
                os.rename(oldname, newname)
            except Exception as e:
                print(e, oldname, newname)


def RemoveDone(iniRoot):
    for root, folders, files in os.walk(iniRoot):
        maxLen = 0
        for file in files:
            l = len(file)
            if maxLen < l:
                maxLen = l
        for file in files:
            newname = file
            while len(newname) < maxLen:
                newname = '0'+newname
            path = os.path.join(root, file)
            newpath = os.path.join(root, newname).replace('__done.', '.')
            os.rename(path, newpath)

RenameFolders(iniRoot)
IntegerNamefile(iniRoot)
RemoveDone(iniRoot)
