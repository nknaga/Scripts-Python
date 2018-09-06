# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 21:30:55 2018

@author: Rignak
"""

import subprocess
import time

for i in range(100):
    time.sleep(60)
    subprocess.call(["taskkill", "/f", "/im", "dllhost.exe"])
    print(i)