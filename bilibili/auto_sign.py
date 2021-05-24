# -*- coding: utf8 -*-
import json
import time
import requests as r

def auto_sign(ck):
    try:
        user_info = json.loads(r.get("https://api.bilibili.com/x/web-interface/nav", cookies={"SESSDATA":ck}).text)
        if user_info["data"]["isLogin"] == False:
            print("Login Failed")

        sign = r.get("https://api.live.bilibili.com/sign/doSign", cookies={"SESSDATA":ck})
        sign_info = json.loads(sign.text)
        if sign_info["code"] == 0:
            print("successfully sign in")
        else:
            print("fall to sign in")
    except:
        print("Please check your network environment")
#  input: the cookie of a user, output if the user already sign in today, return the string fall to sign in
#  otherwise sign in the bilibili's live broadcast platform and return string successfully sign in
ck = "_uuid=33983BE8-3B5E-31DE-84A9-82D37E22D32608283infoc; buvid3=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; fingerprint3=bebaf37e711128ee5f5512f79e445037; buvid_fp=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; CURRENT_FNVAL=80; SESSDATA=b2ed4dde,1631859958,5851d*31; bili_jct=352c7187c835e066bb4ba78c929f6b47; DedeUserID=10548896; DedeUserID__ckMd5=d323e304c5795812; sid=6ewg8zhf; buvid_fp_plain=B337C198-9EB0-4174-A981-14D455D2A338184997infoc; blackside_state=1; rpdid=|(k|mJmYJ~|l0J'uYuYJuY~uJ; LIVE_BUVID=AUTO8516193485120705; bsource=search_baidu; fingerprint=b941082b09b290aea778334025424485; fingerprint_s=7de1a2a0858ae1bac94c76bd7e88e8aa; PVID=5"
auto_sign(ck)
