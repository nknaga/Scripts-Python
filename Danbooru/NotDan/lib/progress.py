# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 14:07:00 2017

@author: Rignak
"""
from sys import stdout

def Progress(s):
    stdout.write('\r')
    stdout.write(s+'            ')
    stdout.flush()