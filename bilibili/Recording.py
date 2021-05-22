import requests
import re
import json
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



class Recording(object):


    def __init__(self, up_id, size=10, filename='recording.flv',baseurl='https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid={}'):
        self.up_id = up_id
        self.size_all = size
        self.filename = filename
        self.roomIdRegex = r'"//live\.bilibili\.com/{.*?}"'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}

        self.baseurl = 'https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid={}'.format(up_id)
        # response2 = requests.get(url=self.url, headers=self.headers)


    def getStream(self):
        url = self.baseurl.format(self.up_id)
        self.Referer = 'https://space.bilibili.com/{}/'.format(self.up_id)
        self.headers['Host'] = 'api.live.bilibili.com'
        self.headers['Referer'] = self.Referer
        response = requests.get(url=url, headers=self.headers).json()
        response2 = requests.get(url=url, headers=self.headers)
        room_id = response['data']['roomid']

        global anchor_status
        response2 = requests.get(url, headers=self.headers)
        html = response2.content.decode()
        anchor_status = re.findall("轮播</span>", html)
        if anchor_status:
            print("尚未开播")
        else:
            print("正在直播")

        return room_id


    def getJson(self, room_id):
        url = 'https://api.live.bilibili.com/room/v1/Room/playUrl?cid={}'.format(room_id)
        content = requests.get(url=url, headers=self.headers).text
        return content

    def extract(self):
        room_id = self.getStream()
        data = self.getJson(room_id)
        data_json = json.loads(data)
        download_url = data_json['data']['durl'][0]['url']
        host = download_url[8:].split('/')[0]
        return download_url, host

    def recording(self):

        content = self.extract()
        url, host = content
        headers = self.headers
        headers['host'] = host
        headers['referer'] = self.Referer


        size = 0
        chunk_size = 1024
        response = requests.get(url, headers=headers, stream=True, verify=False)
        with open(self.filename, 'wb') as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                size += len(data)
                file.flush()
                if self.size_all > 0:
                    sys.stdout.write('  进度:%.2fMB/%.2fMB' % (float(size / 10 / (self.size_all * 1024 * 1024) * 100), self.size_all) + '\r')
                    if size > self.size_all * 1024 * 1024:
                        break
                else:
                    sys.stdout.write('  进度:%.2fMB' % float(size / 1024 / 1024) + '\r')
        print('录制结束')


if __name__ == '__main__':
    up_id = int(input("输入主播UID："))
    # '2225281'
    # '50329118'
    size_MB = 0
    filename = 'recording.flv'
    liveVideo = Recording(up_id=up_id,size=size_MB,filename=filename,baseurl='https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid={}')
    liveVideo.getStream()
    liveVideo.recording()
