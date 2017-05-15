# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 12:13:11 2016

@author: Rignak
"""

import urllib
from datetime import timedelta, date, datetime
from time import sleep

str1 = "http://sonohara.donmai.us/counts/posts.json?tags="
f = open("../Danbooru_Codes.txt")
api_key = f.readline().split()[1]
username = f.readline().split()[1]
f.close()

def NbTags(tags):
    request = str1 + tags + '&login=' + username + '&api_key=' + api_key
    e = True
    while e:
        try:
            e = False
            page = urllib.request.urlopen(request)
        except urllib.error.HTTPError:
            print('Spam?')
            sleep(300)
            e = True

    bytespage = page.read()
    deleted_number = int(bytespage.decode('utf-8')[21:-2])
    return deleted_number



if __name__ == '__main__':
    f = open("../Danbooru_Codes.txt")
    api_key = f.readline().split()[1]
    username = f.readline().split()[1]
    f.close()

    begin = datetime.now()
    mini = 0
    maxi = 30
    file = open('result.txt', 'w')
    for i in range(mini, maxi):
        res = str(date.today() - timedelta(days=i)) + " "
        tag_date = "%20age:" + str(i) + "d"
        upload_number = NbTags("approver:any" + tag_date)
        if i < 4:
            upload_number += NbTags("status:pending"+tag_date)
        if upload_number == 0:
            deleted_number = 0
            ratio = 1
        else:
            deleted_number = NbTags("status:deleted%20approver:none" + tag_date)
            upload_number += deleted_number
            ratio = deleted_number/upload_number
        res += str(ratio).replace('.', ',') + " "
        res += str(upload_number) + " "
        if i<620:
            rignak_number = NbTags("user:" + username + "%20status:all" + tag_date)
            if rignak_number == 0:
                rignak_del = 0
            else:
                rignak_del = NbTags("user:rignak%20status:deleted" + tag_date)
            res += str(rignak_number) + " "  # rignak_number
            res += str(rignak_del)  # rignak_deleted

        t_mean = (datetime.now()-begin)/(i+1)
        print(res)
