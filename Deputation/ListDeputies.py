# -*- coding: utf-8 -*-
"""
Created on Sat Sep  8 16:47:02 2018

@author: Rignak
"""

import bs4 as BeautifulSoup
import urllib
import json
import os
import sys

currentFile = 'currentDeputies.txt'
url = "http://www2.assemblee-nationale.fr/deputes/liste/alphabetique"
archivesFolder = 'archives'
log = 'log.txt'

def RecordDeputies():
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup.BeautifulSoup(page, "lxml")
    deputies = soup.find_all("option")
    deputies = [deputy.text for deputy in deputies]
    return deputies

def UpdateList():
    archives = os.listdir(archivesFolder)
    last = archives[-1]
    with open(currentFile, 'r') as file:
        current = json.load(file)
    deputies = RecordDeputies()
    print('Update')
    if deputies != current:
        i = str(int(last[:-4])+1)+'.txt'
        with open(os.path.join(archivesFolder, i), 'w') as file:
            json.dump(current, file, sort_keys=True, indent=4)
        with open(currentFile, 'w') as file:
            json.dump(deputies, file, sort_keys=True, indent=4)


def CompareList():
    archives = os.listdir(archivesFolder)
    last = archives[-1]
    with open(os.path.join(archivesFolder, last), 'r') as file:
        old = json.load(file)
    with open(currentFile, 'r') as file:
        current = json.load(file)
    added = [deputy for deputy in current if deputy not in old]
    removed=[deputy for deputy in old if deputy not in current]

    return added, removed

def PrintDiff(added, removed):
    print('Députés ajoutés :')
    for deputy in added:
        print(deputy)

    print()
    print('Députés retirés :')
    for deputy in removed:
        print(deputy)


def main():
    RecordDeputies()


if __name__ == '__main__':
    if sys.argv[1] == 'diff':
        added, removed = CompareList()
        PrintDiff(added, removed)
    elif sys.argv[1] == 'update':
        UpdateList()