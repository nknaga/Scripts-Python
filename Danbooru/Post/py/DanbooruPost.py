# -*- coding: utf-8 -*-m

"""
Created : 26/08/2016
Python version : 3.5
@author: Rignak
"""
from os.path import join
from os import remove, rename

root = join('..', 'files')
list_T =    [join(root, 'tags',  f"T{i}.txt") for i in range(1, 5)]
list_L =    [join(root, 'links', f"L{i}.txt") for i in range(1, 5)]
list_HTML = [join(root, 'html',  f"F{i}.html") for i in range(1, 5)]

# Create a list of error to correct
lst_error = []
error_f = open(join(root, "error.txt"), "r")
for line in error_f:
    if len(line) > 3:
        l = line.split('\t')
        try:
            lst_error.append([l[0],l[1].split('\n')[0]])
        except:
            print(l)

dic_banned = {}
banned_f = open(join(root, "banned_artist.txt"), "r")
for line in banned_f:
    dic_banned[line[:-1]] = True


def CorrectorSample(url_sample):
    """Return the url of the picture from the sample
    Input:
    url_sample - string, the url in the .html or .txt

    Output:
    url_pict - string, the url of the image"""
    if "g.hitomi" in url_sample:
        return url_sample.replace("g.hitomi", "a.hitomi")
    if "sample" in url_sample:
        return url_sample.replace("sample", "image")
    if "i.hitomi" in url_sample:
        return url_sample.replace("i.hitomi", "a.hitomi")
    if "twimg" in url_sample:
        return url_sample.replace(":large", ':orig')
    return url_sample

def IsBanned(tags):
    l = tags.split()
    for tag in l:
        if tag in dic_banned:
            return tag
    return False

def ReplaceAll(text, lst_error):
    """Correct line with the dictionnary
    Input:
    text - A string
    lst_error - A list ([[error,corrected_string]])

    Output:
    text - A corrected string"""
    number_replacements = 0
    text = ' ' + text + ' '
    for k in range(10):
        text3 = text
        for i, j in lst_error:
            text2 = text.replace(i, j)
            if text2 != text:
                if i != '  ':
                    number_replacements += 1
                if k>3:
                    print('multiple? ','|'+str(i)+'|'+str(j)+'|')
                text = text2
        if text == text3:
            break
    l = []
    for tag in text.split():
        if tag not in l:
            l.append(tag)
    text = ' '.join(l)+ ' '
    return text, number_replacements


def DelLine(list_n):
    """Delete line in the html file
    Input:
    list_n - A list of str, number of lines to delete in each file"""
    while len(list_n) < len(list_HTML):
        list_n.append(0)
    for i in range(len(list_HTML)):
        newHTML = open(list_HTML[i] + '+', 'w', encoding="utf-8")
        oldHTML = open(list_HTML[i], 'r', encoding="utf-8")
        j = 0
        for line in oldHTML:
            if j >= int(list_n[i]):
                newHTML.write(line)
            j = j + 1
        oldHTML.close()
        newHTML.close()
        remove(list_HTML[i] + '~')
        rename(list_HTML[i], list_HTML[i] + '~')
        rename(list_HTML[i] + '+', list_HTML[i])
    return


def PrintUrl(list_n):
    while len(list_n) < len(list_HTML):
        list_n.append(0)
    lines = []
    for i,file in enumerate(list_HTML[:-1]):
        lines += open(file, 'r').readlines()[:int(list_n[i])]
    for line in lines:
        url = line.split('"')[1]
        print('https://danbooru.donmai.us/uploads/new?url='+url)
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
        newHTML = open(list_HTML[i] + '~', 'w', encoding="utf-8")
        oldHTML = open(list_HTML[i], 'r', encoding="utf-8")
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
    number_replacements = 0
    for file in list_T:
        try:
            remove(file[:-4] + '_old.txt')
        except:
            pass
        rename(file, file[:-4] + '_old.txt')
    for i in range(len(list_T)):
        file = open(list_HTML[i], 'r')
        fileT = open(list_T[i], 'w')
        fileL = open(list_L[i], 'w')
        for line in file:
            try:
                lineL = line.split("\"")[-2]+ "\n"
                lineT = line.split("<")[1].split('>')[1][:-1]
                fileL.write(CorrectorSample(lineL))
                l, nr = ReplaceAll(lineT, lst_error)
                fileT.write(l)
                number_replacements += nr
                fileT.write('\n\n')
            except Exception as e:
                print(e)
    print('Number of remplacements :',number_replacements)
    return


