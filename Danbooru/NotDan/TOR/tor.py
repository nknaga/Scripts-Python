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