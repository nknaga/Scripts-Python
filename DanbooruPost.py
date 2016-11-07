# -*- coding: utf-8 -*-
"""
Created : 26/08/2016
Python version : 3.5
@author: Rignak
"""

from os.path import join
from os import remove, rename

# Declare each files wich will be used
root = "E:\Telechargements\Anime\post\data"
error_fname = "error.txt"
list_T = ["T1.txt", "T2.txt", "T3.txt", "T4.txt", "Priority.txt"]
list_L = ["L1.txt", "L2.txt", "L3.txt", "L4.txt", "LPriority.txt"]
list_HTML = []
for i in range(len(list_T)):
    list_T[i] = join(root, list_T[i])
    list_L[i] = join(root, list_L[i])
    list_HTML.append(list_T[i][:-4] + 'Advanced.html')

# Create a list of error to correct
dic_error = {}
error_f = open(join(root, error_fname), "r")
for line in error_f:
    l = line.split()
    dic_error[l[0]] = l[1]

def CorrectorSample(url_sample):
    """Return the url of the picture from the sample
    Input:
    url_sample - string, the url in the .html or .txt

    Output:
    url_pict - string, the url of the image"""

    if url_sample.startswith("https://files.yande.re/sample/"):
        return url_sample.replace('sample', 'image')
    return url_sample


def ReplaceAll(text, dic_error):
    """Correct line with the dictionnary
    Input:
    text - A string
    dic_error - A dictionnary (error : corrected_string)

    Output:
    text - A corrected string"""
    for i, j in dic_error.items():
        text = text.replace(i, j)
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
    list_url = trim_f.readline().split()
    for i in range(len(list_HTML)):
        newHTML = open(list_HTML[i] + '~', 'w')
        oldHTML = open(list_HTML[i], 'r')
        for line in oldHTML:
            suppr = 0
            for url in list_url:
                if url in line:
                    suppr = 1
            if suppr == 0:
                newHTML.write(line)
        oldHTML.close()
        newHTML.close()
        remove(list_HTML[i])
        rename(list_HTML[i] + '~', list_HTML[i])
    return


def GenerateTXT():
    """Creation of two .txt (url and tags) for each .html"""
    for i in range(len(list_T)):
        file = open(list_T[i][:-4] + 'Advanced.html', 'r')
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
    return


def GenerateHTML():
    """Creation of .html for each duo of .txt"""
    for i in range(len(list_T)):
        file = open(list_T[i][:-4] + 'Advanced.html', 'w')
        fileT = open(list_T[i], 'r')
        fileL = open(list_L[i], 'r')
        for lineL in fileL:
            lineT = fileT.readline()
            fileT.readline()
            file.write(
                '<A HREF="' + CorrectorSample(lineL[:-1]) + '"> ' + ReplaceAll(lineT, dic_error) + '<br/><br/>')
    return

def CountLine():
    """Count the number of line of each .txt"""
    i = []
    for file in list_L:
        j = 0
        current = open(file, 'r')
        for line in current:
            j += 1
        print(j)
        i.append(j)
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