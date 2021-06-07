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
    se,cs,duid = handle_info(sess)
    mycookies = {"SESSDATA":se,"bili_jct":cs,"DedeUserID": duid}
    S = requests.Session()
    requests.utils.add_dict_to_cookiejar(S.cookies, mycookies)
    S.headers.update(headers)
    b_j = mycookies["bili_jct"]
    url = "https://api.bilibili.com/x/web-interface/nav?build=0&mobi_app=web"
    content = S.get(url)
    return int(json.loads(content.text)["data"]['money'])
# this method can get the user's coin sum and return the information as integer
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
#  this method can get the coin of the user and the method is used below, if the coin of the
#  user is not enough, the method will not process.
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
#   get the videos of a poster and put them in a list for later process
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
            se = list[i + 1]
        if list[i] == "bili_jct":
            cs = list[i + 1]
        if list[i] == "DedeUserID":
            duid = list[i + 1]
        i = i + 1
    return se,cs,duid
# this method is used to process the cookie information, for the bilibili, we need
# some specific string in order the proform the function
def auto_coin_like(sess, aid) :
    se,cs,duid = handle_info(sess)
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
    return text["message"]

#  this method is used to put the coin and like the video

def random_like_coin(sess, uid, coins):
    list_of_video,x = get_up_video(uid)
    i = 0
    j = 0
    n = 0
    u = 0
    # try:
    while n < coins:
        k = random.randint(0, x - 1)
        # print("the video the you try to share : ")
        # print(list_of_video[k])
        if auto_Forwarding(sess, list_of_video[k]) == "重复分享":
            # print("the video have been shared")
            u = u + 1
        else:
            # print("successfully shared, The added experience will be displayed after a period of time")
            n = n + 1
        if u > 20:
            # print("most of his video have shared, change a user please")
            break
    # print("you now have " + str(get_coin(sess))+ " coins")
    if get_coin(sess) >= coins:
        while i < coins:
            k = random.randint(0, x-1)
            retrun =""
            retrun = auto_coin_like(sess,list_of_video[k])
            time.sleep(2)

            # print("the video the you try to drop coin : ")
            # print(list_of_video[k])
            if retrun == '超过投币上限啦~':
                j = j + 1
                # print("you already like and drop coin to this video")
                # if most of the video that the author post in recent are put coin in the system will
                # ask you to the change a author.
            else:
                i = i + 1
                # print("successful drop coin")
                # print(retrun)
            if j > 5:
                # print("maybe you have drop too many coins to his/her videos, change a user please")
                return get_user_detail(uid)
            time.sleep(2)
    else:
        # print("You do not have enough coin")
        return get_user_detail(uid)
    return get_user_detail(uid)
    # except:
    #     print("Please check your network environment")

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
    # print(json.loads(content.text))
    s = json.loads(content.text)
    return s["message"]
