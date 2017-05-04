from os.path import join, dirname, realpath
import urllib
from WhiteFunctions import IMG
import WaifuFunctions
from os import remove

standartRoot = join(dirname(realpath(__file__)),'Gate Divine')

def Download(line, i):
    urllib.request.urlretrieve(line, join(standartRoot, "images",str(i) + line[-4:]))
    return join(standartRoot, "images",str(i) + line[-4:])

if __name__ == '__main__':
    f = open(join(standartRoot,'files.txt'))
    i = 0
    for i, line in enumerate(f):
        print(i)
        file = Download(line[:-1], i)
        WaifuFunctions.LaunchWaifu(file, scale = 2, noise = 3)
        img = IMG(file[:-4]+'_waifu'+file[-4:])
        img.Thumbnail((1024, 1024))
        img._name = file
        img.Save(ext = 'png')
        remove(file[:-4]+'_waifu'+file[-4:])
