# -*- coding: utf-8 -*-m

"""
Created : 26/08/2016
Python version : 3.5
@author: Rignak
"""

from os.path import join
from os import remove, rename

root = "../files"
list_T = ["T1.txt", "T2.txt", "T3.txt", "T4.txt", "TP.txt"]
list_T = [join(root, 'tags', e) for e in list_T]
list_L = ["L1.txt", "L2.txt", "L3.txt", "L4.txt", "LP.txt"]
list_L = [join(root, 'links', e) for e in list_L]
list_HTML = ["F1.html", "F2.html", "F3.html", "F4.html", "FP.html"]
list_HTML = [join(root,'html', e) for e in list_HTML]

# Create a list of error to correct
error_fname = "error.txt"
dic_error = {}
error_f = open(join(root, error_fname), "r")
for line in error_f:
    if len(line) > 3:
        l = line.split('\t')
        dic_error[l[0]] = l[1][:-2]

banned_fname = "banned_artist.txt"
dic_banned = {}
banned_f = open(join(root, banned_fname), "r")
for line in banned_f:
    dic_banned[line[:-1]] = "True"
global number_replacements
number_replacements = 0


def CorrectorSample(url_sample):
    """Return the url of the picture from the sample
    Input:
    url_sample - string, the url in the .html or .txt

    Output:
    url_pict - string, the url of the image"""
    if "g.hitomi" in url_sample:
        return url_sample.replace("g.hitomi", "a.hitomi")
    if "sample" in url_sample:
        return url_sample.replace("sample", "jpeg")
    if "i.hitomi" in url_sample:
        return url_sample.replace("i.hitomi", "a.hitomi")
    if "twimg" in url_sample:
        return url_sample.replace(":large", ':orig')
    return url_sample

def IsBanned(tags):
    l = tags.split()
    if len(l)<3:
        print(l)
    for tag in l:
        if tag in dic_banned:
            return True
    return False

def ReplaceAll(text, dic_error):
    """Correct line with the dictionnary
    Input:
    text - A string
    dic_error - A dictionnary (error : corrected_string)

    Output:
    text - A corrected string"""
    global number_replacements
    for i, j in dic_error.items():
        text2 = text.replace(i, j)
        if text2 != text:
            number_replacements += 1
            text = text2
    return text


def DelLine(list_n):
    """Delete line in the html file
    Input:
    list_n - A list of str, number of lines to delete in each file"""
    while len(list_n) < len(list_HTML):
        list_n.append(0)
    for i in range(len(list_HTML)):
        newHTML = open(list_HTML[i] + '~', 'w')
        oldHTML = open(list_HTML[i], 'r')
        j = 0
        for line in oldHTML:
            if j >= int(list_n[i]):
                newHTML.write(line)
            j = j + 1
        oldHTML.close()
        newHTML.close()
        remove(list_HTML[i])
        rename(list_HTML[i] + '~', list_HTML[i])
    return


def TrimHTML():
    """Delete lines with the url of the pictures listed in trim.txt"""
    trim_f = open(join(root, "trim.txt"), 'r')
    list_url = []
    for line in trim_f:
        if line:
            list_url.append(line[:-1])

    rem = 0
    for i in range(len(list_HTML)):
        newHTML = open(list_HTML[i] + '~', 'w')
        oldHTML = open(list_HTML[i], 'r')
        for line in oldHTML:
            suppr = 0
            for url in list_url:
                if url in line:
                    suppr = 1
                    rem += 1
            if suppr == 0:
                newHTML.write(line)
        oldHTML.close()
        newHTML.close()
        remove(list_HTML[i])
        rename(list_HTML[i] + '~', list_HTML[i])
    print("Number of trimmed url :", rem)
    return


def GenerateTXT():
    """Creation of two .txt (url and tags) for each .html"""
    print("Generation of .txt")
    for i in range(len(list_T)):
        file = open(list_HTML[i], 'r')
        fileT = open(list_T[i], 'w')
        fileL = open(list_L[i], 'w')
        for line in file:

            try:
                lineL = line.split("\"")[-2] + "\n"
                fileL.write(CorrectorSample(lineL))
                lineT = line.split("\"")[-1][2:] + "--\n"
                fileT.write(ReplaceAll(lineT, dic_error))
            except:
                continue
    global number_replacements
    print('Number of remplacements :',number_replacements)
    return


def GenerateHTML():
    """Creation of .html for each duo of .txt"""
    print("Generation of .html")
    banned = 0
    for i in range(len(list_T)):
        file = open(list_HTML[i], 'w')
        fileT = open(list_T[i], 'r')
        fileL = open(list_L[i], 'r')

        for lineL in fileL:
            lineT = fileT.readline()
            lineT = lineT.replace("\n", '')
            fileT.readline()
            if IsBanned(lineT):
                banned += 1
                print(lineL, 'Banned\n')
                continue
            l = '<A HREF="' + CorrectorSample(lineL[:-1]) + '"> ' \
            + ReplaceAll(lineT, dic_error) + '<br></br> \n'
            l = l.replace('<br></br><br></br>','<br></br>')
            l = l.replace('<br></br> <br></br>','<br></br>')
            file.write(l)

    global number_replacements
    print('Number of deleted :', banned)
    print('Number of remplacements :',number_replacements)
    return

def CountLine():
    """Count the number of line of each .txt"""
    s = 0
    for file in list_L:
        j = 0
        current = open(file, 'r')
        for line in current:
            j += 1
        s += j
        print(j)
    print(s)
    return


if __name__ == '__main__':
    print("Case 1 : Generate HTML")
    print("Case 2 : Generate TXT")
    print("Case 3 : Delete lines from trim.txt")
    print("Case 4 : Delete n, m, k, l, p first line")
    print("Case 5 : Count the line in each link file")
    case = int(input('Choisir un mode : '))
    if case == 1:
        GenerateHTML()
    elif case == 2:
        GenerateTXT()
    elif case == 3:
        TrimHTML()
        GenerateTXT()
    elif case == 4:
        list_n = input("How many line to delete? ")
        DelLine(list_n.split())
        GenerateTXT()
    elif case == 5:
        CountLine()