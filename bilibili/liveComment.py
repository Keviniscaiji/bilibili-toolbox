import requests
import time

class bilibiliDanmu():
    def __init__(self, romid):
        self.url = "https://api.live.bilibili.com/ajax/msg"
        self.headers = {
            "User-Agen"
            "t": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
            "Referer": "https://live.bilibili.com/"
        }
        self.data = {
            "roomid": romid,
            "csrf_token": "",
            "csrf": "",
            "visit_id": ""
        }
        self.old_list = []

    def text_danmu(self, html, callback=None):
        temp_list = []
        for text in html["data"]["room"]:
            danmu_string = text["nickname"] + " say:" + text["text"]
            temp_list.append(danmu_string)
        if temp_list == self.old_list:
            pass
        else:
            for text_number in range(1, 11):
                if "".join(temp_list[:text_number]) in "".join(self.old_list):
                    pass
                else:
                    try:
                        if callable is None:
                            print(temp_list[text_number - 1])
                        else:
                            callback(temp_list[text_number - 1])
                    except:
                        pass
                    else:
                        pass
            self.old_list = temp_list[:]

    def get_danmu(self, callback=None):
        html = requests.post(url=self.url, headers=self.headers, data=self.data)
        html.json()
        self.text_danmu(eval(html.text), callback)

if __name__ == "__main__":
    room_id = 1361615
    bzhan = bilibiliDanmu(room_id)

    while True:
        bzhan.get_danmu()
        time.sleep(2)
    
