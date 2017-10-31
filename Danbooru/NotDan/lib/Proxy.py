# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 19:47:58 2017

@author: Rignak
"""

import socks
import socket
from stem import Signal
from stem.control import Controller
from pixivpy3 import AppPixivAPI
import os

controller = None
connexion = False

def renew_tor():
    """Create a connexion to Tor or renew it if it already exist"""
    global connexion
    global controller
    if not connexion:
        controller = Controller.from_port(port=9151)
        connexion = True
    controller.authenticate()
    controller.signal(Signal.NEWNYM)
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150, True)
    socket.socket = socks.socksocket

def SetProxy(n, test=False):
    if n == 1: ip, port = "163.172.217.103", 3128
    elif n == 2: ip, port = "82.2.102.83", 8080
    elif n == 3: ip, port = "51.254.33.179", 3128
    elif n == 4: ip, port = "145.239.137.83", 3128
    elif n == 5: ip, port = "109.203.124.226", 80
    elif n == 6: ip, port = "145.239.80.105", 3128
    elif n == 7: ip, port = "163.172.93.129", 3128
    elif n == 8: ip, port = "167.114.148.5", 3128
    elif n == 9: ip, port = "149.56.226.31", 80
    elif n == 10: ip, port = "50.117.47.206", 3128
    elif n == 11: ip, port = "173.212.245.54", 3128
    elif n == 12: ip, port = "69.30.212.186", 3128
    elif n == 13: ip, port = "35.198.2.63", 80
    elif n == 14: ip, port = "35.198.2.63", 8080
    elif n == 15: ip, port = "138.197.232.80", 8080
    elif n == 16: ip, port = "173.212.246.178", 3128
    elif n == 17: ip, port = "149.56.226.31", 3128
    elif n == 18: ip, port = "50.59.162.78", 8088
    elif n == 19: ip, port = "52.178.197.34", 3128
    elif n == 20: ip, port = "188.165.194.110", 8888
    elif n == 21: ip, port = "213.174.123.194", 3128
    elif n == 22: ip, port = "212.47.252.49", 3128
    elif n == -1: renew_tor()
    if n < 1: return
    socks.setdefaultproxy(socks.HTTP, ip, port, True)
    socket.socket = socks.socksocket
    if test:
        try:
            namefile = ["../../Pixiv_Codes.txt", "../Pixiv_Codes.txt"][os.path.isfile("../Pixiv_Codes.txt")]
            with open(namefile, 'r') as f:
                pixiv_mail = f.readline().split()[1]
                pixiv_code = f.readline().split()[1]
            api = AppPixivAPI()
            api.login(pixiv_mail, pixiv_code)
            return(True)
        except Exception:
            print(n,': Bad Proxy')
            return False

def TestProxy():
    from datetime import datetime
    res = {}
    n = 22
    for i in range(1, n+1):
        begin = datetime.now()
        config = SetProxy(i, test=True)
        if config:
            res[i] = (datetime.now()-begin)
            print(i, res[i])
    return min(res, key=res.get)


if __name__ == '__main__':
    print(TestProxy())