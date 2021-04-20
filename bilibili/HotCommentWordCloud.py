# -*- codeing = utf-8 -*-
# @Time : 2021/4/2 10:23
# @Auther : 龚kevin
# @File : get_video_comment.py
# @Software: PyCharm
import requests
import json
import re
import jieba
import imageio
import wordcloud
import os
from PIL import Image
import configparser
from matplotlib import pyplot as plt

__all__ = ["VideoCommentWordCloud"]

class VideoCommentWordCloud(object):
    def __init__(self, headers: dict, path: str, api_path='./api.cfg'):
        self.parser = configparser.ConfigParser()
        self.parser.read(api_path)
        self.headers = headers
        self.path = path
        self.mask_path = None
        self.font_path = None
    
    def get_video_aid(self, bvid):
        url = str(self.parser.get("video", "INFO_API"))
        param = {
            'bvid':'%s'%bvid
        }
        res = requests.get(url, params=param, headers=self.headers)
        json_data = json.loads(res.text)
        return json_data['data']['aid']

    def get_hot_comment(self, bvid):
        aid = self.get_video_aid(bvid)
        x = 1
        i = 1
        data = []
        while(x<10):
            url = str(self.parser.get("video", "COMMENT_API"))
            param = {
                'type':1,
                'pn':str(x),
                'oid':str(aid)
            }
            res = requests.get(url, params=param, headers=self.headers)
            json_data = json.loads(res.text)
            x += 1
            for l in json_data['data']['replies']:
                i += 1
                data.append(l['content']['message'])
        return data

    def get_wordcloud(self, bvid):
        data = self.get_hot_comment(bvid)
        d = " ".join(data)
        s_text = re.split(
            '["\"笑哭"¨̮ 哈\`\-\=\~\!\@\#\$\%\^\&\*\(\)\_\+\[\]\{\}\;\'\\\:\"\|\<\.\/\>\<\>\?\\n1234567890abcdefghijkmlnopqrstuvwxyzABCDEFGHIJKMLNOPQRSTUVWXYZ]',
            d)

        text_list = []
        for l in s_text:
            if len(l) > 1:
                text_list.append(l)

        mytext = []
        for l in text_list:
            mytext.append(jieba.lcut_for_search(l))

        cloudtext = []
        for l in mytext:
            for i in l:
                if len(i) >= 2:
                    cloudtext.append(i)
        s = " ".join(cloudtext)
        if self.mask_path is None:
            wc = wordcloud.WordCloud(font_path=self.font_path, max_font_size=50)
        else:
            color_mask = imageio.imread(self.mask_path)
            wc = wordcloud.WordCloud(max_font_size=50, mask=color_mask)
        pic = wc.generate(s)
        wc.to_file(os.path.join(self.path, "{}_wc.png".format(bvid)))

    def set_mask_path(self, path):
        self.mask_path = path

    def set_font_path(self, path):
        self.font_path = path

if __name__ == "__main__":
    headers = {
        'Referer':'https://www.bilibili.com/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        'cookie':"",
    }
    videoCommentWordCloud = VideoCommentWordCloud(headers, "./", "../api.cfg")
    videoCommentWordCloud.set_font_path('../simhei.ttf')
    videoCommentWordCloud.get_wordcloud("BV1r7411M7Pu")
