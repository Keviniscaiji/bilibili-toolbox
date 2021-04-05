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
from matplotlib import pyplot as plt


class get_video_comment:
    def tans_bvid(bvid):
        url = 'https://api.bilibili.com/x/web-interface/view?bvid={}'.format(bvid)
        res = requests.get(url)
        json_data = json.loads(res.text)
        print(json_data['data']['aid'])
        return json_data['data']['aid']
    # in general the user can only get the bvid of the video but the API
    # require aid of the video so we need to transform it.
    def get_hot_comment(BVID,PICDIR):
        AV = get_video_comment.tans_bvid(BVID)
        x = 1
        i = 1
        data = []
        try:
            while(x<10):
                url2 = 'https://api.bilibili.com/x/v2/reply?&type=1&pn={}&oid={}'.format(x,str(AV))
                res2 = requests.get(url2)
                json_data = json.loads(res2.text)
                x += 1
                for l in json_data['data']['replies']:
                    print(i, l['content']['message'])
                    i += 1
                    data.append(l['content']['message'])
        except:
            pass

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
        print(cloudtext)
        s = " ".join(cloudtext)
        a = []
        print(s)
        color_mask = imageio.imread(PICDIR)
        font = r'C:\Users\86132\simhei.ttf'
        wc = wordcloud.WordCloud(font_path=font,max_font_size=50,mask=color_mask)
        try:
            pic = wc.generate(s)
            wc.to_file("wordcloud.png")
            plt.imshow(pic)
            plt.axis("off")
            plt.show()
        except:
            print("The video have no comment")

get_video_comment.get_hot_comment('BV1p64y1S7xx',r'C:\Users\86132\Downloads\5b22c8b7c4152449d5e6dbe642c72d7b.jpeg')
# the pic that you choosed should be white background and
# should not to be too complex otherwise the result would not be good
