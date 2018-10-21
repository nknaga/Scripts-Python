# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 21:30:55 2018

@author: Rignak
"""

import subprocess
import time

while True:
    time.sleep(60)
    subprocess.call(["taskkill", "/f", "/im", "dllhost.exe"])