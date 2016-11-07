# -*- coding: utf-8 -*-
"""
    Author: Rignak
    Python version: 3.5
"""
from PIL import Image
from os import remove, rename, walk, stat
from os.path import join
import datetime
import math
import requests

standart_root = 'E:\Mes images\Anime - Manga\Art'
waifu_root = 'E:\Telechargements\Anime\Waifu'

max_dim = pow(1500, 2)

def Alt0160():
    """Add insecable space before 'Duo' and 'White' folder"""
    print("--------------")
    print("Alt0160 begin")
    alldirs = []
    for root, dirs, files in walk(standart_root):
        for folder in dirs:
            if folder.startswith("White") or folder.startswith("Duo"):
                alldirs.append((join(root, folder), join(root, " " + folder)))
    alldirs.sort()
    alldirs.reverse()
    for i in range(len(alldirs)):
        print(alldirs[i][0])
    for i in range(len(alldirs)):
        try:
            rename(alldirs[i][0], alldirs[i][1])
        except FileExistsError:
            print("Check : ", alldirs[i][1])

    print("Done for", len(alldirs), "folders")


def ListAllFiles():
    """Return the list of all the files in standart_root"""
    print("--------------")
    print("ListAllFiles begin")
    list_file = []
    for root, dirs, files in walk(standart_root):
        for name in files:
            T = stat(join(root, name)).st_mtime
            T = datetime.date.fromtimestamp(T)
            list_file.append(join(root, name))
    print(len(list_file), "files found")
    return list_file


def ListThumbnail(list_file):
    """Liste file to Thumbnail"""
    print("--------------")
    print("ListThumbnail begin")
    list_thumbnail = []
    for file in list_file:
        im = Image.open(file)
        width, height = im.size
        dim = width * height
        if (max_dim < dim) and (3 * max_dim > dim):
            list_thumbnail.append(file)
        im.close()
    print(len(list_thumbnail), "files found")
    return list_thumbnail


def ListWaifu(list_file):
    """List file to Waifu"""
    print("--------------")
    print("ListWaifu begin")
    list_waifu = []
    for file in list_file:
        im = Image.open(file)
        width, height = im.size
        dim = width * height
        if (max_dim >= dim):
            list_waifu.append(file)
        im.close()
    print(len(list_waifu), "files found")
    return list_waifu


def LaunchWaifu(list_waifu):
    print("--------------")
    print("Launch_Waifu2x begin")
    begin = datetime.datetime.now()
    for i in range(len(list_waifu)):
        file = list_waifu[i]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
        files = {'file':  (file.split('\\')[-1], open(file, 'rb'))}
        payload = {'scale': 2, 'style': 'art', 'noise': 0}

        r = requests.post('http://waifu2x.udp.jp/api', files=files,
                          data=payload, headers=headers, stream=True)
        if len(r.content)>400:
            with open(join(waifu_root, file.split('\\')[-1][:-4] + '.png'), 'wb') as out_file:
                out_file.write(r.content)
            out_file.close()
            print(i+1, "on", len(list_waifu), '|',
                  (datetime.datetime.now() - begin) / (i + 1) * len(list_waifu) + begin)
    return


def Rem_Waifu():
    print("--------------")
    print("Rem_Waifu Begin")
    """Remove Waifu2x in the name and convert to png"""
    begin = datetime.datetime.now()
    for root, dirs, files in walk(waifu_root):
        for i in range(len(files)):
            name = files[i]
            newname = name[:-4] + ".jpg"
            if name != newname:
                im = Image.open(join(root, name))
                im.save(join(root, newname), format="JPEG", quality=100)
                remove(join(root, name))
                im.close()
            print(i+1, "on", len(files), '|',
                  (datetime.datetime.now() - begin)/(i + 1)*len(files) + begin)
    return


def Replace(list_file):
    """Replace the file from waifu in the right directory"""
    print("--------------")
    print("Replace Begin")
    for root, dirs, files in walk(waifu_root):
        for name in files:
            for actual_file in list_file:
                if name == actual_file.split('\\')[-1]:
                    remove(actual_file)
                    rename(join(root, name), actual_file)
    return


def Convert_to_jpg(list_file):
    """Convert png to jpg"""
    print("--------------")
    print("Convert_to_jpg Begin")
    for file in list_file:
        if file[-4:] == ".png":
            print(file)
            im = Image.open(file)
            try:
                im.save(file[:-4] + ".jpg", format="JPEG", quality=100)
            except:
                print('error:', file)
            remove(file)
            im.close()
    return


def Thumbnail(list_thumbnail):
    """Resized picture to under max_dim"""
    print("--------------")
    print("Thumbnail Begin")
    for file in list_thumbnail:
        im = Image.open(file)
        width, height = im.size
        dim = width * height
        rate = math.sqrt(max_dim / dim)
        size = (int(width * rate), int(height * rate))
        im.thumbnail(size)

        im.save(file, format="JPEG", quality=100)
        print(file)
        im.close()
    print(len(list_thumbnail), "image thumbnailed")
    return

def IsInNthRaw(x, l, n):
    "Return 1 if x is in n-th raw of l, else 0"
    for i in range(len(l)):
        if x == l[i][n]:
            return 1
    return 0

def SameName(list_file):
    """Change filename to have all files with different names"""
    print("--------------")
    print("SameName Begin")
    #list with [fullname, newname]
    list_name = []

    # Create a list a all names (only one occurence)
    for i in range(len(list_file)):
        file = list_file[i]
        name = file.split('\\')[-1]
        if IsInNthRaw(name, list_name, 1):
            newname = name
            end = name.split()[-1][-4:]
            begin = " ".join(name.split()[:-1])
            i = int(name.split()[-1][:-4])
            while IsInNthRaw(newname, list_name, 1):
                i = i + 1
                newname = begin + " " + str(i) + end
            list_name.append([file, newname])
            print(name,'->', newname)
        else:
            list_name.append([file, name])
    for i in range(len(list_name)):
        if list_name[-i][0].split('\\')[-1] != list_name[-i][1]:
            file = list_name[-i][0]
            newname = list_name[-i][1]
            rename(file,  "\\".join(file.split('\\')[:-1]) + "\\" + newname)
    return


if __name__ == '__main__':
    Alt0160()
    list_file = ListAllFiles()
    Convert_to_jpg(list_file)
    SameName(list_file)

    Rem_Waifu()
    list_file = ListAllFiles()
    Replace(list_file)
    Convert_to_jpg(list_file)
    Thumbnail(ListThumbnail(ListAllFiles()))

    list_file = ListAllFiles()
    list_waifu = ListWaifu(list_file)

    while list_waifu:
        LaunchWaifu(list_waifu)

        Rem_Waifu()
        Replace(list_file)

        list_file = ListAllFiles()
        list_waifu = ListWaifu(list_file)