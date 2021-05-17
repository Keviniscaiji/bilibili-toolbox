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

def get_coin(sess):
    se,cs,duid = handle_info(sess);
    mycookies = {"SESSDATA":se,"bili_jct":cs,"DedeUserID": duid}
    S = requests.Session()
    requests.utils.add_dict_to_cookiejar(S.cookies, mycookies)
    S.headers.update(headers)
    b_j = mycookies["bili_jct"]
    url = "https://api.bilibili.com/x/web-interface/nav?build=0&mobi_app=web"
    content = S.get(url)
    return int(json.loads(content.text)["data"]['money'])

def get_user_detail(uid):  # need user to enter the ID of the video producer
    url = 'https://api.bilibili.com/x/relation/stat?vmid={}&jsonp=jsonp%20'.format(uid)
    res = requests.get(url)
    json_data = json.loads(res.text)
    list = []
    list.append(['UID: %s' % uid])
    list.append(['He/She followers: %s'%json_data['data']['follower']])
    list.append(['He/She follows: %s people'%json_data['data']['following']])
    list.append(["There are %s people on his/her blacklist"%json_data['data']['black']])
    string = ""
    string = string + list[0][0] + ",\n"
    string = string + list[1][0] + ",\n"
    string = string + list[2][0] + ",\n"
    string = string + list[3][0] + "."
    return string

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

def handle_info(sess):
    list = re.split('=|;', sess)
    j = 0
    while j < len(list):
        list[j] = list[j].replace(" ","")
        j = j + 1
    sess = ""
    cs = ""
    duid = ""
    se = ""
    i = 0
    while i < len(list):
        if list[i] == "SESSDATA":
            se = list[i + 1];
        if list[i] == "bili_jct":
            cs = list[i + 1]
        if list[i] == "DedeUserID":
            duid = list[i + 1]
        i = i + 1
    return se,cs,duid

def auto_coin_like(sess, aid) :
    se,cs,duid = handle_info(sess);
    mycookies = {"SESSDATA":se,"bili_jct":cs,"DedeUserID": duid}
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
        "csrf": cs
    }
    content = S.post(url, post_data)
    text = json.loads(content.text)
    print(text["message"])
    # print(se+" "+sess+" "+duid)
    # return text["message"]["money"]

def random_like_coin(sess,uid,coins):
    list_of_video,x = get_up_video(uid)
    i = 0
    j = 0
    if get_coin(sess) > coins:
        while i < coins:
            k = random.randint(0, x-1)
            retrun = auto_coin_like(sess,list_of_video[k])
            auto_Forwarding(sess, list_of_video[k])
            print("the video the you try to drop coin and share : ")
            print(list_of_video[k])
            if retrun != '超过投币上限啦~':
                j = j + 1
            i = i + 1
            if j > 30:
                print("maybe you have drop too many coins to his videos, change a user please")
                return get_user_detail(uid)
            time.sleep(2)
    else:
        print("you do not have enough coin")
        return get_user_detail(uid)
    return get_user_detail(uid)

def auto_Forwarding(sess,aid):
    se, cs, duid = handle_info(sess)
    url = "https://api.bilibili.com/x/web-interface/share/add"
    post_data = {
        "aid": aid,
        "csrf": cs
    }
    mycookies = {"SESSDATA": se, "bili_jct": cs, "DedeUserID": duid}
    S = requests.Session()
    requests.utils.add_dict_to_cookiejar(S.cookies, mycookies)
    S.headers.update(headers)
    content = S.post(url, post_data)
    return json.loads(content.text)

print(random_like_coin("_uuid=33983BE8-3B5E-31DE-84A9-82D37E22D32608283infoc; buvid3=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; fingerprint3=bebaf37e711128ee5f5512f79e445037; buvid_fp=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; CURRENT_FNVAL=80; SESSDATA=b2ed4dde,1631859958,5851d*31; bili_jct=352c7187c835e066bb4ba78c929f6b47; DedeUserID=10548896; DedeUserID__ckMd5=d323e304c5795812; sid=6ewg8zhf; buvid_fp_plain=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; blackside_state=1; rpdid=|(k|mJmYJ~|l0J'uYuYJuY~uJ; LIVE_BUVID=AUTO8516193485120705; fingerprint=b941082b09b290aea778334025424485; fingerprint_s=7de1a2a0858ae1bac94c76bd7e88e8aa; PVID=3; bfe_id=1e33d9ad1cb29251013800c68af42315",3301695,0))
# print(auto_Forwarding("_uuid=33983BE8-3B5E-31DE-84A9-82D37E22D32608283infoc; buvid3=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; fingerprint3=bebaf37e711128ee5f5512f79e445037; buvid_fp=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; CURRENT_FNVAL=80; SESSDATA=b2ed4dde,1631859958,5851d*31; bili_jct=352c7187c835e066bb4ba78c929f6b47; DedeUserID=10548896; DedeUserID__ckMd5=d323e304c5795812; sid=6ewg8zhf; buvid_fp_plain=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; blackside_state=1; rpdid=|(k|mJmYJ~|l0J'uYuYJuY~uJ; LIVE_BUVID=AUTO8516193485120705; fingerprint=b941082b09b290aea778334025424485; fingerprint_s=7de1a2a0858ae1bac94c76bd7e88e8aa; PVID=3; bfe_id=1e33d9ad1cb29251013800c68af42315",374916041))
# print(get_coin("_uuid=33983BE8-3B5E-31DE-84A9-82D37E22D32608283infoc; buvid3=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; fingerprint3=bebaf37e711128ee5f5512f79e445037; buvid_fp=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; CURRENT_FNVAL=80; SESSDATA=b2ed4dde,1631859958,5851d*31; bili_jct=352c7187c835e066bb4ba78c929f6b47; DedeUserID=10548896; DedeUserID__ckMd5=d323e304c5795812; sid=6ewg8zhf; buvid_fp_plain=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; blackside_state=1; rpdid=|(k|mJmYJ~|l0J'uYuYJuY~uJ; LIVE_BUVID=AUTO8516193485120705; fingerprint=b941082b09b290aea778334025424485; fingerprint_s=7de1a2a0858ae1bac94c76bd7e88e8aa; PVID=3; bfe_id=1e33d9ad1cb29251013800c68af42315"))