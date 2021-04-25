# -*- codeing = utf-8 -*-
# @Time : 2021/3/25 8:13
# @Auther : 龚kevin
# @File : UP's video.py
# @Software: PyCharm
import requests
import json

from pip._vendor.distlib.compat import raw_input
import matplotlib.pyplot as plt

def get_up_video(UID,show,expo):
    a = []
    url = 'https://api.bilibili.com/x/space/arc/search?mid={}&ps=30&tid=0&pn=1&keyword=&order=pubdate&jsonp=jsonp'.format(UID)
    res = requests.get(url)
    json_data = json.loads(res.text)

    for i in json_data['data']['list']['vlist']:
        a.append([i['title'],i['comment'],i['play'],i['bvid']])

    list = []
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
        list.append([str(c)+". title：%s comments：%s plays：%s bvid: %s"%(b[0],b[1],b[2],b[3])])

    # print(list)

    def export_info():

        try:
            tofile = raw_input("dirname:")
            filename = raw_input("filename:")
            conbine = tofile+'\\'
            conbine = conbine+filename+".txt"

            print(conbine)
            print("r"+"\""+conbine)
            with open(conbine,"w", encoding='utf-8',) as f:
                for l in list:
                    f.writelines(l[0]+"\n");
                f.close()
        except:
            print("Please check your format")
            export_info()
        print("export success")
    if expo :
        export_info()
    if show:
        print("The producer with UID:", UID, "'s videos that posted recently(maximum 30)(sorted by plays)")
        for l in list:
            print(l[0])

if __name__ =="__main__":
    get_up_video(16001661,True,True)

