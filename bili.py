import requests
import json
import re
import urllib


class bilibili:

    def __init__(self, *args):
        print("初始化参数")

        self.cookie=args[0]
        self.ua = args[1]





    def dianzan(self,aid):

        cookiedic = self.cookietodic()
        print(cookiedic)
        csrf = cookiedic["bili_jct"]
        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent":self.ua,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br", "accept-language": "zh-CN,zh;q=0.9",
            "sec-fetch-dest": "document", "sec-fetch-mode": "navigate", "sec-fetch-site": "none",
            "upgrade-insecure-requests": "1"}

        res = requests.post('https://api.bilibili.com/x/web-interface/archive/like', headers=headers,data="aid="+aid+"&like=1&csrf="+csrf,cookies=cookiedic)
        print(res.text)
        if res.json()["code"]==0:
            print("点赞成功")
            return True
        else:
            print("点赞失败")
            return False


    def pinglun(self,aid,comment):
        print("aaaa")
        cookiedic = self.cookietodic()
        print(cookiedic)
        csrf=cookiedic["bili_jct"]

        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": self.ua,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br", "accept-language": "zh-CN,zh;q=0.9",
            "upgrade-insecure-requests": "1"}

        res = requests.post('https://api.bilibili.com/x/v2/reply/add', headers=headers,data="oid="+aid+"&type=1&message="+urllib.request.quote(comment)+"&plat=1&ordering=heat&jsonp=jsonp&csrf="+csrf,cookies=cookiedic)
        print(res.text)
        if res.json()["code"]==0:
            print("评论成功")
            return True
        else:
            print("评论失败")
            return False


    def BvtoAid(self,BV):
        headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36","accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9","accept-encoding":"gzip, deflate, br","accept-language":"zh-CN,zh;q=0.9","sec-fetch-dest":"document","sec-fetch-mode":"navigate","sec-fetch-site":"none","upgrade-insecure-requests":"1"}


        res = requests.get('https://www.bilibili.com/video/'+BV,headers=headers).text
        # print(res)
        try:
            INITIAL_STATE=re.findall('window.__INITIAL_STATE__=(.*?)};', res)[0]
            # print(INITIAL_STATE)
            aid = re.findall('"aid":(.*?),"',INITIAL_STATE)[0]

        except:
            print("BvtoAid err")
        if aid:
            return aid
        else:
            return None



    def cookietodic(self):
        cookie1=self.cookie
        cookiedic = {}
        for ii in cookie1.split(";"):
            if ii.find("=") != -1:
                cookiedic[ii.split("=")[0].strip().replace(" ", "")] = ii.split("=")[1].strip().replace(" ", "")
        return cookiedic


