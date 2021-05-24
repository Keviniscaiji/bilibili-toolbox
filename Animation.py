import requests
from bs4 import BeautifulSoup
from Printing import Printing
from datetime import datetime
import os
import json

class Animation(object):

    header = {
        "Referer": "",
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
        s = requests.get(self.url, headers=Animation.header)
        if s.status_code == 200:
            animelist = s.json()['data']['list']
            with Printing() as xs:
                for item in animelist:
                    title = item['title']
                    order = item['order']
                    badge = item['badge']
                    index = item['index_show']
                    link = item['link']
                    image_url = item['cover']
                    filename = self.save_image(image_url)
                    content = title+"\t"+order+"\n"+index+"\t"+badge + \
                        "\n番剧链接："+link+"\n封面链接："+image_url + \
                        "\n封面存放位置:"+self.dir + '/'+filename+"\n"
                    print(content)
                    xs.write(content)

    def save_image(self, image_url):
        image = self.s.get(image_url, headers=Animation.header)
        now = datetime.now()
        suffix = now.strftime('%Y%m%d_%H%M')
        name = "img_%s_%d.jpg" % (suffix, self.idx)
        self.idx += 1
        with open(self.dir + '/' + name, 'wb') as file:
            file.write(image.content)
        return name

if __name__ == "__main__":

    while True:
        inp = None
        try:
            inp = int(input("爬取数量："))
        except:
            pass
        if type(inp) == int:
            if inp >= 3142:
                print("超出范围")
                continue
            num = inp
            break
        if inp == None:
            num = 20
            break
    url = "https://api.bilibili.com/pgc/season/index/result?season_version=-1&area=-1&is_finish=-1&copyright=-1&season_status=-1&season_month=-1&year=-1&style_id=-1&order=3&st=1&sort=0&page=1&season_type=1&pagesize=%d&type=1" %num
    Animation(url,"./图片").spider()
