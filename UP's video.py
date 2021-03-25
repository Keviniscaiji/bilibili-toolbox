# -*- codeing = utf-8 -*-
# @Time : 2021/3/25 8:13
# @Auther : 龚kevin
# @File : UP's video.py
# @Software: PyCharm
import requests
import json
def get_up_video(UID):
    a = []
    url = 'https://api.bilibili.com/x/space/arc/search?mid={}&ps=30&tid=0&pn=1&keyword=&order=pubdate&jsonp=jsonp'.format(UID)
    res = requests.get(url)
    json_data = json.loads(res.text)
    print("The producer with UID:",UID,"'s videos that posted recently(maximum 30)(sorted by plays)")

    for i in json_data['data']['list']['vlist']:
        a.append([i['title'],i['comment'],i['play'],i['bvid']])

    counta = 0
    while counta < len(a):
        countb = counta
        while countb < len(a) :
            if a[counta][2] < a[countb][2]:
                tema = a[countb]
                a[countb] = a[counta]
                a[counta] = tema
            countb+= 1
        counta += 1
    c = 0
    for b in a:
        c+=1
        print(c,"title：%s comments：%s plays：%s bvid: %s"%(b[0],b[1],b[2],b[3]))

get_up_video(11100920)