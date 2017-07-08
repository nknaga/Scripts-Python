# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 18:11:08 2017

@author: Rignak
"""
from datetime import datetime
from threading import Thread
import threading
import time
from pixivpy3 import AppPixivAPI

def renew_tor():
    """Create a connexion to Tor or renew it if it already exist"""
    from stem import Signal
    from stem.control import Controller
    import socks
    import socket
    controller = Controller.from_port(port=9151)
    controller.authenticate()
    controller.signal(Signal.NEWNYM)
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1",
                          9150, True)
    socket.socket = socks.socksocket


def IndividualWritePixiv(index):
    try:
        illust_detail(index, req_auth=True)
    except Exception as e:
        print(e)

limit_active = list(range(50,300,25))
begin, limit = 30000000, 10000
index = list(range(begin, begin+limit))
global api
api = AppPixivAPI()
with open("../Pixiv_Codes.txt", 'r') as f:
    pixiv_mail = f.readline().split()[1]
    pixiv_code = f.readline().split()[1]
api.login(pixiv_mail, pixiv_code)

illust_detail = api.illust_detail
for r in limit_active:
    begin = datetime.now()
    for x in index:
        while threading.active_count() > r:
            time.sleep(0.5)
        Thread(target=IndividualWritePixiv, args=(x,)).start()
    print(r, 'threads:', (datetime.now()-begin)/limit)
