

from os import makedirs, walk
import urllib
import bs4 as BeautifulSoup
from datetime import datetime
from os.path import join, dirname, realpath


def EndTime(begin, i, n):
    mean_time = (datetime.now()-begin)/i
    remaining_time = mean_time*(n-i)
    end_time = datetime.now() + remaining_time
    return end_time.strftime('%H:%M')

def GetDataLink(link):
    e = 1
    while e:
        try:
            page = urllib.request.urlopen(link)
            e = 0
        except urllib.error.HTTPError:
            e = 1
            continue
        try:
            bytespage = page.read()
            soup = BeautifulSoup.BeautifulSoup(bytespage, "lxml")
            e = 0
        except:
            e = 1
    present_links = soup.find_all('a', href=True)
    return present_links


def GetDataWebsite(site):

    visited_links = []
    unvisited_links = [site]
    pictures_id = {}
    begin = datetime.now()

    while unvisited_links:
        current_link = unvisited_links[0]
        unvisited_links.pop(0)
        visited_links.append(current_link)

        present_links = GetDataLink(current_link)

        for i, data in enumerate(present_links):
            href = data['href'].split('?')[0]
            if href.startswith(site) and href not in visited_links and href not in unvisited_links:
                unvisited_links.append(href)
                continue
            if href.endswith("Render.png"):
                ID = href.split('/')[-1]
                if ID not in pictures_id:
                    pictures_id[ID] = href
                else:
                    if href.split('/')[-2][1:] > pictures_id[ID].split('/')[-2][1:]:
                        pictures_id[ID] = href
        print('V|R[P|E:', len(visited_links),'|',len(unvisited_links),'|',
              len(pictures_id),'|', EndTime(begin, len(visited_links),
                                            len(visited_links)+len(unvisited_links)),
              '|', current_link)

    pictures = [pictures_id[ID] for ID in pictures_id]
    print(pictures)
    return pictures

def Download(pictures):
    try:
        makedirs("Images")
    except Exception:
        pass
    begin = datetime.now()
    for i, url in enumerate(pictures):
        try:
            urllib.request.urlretrieve(url, "Images/" + url.split('/')[-1])
        except:
              pass
        print(i+1, "on", len(pictures), '|',EndTime(begin, i+1, len(pictures)))

if __name__ == '__main__':
    """site = "http://ors-renders.animemeeting.com/"
    Download(pictures)"""

    standartRoot = "E:\\Telechargements\\Anime\\ors\\ors"
    s = open(join(dirname(realpath(__file__)), "samples.txt"), 'r')
    pictures = []
    full = {}
    for line in s:
        pictures.append(line.split('/')[-1])
        full[pictures[-1]] = line

    f = open(join(dirname(realpath(__file__)), "txt.txt"), 'w')
    names = []
    for root, dirs, files in walk(standartRoot):
        for i, name in enumerate(files):
            if name.endswith("_noise.png"):
                name = name.replace("_noise.png", ".png")
            names.append(name)
    for name in names:
        for picture in pictures:
            if name in picture:
                #print(picture)
                l= "<DT><A HREF=\"" + full[picture][:-1] + "\"ADD_DATE=\"1487861288\">image</A>\n"
                print(l)
                f.write(l)
                continue
    f.close