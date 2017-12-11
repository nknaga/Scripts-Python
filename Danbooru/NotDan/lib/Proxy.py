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
    if n == 1: ip, port = "165.227.53.107", 80
    elif n == 2: ip, port = "40.85.184.189", 8080
    elif n == 3: ip, port = "35.196.18.239", 80
    elif n == 4: ip, port = "13.82.232.37", 8080
    elif n == 5: ip, port = "67.205.178.183", 55555
    elif n == 6: ip, port = "209.126.106.225", 8799
    elif n == 7: ip, port = "52.164.244.34", 8080
    elif n == 8: ip, port = "209.126.102.151", 8888
    elif n == 9: ip, port = "192.240.150.133", 8080
    elif n == 10: ip, port = "96.71.40.129", 3128
    elif n == 11: ip, port = "147.135.210.114", 54566
    elif n == 12: ip, port = "54.36.182.96", 3128
    elif n == 13: ip, port = "167.114.148.5", 3128
    elif n == 14: ip, port = "67.78.143.182", 8080
    elif n == 15: ip, port = "165.227.124.187", 3128
    elif n == 16: ip, port = "50.59.162.78", 8088
    elif n == 17: ip, port = "188.165.194.110", 8888
    elif n == 18: ip, port = "213.174.123.194", 3128
    elif n == 19: ip, port = "217.182.76.229", 8888
    elif n == 20: ip, port = "163.172.211.176", 3128
    elif n == 21: ip, port = "51.15.202.250", 3128
    elif n == 22: ip, port = "51.254.33.179", 3128
    elif n == 23: ip, port = "163.172.220.221", 8888
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
        except Exception as e:
            print(n,': Bad Proxy', e)
            return False

def TestProxy():
    from datetime import datetime
    res = {}
    n = 23
    for i in range(1, n+1):
        begin = datetime.now()
        config = SetProxy(i, test=True)
        if config:
            res[i] = (datetime.now()-begin)
            print(i, res[i])
    return min(res, key=res.get)


if __name__ == '__main__':
    print(TestProxy())