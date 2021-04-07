# -*- codeing = utf-8 -*-
# @Time : 2021/3/29 22:26
# @Author : Li Qiyu
# @File : Animation.py
# @Software : PyCharm

import requests
from bs4 import BeautifulSoup
import os
import json



class Animation(object):

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
    }



    def __init__(self, url, directory):
        self.s = requests.Session()
        self.url = url
        self.dir = directory
        if not os.path.exists(directory):
            os.mkdir(directory)
        self.idx = 0



    def spider(self):
        s = requests.get(self.url, headers = Animation.header)
        # print(s)

        if s.status_code == 200:
            animationlist = s.json()['data']['list']

            for item in animationlist:
                title = item['title']
                order = item['order']
                badge = item['badge']
                index = item['index_show']
                link = item['link']
                url = item['cover']
                info = title + "\t" + order + "\n" + index + "\t" + badge + "\n番剧链接：" + link + "\n封面链接："+url + "\n封面存放位置:"+self.dir + '/' + "\n"
                print(info)



if __name__ == "__main__":
    while True:
        inp = None

        try:
            inp = int(input("番剧数量："))
        except:
            pass

        if type(inp) == int:
            if inp >= 3315:
                print("超出范围")
                continue
            num = inp
            break
        if inp == None:
            num = 20
            break

    # num = 20

    url = "https://api.bilibili.com/pgc/season/index/result?season_version=-1&area=-1&is_finish=-1&copyright=-1&season_status=-1&season_month=-1&year=-1&style_id=-1&order=3&st=1&sort=0&page=1&season_type=1&pagesize=%d&type=1" %num
    Animation(url,"./图片").spider()