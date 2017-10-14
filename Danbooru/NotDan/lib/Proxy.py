# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 19:47:58 2017

@author: Rignak
"""

import socks
import socket
from stem import Signal
from stem.control import Controller
import requests

controller = None
connexion = False

def renew_tor():
    """Create a connexion to Tor or renew it if it already exist"""
    global connexion
    global controller
    if not connexion:
        controller = Controller.from_port(port=9151)
        connexion = True
    controller.authenticate() and controller.signal(Signal.NEWNYM)
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
    socket.socket = socks.socksocket

def SetProxy(n, test=False):
    if n == 1: ip, port = "35.198.211.62", 80
    elif n == 2: ip, port = "35.198.219.184",3128
    elif n == 3: ip, port = "35.201.197.38",3128
    elif n == 4: ip, port = "46.105.101.88",3128
    elif n == 5: ip, port = "188.165.194.110",8888
    elif n == 6: ip, port = "67.205.188.62",8080
    elif n == 7: ip, port = "185.42.221.246",80
    elif n == 8: ip, port = "35.189.225.0",80
    elif n == 9: ip, port = "52.178.197.34",3128
    elif n == 10: ip, port = "138.197.187.236",3128
    elif n == -1: renew_tor()
    if n < 1: return
    socks.setdefaultproxy(socks.HTTP, ip, port, True)
    socket.socket = socks.socksocket
    try:
        requests.get("http://www.google.fr/")
        if not test: print('Connexion OK')
        return(True)
    except Exception:
        print(n,': Bad Proxy')
        return False

def TestProxy():
    from datetime import datetime
    res = {}
    l = 1
    for i in range(1, 11):
        begin = datetime.now()
        for j in range(l):
            config = SetProxy(i, test=True)
            if not config: break
        if config: res[i] = (datetime.now()-begin)/l
    print(res)
    return min(res, key=res.get)


if __name__ == '__main__':
    print(TestProxy())