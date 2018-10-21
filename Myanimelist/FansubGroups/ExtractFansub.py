# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 13:25:26 2018

@author: Rignak
"""


import bs4 as BeautifulSoup
from os.path import join, splitext
from os import listdir
import json

def IndividualFansub(filename):
    with open(filename, encoding="ISO-8859-1") as file:
        soup = soup = BeautifulSoup.BeautifulSoup(file, "lxml")
    print(filename)
    table = soup.find('td', {'class':'borderClass'})
    if table:
        divs = table.find_all('div', {'class':'spaceit_pad'})
        projects = table.find_all('div', {'style':"border-width: 0; margin: 12px 0 0 0;"})

        fansub = {}
        fansub['name'] = table.contents[3][3:-3]
        fansub['shortname'] = table.contents[8][3:-3]
        fansub['IRC'] = table.contents[13][3:-3]
        fansub['language'] = table.contents[18][3:-3]
        if divs:
            fansub['positiveOpinion'] = int(divs[0].find('strong').text)
            fansub['negativeOpinion'] = int(divs[1].find('strong').text)
        fansub['projects'] = [IndividualProject(project) for project in projects]
    else:
        return {}
    return fansub

def IndividualProject(project):
    anime = {}
    anime['name'] = project.find('strong').text
    anime['id'] = int(project.find('a')['href'].split('=')[-1])
    if len(project.find_all('small'))==2:
        opinions = project.find_all('small')[1].text.split()
        anime['positiveOpinion'] = int(opinions[0])
        anime['opinion'] = int(opinions[2])
    anime['comments'] = []
    for comment in project.find_all('div')[2:]:
        anime['comments'].append(comment.text)
    return anime

if __name__ == '__main__':
    fansubs = {}
    for filename in listdir('archives'):
        number = splitext(filename)[0]
        filename = join('archives', filename)
        fansubs[int(number)] = IndividualFansub(filename)

    with open('fansubs.json', 'w') as file:
        json.dump(fansubs, file, sort_keys=True, indent=4)