def GenerateHTML():
    """Creation of .html for each duo of .txt"""
    print("Generation of .html")
    banned = 0
    number_replacements = 0
    for i in range(len(list_T)):
        file = open(list_HTML[i], 'w')
        fileT = open(list_T[i], 'r')
        fileL = open(list_L[i], 'r')

        for lineL in fileL:
            if 'yande.re' in lineL:
                if '%20' in lineL:
                    lineL = lineL.split('/')
                    lineL = '/'.join(lineL[:-1]+[lineL[-1].split('%20')[1]+lineL[-1][-5:]])
            lineT = fileT.readline()
            lineT = lineT.replace("\n", '')
            fileT.readline()
            isbanned = IsBanned(lineT)
            if isbanned:
                banned += 1
                print(lineL, 'Banned because of :', isbanned, '\n')
            else:
                ele, nr = ReplaceAll(lineT, lst_error)
                l = '<A HREF="' + CorrectorSample(lineL[:-1]) + '"> ' \
                    + ele + '<br></br> \n'
                number_replacements += nr
                l = l.replace('<br></br><br></br>','<br></br>')
                l = l.replace('<br></br> <br></br>','<br></br>')
                file.write(l)

    print('Number of deleted :', banned)
    print('Number of remplacements :',number_replacements)
    return


def CountLine():
    """Count the number of line of each .txt"""
    s = 0
    for file in list_HTML:
        current = len(open(file, 'r', encoding='utf-8').readlines())
        s+= current
        print(current)
    print(s)
    return


def CheckTags():
    tags = []
    for file in list_HTML:
        for line in open(file, 'r', encoding="ISO-8859-1"):
            for tag in line.split('">')[-1].split():
                tags.append(tag)
    tags = set(tags)
    true_tags = []
    with open("../../AddTags/tags.txt", 'r') as file:
        for line in file:
            true_tags.append(line[:-1])
    true_tags = set(true_tags)
    ok = ["-", "<br>"]
    prefix =['copy', 'art', 'char', 'pool', 'rating', 'parent', 'source']
    for tag in [tag for tag in tags if tag not in true_tags and not any([tag.startswith(i) for i in ok]) and not tag.split(':')[0] in prefix]:
        print(tag)


def CountTags():
    tags = []
    nb = 0
    for file in list_HTML[:-1]:
        for line in open(file, 'r'):
            for tag in line.split('">')[-1].split():
                if tag != '<br></br>':
                    tags.append(tag)
            nb += 1
    print('Mean number of tags:', round(len(tags)/nb, 1))
    print('Variety:', len(set(tags)), 'unique on', len(tags))
    return


if __name__ == '__main__':
    print("Case 1 : Generate HTML")
    print("Case 2 : Generate TXT")
    print("Case 3 : Delete lines from trim.txt")
    print("Case 4 : Delete n, m, k, l, p first line")
    print("Case 5 : Count the line in each link file")
    print("Case 6 : Print unknown tags")
    print("Case 7 : Print urls to post")
    print("Case 8 : Count the mean number of tags")
    case = int(input('Choisir un mode : '))
    if case == 1:
        GenerateHTML()
    elif case == 2:
        GenerateTXT()
    elif case == 3:
        TrimHTML()
        GenerateTXT()
    elif case == 4:
        list_n = input("How many lines to delete? ")
        DelLine(list_n.split())
        GenerateTXT()
    elif case == 5:
        CountLine()
    elif case == 6:
        CheckTags()
    elif case == 7:
        list_n = input("How many lines to show? ")
        PrintUrl(list_n.split())
    elif case == 8:
        CountTags()
