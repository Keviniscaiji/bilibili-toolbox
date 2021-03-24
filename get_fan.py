# -*- codeing = utf-8 -*-
# @Time : 2021/3/21 16:05
# @Auther : 龚kevin
# @File : bilibiliapi.py
# @Software: PyCharm
import requests
import json
from bs4 import BeautifulSoup
import re

def get_user_detail(fan):  # need user to enter the ID of the video producer
    url = 'https://api.bilibili.com/x/relation/stat?vmid={}&jsonp=jsonp%20'.format(fan)
    res = requests.get(url)
    json_data = json.loads(res.text)
    print('The user with id %s has:' % fan)
    print('followers :', json_data['data']['follower'])
    print( 'He/She follows:',json_data['data']['following'],'people')

def get_hot_comment(AV):
    url2 = 'https://comment.bilibili.com/{}.xml'.format(str(AV))
    res2 = requests.get(url2)
    res2.encoding = 'utf-8'
    soup = BeautifulSoup(res2.text,'html.parser')
    text = soup.get_text()
    s_text = re.split('[,.?!。？！【】{}~-]',text)

    text_list = []
    for l in s_text:
        if len(l) != 0:
            text_list.append(l)
    hot_word = text_list[3]
    max_word = text_list.count(hot_word)

    for l in text_list:
        if text_list.count(l)>max_word:
            max_word = text_list.count(l)
            hot_word = l
    print(hot_word,'appeared for {} times'.format(max_word))
    print(text_list)

get_user_detail(44605243)
get_hot_comment(312361287)