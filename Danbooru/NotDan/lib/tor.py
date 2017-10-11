# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 19:47:58 2017

@author: Rignak
"""

import socks
import socket
from stem import Signal
from stem.control import Controller


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
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1",
                          9150, True)
    socket.socket = socks.socksocket

def SetProxy(n):
    if n == 1:
        ip, port = "64.173.224.142", 9991
    elif n == 2:
        ip, port = "174.138.54.111", 3128
    elif n == 3:
        ip, port = "165.227.66.106", 8080
    elif n == 4:
        ip, port = "35.200.45.152", 3128
    elif n == 5:
        ip, port = '46.105.101.88', 3128
    elif n == -1:
        renew_tor()
    if n < 1:
        return
    socks.setdefaultproxy(socks.HTTP, ip, port, True)
    socket.socket = socks.socksocket