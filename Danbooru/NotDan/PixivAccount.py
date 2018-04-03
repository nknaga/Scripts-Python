# -*- coding: utf-8 -*-
"""
Created on Sun Oct  8 13:09:27 2017

@author: Rignak
"""
from pixivpy3 import AppPixivAPI
from datetime import datetime
from threading import Thread
import threading

import socks
import socket
import time

from sys import stdout
def Progress(s):
    stdout.write('\r')
    stdout.write(s+'           ')
    stdout.flush()

def GetId():
    with open("../Pixiv_Codes.txt", 'r') as f:
        pixiv_mail = f.readline().split()[1]
        pixiv_code = f.readline().split()[1]
    return pixiv_mail, pixiv_code


def foo2(api,mode=0):
    json = (api.illust_detail(59381952, req_auth=True))
    t_block = datetime.now()
    block =False
    while 'error' in json and 'Rate Limit' == json['error']['message']:
        time.sleep(1)
        block = True
        json = api.illust_detail(59381952, req_auth=True)
    if block and mode==2:
        print('time before retrieve:', datetime.now()-t_block)
    return True


def IndividualRequest():
    pixiv_mail, pixiv_code = GetId()
    api = AppPixivAPI()
    print('pixiv_mail:', pixiv_mail, 'pixiv code:',pixiv_code,'\n')
    api.login(pixiv_mail, pixiv_code)
    time = []
    for i in range(1):
        startTime= datetime.now()
        json = api.illust_detail(59381952, req_auth=True)
        print('------------------\n', json, '\n',
              [tag.name for tag in json.illust.tags] + [json.illust.user.id])
        time.append(datetime.now()-startTime)
    for t in time:
        print('Time elpased (hh:mm:ss.ms) {}'.format(t))

def TestRateLimit():
    pixiv_mail, pixiv_code = GetId()
    api = AppPixivAPI()
    api.login(pixiv_mail, pixiv_code)

    for j in [200, 150, 100, 75, 50, 40, 30, 20, 15, 10,8,6,5,4,3,2,1]:
        limit_active = j+threading.active_count()
        print('\nnumber of threads:', j)
        startTime= datetime.now()
        i_block=0
        for i in range(10000):
            m = 0
            while threading.active_count() > limit_active:
                time.sleep(0.1)
                m+=1
                if m == 20:
                    t_block = datetime.now()
                    print('\ntime before block:', t_block-startTime, '\niteration until block:', i-i_block,
                          '\noverall mean time:', (datetime.now()-startTime)/(i+1))
                    i_block = i
                    foo2(api, mode = 2)
                    break
            if m==20:
                break
            Thread(target=foo2,args=(api,)).start()
            Progress('mean time: ' +str((datetime.now()-startTime)/(i+1))+ ' '+str(i))



def TestAccount():
    pixiv_code = 'password'
    base_mail = ['john_smith','@gmail.com']
    api = AppPixivAPI()
    for i in range(126,141):
        pixiv_mail = str(i).join(base_mail)
        try:
            api.login(pixiv_mail, pixiv_code)
        except Exception as e:
            print(pixiv_mail, pixiv_code, 'Login Error', e)
            continue
        json = api.illust_detail(59381952, req_auth=True)
        if 'illust' in json:
            print(pixiv_mail, [tag.name for tag in json.illust.tags])
        elif 'error' in json:
            print(pixiv_mail, json['error']['message'])
    pass

if __name__ == '__main__':
    print('mode 0 : unique request\nmode 1 : test rate limit\nmode 2 : test accounts')
    mode = int(input('Mode ? '))
    [IndividualRequest, TestRateLimit, TestAccount][mode]()