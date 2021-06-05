import json
import requests as r

def auto_sign(ck):
    user_info = json.loads(r.get("https://api.bilibili.com/x/web-interface/nav", cookies={"SESSDATA":ck}).text)
    if user_info["data"]["isLogin"] == False:
        return -1
    sign = r.get("https://api.live.bilibili.com/sign/doSign", cookies={"SESSDATA":ck})
    sign_info = json.loads(sign.text)
    if sign_info["code"] == 0:
        return 0
    else:
        return -1
