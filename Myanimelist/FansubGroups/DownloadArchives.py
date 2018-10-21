# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 08:16:33 2018

@author: Rignak
"""
import urllib
from os.path import join
from threading import Thread
import threading
import sys
import time
from datetime import datetime
import urllib.request
import shutil

def Progress(s):
    """Print a carriage return then a string

    Input:
    s -- a string"""
    sys.stdout.write('\r')
    sys.stdout.write(s+'           ')
    sys.stdout.flush()

def IndividualPage(url, file):
    i = 0
    while i < 100:
        try:
            res = urllib.request.urlopen(url)
        except urllib.error.HTTPError as err:
            if err.code in [404, 400]:
                return
        except:
            i += 1
            time.sleep(3)
            continue

        with open(file, 'wb') as out_file:
            shutil.copyfileobj(res, out_file)
            return
    else:
        print('Failed 20 times')

limit = 6100
begin = datetime.now()
maxThread = threading.active_count() + 4
for i in range(limit):
    url = f"https://web.archive.org/web/20180511221408/https://myanimelist.net/fansub-groups.php?id={i}"
    while  threading.active_count() > maxThread:
        time.sleep(0.5)
    try:
        Thread(target=IndividualPage, args=(url, join("archives", f"{i}.html"))).start()
    except Exception as e:
        Progress('                      '+str(e))
        pass

    eta = ((datetime.now()-begin)/(i+1)*limit+begin).strftime('%H:%M')
    Progress(f"{i}/{limit} - {eta}")