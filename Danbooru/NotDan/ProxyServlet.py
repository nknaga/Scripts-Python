# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 16:53:35 2017

@author: Rignak
"""

import socks
import socket
from pixivpy3 import AppPixivAPI


if __name__ == '__main__':
    with open("../Pixiv_Codes.txt", 'r') as f:
        pixiv_mail = f.readline().split()[1]
        pixiv_code = f.readline().split()[1]
    with open("proxy.txt", 'r') as file:
        lines = file.readlines()
    i = 0
    for line in lines:
        if i == 0:
            prefix = 'if '
        else:
            prefix = 'elif '
        prefix += 'n == '+str(i+1)+': ip, port = "'
        ip, port = line.split('\t')[0:2]
        prefix += ip + '", ' + port
        socks.setdefaultproxy(socks.HTTP, ip, int(port), True)
        socket.socket = socks.socksocket
        try:
            api = AppPixivAPI()
            api.login(pixiv_mail, pixiv_code)
            print(prefix)
            i+=1
        except Exception as e:
            pass