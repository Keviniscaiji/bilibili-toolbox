# -*- codeing = utf-8 -*-
# @Time : 2021/5/1 16:13
# @Auther : 龚kevin
# @File : auto_coin.py
# @Software: PyCharm
import json
import random
import re
import time
import requests
headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36"
    ,"Referer": "https://www.bilibili.com/",
}

def get_up_video(UID):
    a = []
    url = 'https://api.bilibili.com/x/space/arc/search?mid={}&ps=50&tid=0&pn=1&keyword=&order=pubdate&jsonp=jsonp'.format(UID)
    res = requests.get(url)
    json_data = json.loads(res.text)
    x = 0
    for i in json_data['data']['list']['vlist']:
        x = x + 1
        a.append(i['aid'])
    return a,x

def auto_coin_like(sess, aid) :
    list = re.split('=|;',sess)
    duid = list[15] #get the DedeUserID
    cs = list[13] #get the bili_jct
    mycookies = {"SESSDATA":sess,"bili_jct":cs,"DedeUserID": duid}
    S = requests.Session()
    requests.utils.add_dict_to_cookiejar(S.cookies, mycookies)
    S.headers.update(headers)
    b_j = mycookies["bili_jct"]
    url = "https://api.bilibili.com/x/web-interface/coin/add"
    post_data = {
        "aid": aid,
        "multiply": '1',
        "select_like": '1',
        "cross_domain": "1",
        "csrf": b_j
    }
    content = S.post(url, post_data)
    text = json.loads(content.text)
    print(text)
    return text["message"]
def random_like_coin(sess,uid,coins):
    list_of_video,x = get_up_video(uid)
    i = 0
    j = 0
    while i < coins:
        k = random.randint(0, x-1)
        retrun = auto_coin_like(sess,list_of_video[k])
        print("the video the you try to drop coin: ")
        print(list_of_video[k])
        if retrun != '超过投币上限啦~':
            i = i + 1
        j = j + 1
        if j > 30:
            print("change a user please")
            return
        time.sleep(2)
# auto_coin_like("_uuid=33983BE8-3B5E-31DE-84A9-82D37E22D32608283infoc; buvid3=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; fingerprint3=bebaf37e711128ee5f5512f79e445037; buvid_fp=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; CURRENT_FNVAL=80; SESSDATA=b2ed4dde,1631859958,5851d*31; bili_jct=352c7187c835e066bb4ba78c929f6b47; DedeUserID=10548896; DedeUserID__ckMd5=d323e304c5795812; sid=6ewg8zhf; buvid_fp_plain=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; blackside_state=1; rpdid=|(k|mJmYJ~|l0J'uYuYJuY~uJ; LIVE_BUVID=AUTO8516193485120705; bsource=search_baidu; fingerprint=b941082b09b290aea778334025424485; fingerprint_s=7de1a2a0858ae1bac94c76bd7e88e8aa; PVID=5"
# ,'715146860')
random_like_coin("_uuid=33983BE8-3B5E-31DE-84A9-82D37E22D32608283infoc; buvid3=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; fingerprint3=bebaf37e711128ee5f5512f79e445037; buvid_fp=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; CURRENT_FNVAL=80; SESSDATA=b2ed4dde,1631859958,5851d*31; bili_jct=352c7187c835e066bb4ba78c929f6b47; DedeUserID=10548896; DedeUserID__ckMd5=d323e304c5795812; sid=6ewg8zhf; buvid_fp_plain=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; blackside_state=1; rpdid=|(k|mJmYJ~|l0J'uYuYJuY~uJ; LIVE_BUVID=AUTO8516193485120705; bsource=search_baidu; fingerprint=b941082b09b290aea778334025424485; fingerprint_s=7de1a2a0858ae1bac94c76bd7e88e8aa; PVID=5"
,3301695,1)