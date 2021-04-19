# -*- codeing = utf-8 -*-
# @Time : 2021/3/29 22:26
# @Author : Li Qiyu
# @File : Animation.py
# @Software : PyCharm

import requests
from bs4 import BeautifulSoup
import os
import json
import configparser



class Animation(object):
    def __init__(self, headers: dict, path: str, api_path='./api.cfg'):
        self.parser = configparser.ConfigParser()
        self.parser.read(api_path)
        self.headers = headers
        self.path = path

    def get_sorted_animation_info(self, num=20):
        param = {
            'season_version':-1,
            'area':-1,
            'is_finish':-1,
            'copyright':-1,
            'season_status':-1,
            'season_month':-1,
            'year':-1,
            'style_id':-1,
            'order':3,
            'st':1,
            'sort':0,
            'page':1,
            'season_type':1,
            'pagesize':num,
            'type':1
        }
        data = requests.get(
            url=self.parser.get("video", "ANIMATION_API"), 
            params=param, headers=self.headers)
        sorted_info = []
        animationlist = data.json()['data']['list']
        for item in animationlist:
            info = {k:str(item[k]) for k in ['title', 'order', 'badge', 'index_show', 'link', 'cover']} 
            sorted_info.append(info)       
        return sorted_info

    def print_animation_info(self, num=20):
        sorted_info = self.get_sorted_animation_info(num)
        for i, info in enumerate(sorted_info):
            print("Rank: %d"%(i+1))
            print("Title: %s"%info['title'])
            print("Like: %s"%info['order'])
            print("Piece Num: %s"%info['index_show'])
            print("Authority: %s"%info['badge'])
            print("Link: %s"%info['link'])
            print("Cover Link: %s"%info['cover'])
            print(" ")

    def download_cover(self):
        pass




if __name__ == "__main__":
    headers = {
        'Referer':'https://www.bilibili.com/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        'cookie':"",
    }
    animation = Animation(headers, "./", "../api.cfg")
    animation.print_animation_info()