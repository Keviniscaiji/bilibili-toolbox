# -*- codeing = utf-8 -*-
# @Time : 2021/4/20
# @Author : Zhao Lingfei
# @File : send.py
# @Software : PyCharm



import requests
import time
from tkinter import *
import random

lis_text = ['666', '主播真厉害',
            '爱了，爱了',
            '关注走一走，活到99',
            '牛逼！！！',
            '秀儿，是你吗？',
            '哈哈哈',
            '这主播我爱了',
            '我要上电视']


def send():
    a = 0
    while True:
        time.sleep(3)
        send_meg = random.choice(lis_text)
        roomid = entry.get()
        ti = int(time.time())
        url = 'https://api.live.bilibili.com/msg/send'
        data = {
            'color': '16777215',
            'fontsize': '25',
            'mode': '1',
            'msg': send_meg,
            'rnd': '{}'.format(ti),
            'roomid': '{}'.format(roomid),
            'bubble': '0',
            'csrf_token': '29c790ccdfc03676a01d051a676d86d8',
            'csrf': '29c790ccdfc03676a01d051a676d86d8',
        }

        headers = {
            "cookie": "_uuid=8CEE3CA0-FC86-0579-9733-3F5EB07CF79456375infoc; buvid3=1CE302BB-BD83-4328-B1D4-C14EA949049B138397infoc; CURRENT_FNVAL=80; blackside_state=1; rpdid=|(k|kmkmmJRu0J'uY|lRkulu~; bsource=search_baidu; sid=db09wm2g; fingerprint=ba82611ea6f7950ccc7f1b974ba4908b; buvid_fp=1CE302BB-BD83-4328-B1D4-C14EA949049B138397infoc; buvid_fp_plain=4C0F5B43-9FA0-404F-A3FE-7A7585E79F50185010infoc; DedeUserID=456758752; DedeUserID__ckMd5=1e2cfb6df2b5f6e9; SESSDATA=e62a5e4d%2C1632375471%2Cadc8f*31; bili_jct=29c790ccdfc03676a01d051a676d86d8; PVID=1; LIVE_BUVID=AUTO2216168238263522; Hm_lvt_8a6e55dbd2870f0f5bc9194cddf32a02=1616826951,1617776963; Hm_lpvt_8a6e55dbd2870f0f5bc9194cddf32a02=1617776963; _dfcaptcha=021a523caa82139d2b61ddfc13de2423",
            'origin': 'https://live.bilibili.com',
            'referer': 'https://live.bilibili.com/blanc/1029?liteVersion=true',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        }
        a += 1
        response = requests.post(url=url, data=data, headers=headers)
        print(response)

        text.insert(END, '第{}条弹幕发送成功'.format(a))
        # 文本框滚动
        text.see(END)
        # 更新
        text.update()
        text.insert(END, '发送内容：{}'.format(send_meg))



root = Tk()
root.title('B站自动发送弹幕')
root.geometry('560x450+400+200')

label = Label(root, text='请输入房间ID:', font=('华文行楷', 20))
label.grid()

entry = Entry(root, font=('隶书', 20))
entry.grid(row=0, column=1)

text = Listbox(root, font=('隶书', 16), width=50, heigh=15)
text.grid(row=2, columnspan=2)

button1 = Button(root, text='开始发送', font=('隶书', 15), command=send)
button1.grid(row=3, column=0)

button2 = Button(root, text='退出程序', font=('隶书', 15), command=root.quit)
button2.grid(row=3, column=1)

root.mainloop()