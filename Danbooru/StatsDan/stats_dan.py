# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 12:13:11 2016

@author: Rignak
"""


from datetime import timedelta, date
from stats_functions import Lib

if __name__ == '__main__':
    api_key, username = Lib.DanbooruCodes()
    mini = 0
    maxi = int(input("How many data ? "))
    file = open('result.txt', 'w')
    for i in range(mini, maxi):
        tag_date = f"%20age:{i}d"
        upload_number = Lib.NbTags("approver:any" + tag_date, username, api_key)

        if i < 4:
            upload_number += Lib.NbTags("status:pending"+tag_date, username, api_key)
        if upload_number == 0:
            deleted_number = 0
            ratio = 1
        else:
            deleted_number = Lib.NbTags("status:deleted%20approver:none" + tag_date, username, api_key)
            upload_number += deleted_number
            ratio = deleted_number/upload_number
        res = f"{date.today() - timedelta(days=i)} {ratio} {upload_number} ".replace('.', ',')
        user_number = Lib.NbTags(f"user:{username} status:all {tag_date}", username, api_key)
        if user_number == 0:
            user_del = 0
        else:
            user_del = Lib.NbTags(f"user:{username} status:deleted {tag_date}", username, api_key)
        res += f" {user_number} {user_del}"
        total = Lib.NbTags("status:any" + tag_date, username, api_key)
        res += f" {total}"
        print(res)
