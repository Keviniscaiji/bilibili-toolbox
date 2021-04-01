import requests
import os
import configparser
import urllib
import sys
import time
import math
from prettytable import PrettyTable
from bs4 import BeautifulSoup
import json

__all__ = [
    "BaseDownloader", "CoverDownloader", 
    "VideoDownloader", "BulletScreenDownloader", "CommentDownloader"]

class BaseDownloader(object):
    def __init__(self, headers: dict, path: str, api_path='./api.cfg'):
        self.parser = configparser.ConfigParser()
        self.parser.read(api_path)
        self.headers = headers
        self.path = path
        self.info_key = ['title', 'bvid', 'aid', 'cid', 'pic']

    def get_video_info(self, link=None, bvid=None) -> dict:
        # link: str, bvid: str
        url = str(self.parser.get("video", "INFO_API"))
        if link is not None:
            html_text = requests.get(url=link, headers=self.headers).text
            soup = BeautifulSoup(html_text,"html.parser")
            raw_data = list(soup.head.children)[-3]
            bvid = str(raw_data).split('aid')[1].split("bvid")[2].strip('":,')
        param = {
            'bvid':'%s'%bvid
        }
        infos = requests.get(url=url, params=param, headers=self.headers).json()
        info_dict = {key: infos['data'][key] for key in self.info_key}
        return info_dict

    def update_headers(self, headers: dict):
        self.headers = headers

    @staticmethod
    def _progress(blocknum, blocksize, totalsize, units: str):
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100:
            percent = 100
        s = ('#' * min(round(percent/5), 20)).ljust(20, ' ')
        if percent == 100:
            sys.stdout.write("%.1f%%" % percent + '[' + s +']' + \
                " {}/{} ({})".format(totalsize, totalsize, units) + '\n')
        else:
            sys.stdout.write("%.1f%%" % percent + '[' + s +']' + \
                " {}/{} ({})".format(blocknum*blocksize, totalsize, units) + '\r')
        sys.stdout.flush()