import os
import requests
import json
import sys
import configparser

class LiveRecording(object):
    def __init__(self, room_id, path="./download/video", filename="sample", headers={}, api_path="./api.cfg"):
        self.room_id = room_id
        self.path = os.path.join(path, filename+".flv")
        self.parser = configparser.ConfigParser()
        self.parser.read(api_path)
        self.headers = headers

    def get_support_qu_server(self):
        url = self.parser.get("live", "LIVE_API")
        res = json.loads(
            requests.get(url, headers=self.headers, params={'cid': self.room_id}).text)
        qu_des = res['data']['quality_description']
        return qu_des, len(res['data']['durl'])

    def record_live(self, qu, callback=None):
        url = self.parser.get("live", "LIVE_API")
        size = 0
        chunk_size = 1024
        params={
            'cid': self.room_id,
            'quality': str(qu)
            }
        res = json.loads(
            requests.get(url, headers=self.headers, params=params).text)
        d_url = res['data']['durl'][1]['url']
        response = requests.get(
            d_url, headers=self.headers, stream=True, verify=False)
        with open(self.path, 'wb') as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                size += len(data)
                file.flush()
                if callback is None:
                    # sys.stdout.write('  进度:%.2fMB' % float(size / 1024 / 1024) + '\r')
                    pass
                else:
                    callback(float(size / 1024 / 1024))
            if callback is not None:
                callback(None)

if __name__ == '__main__':
    room_id = 76
    headers = {
        'Referer':'https://www.bilibili.com/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        'cookie':"",
    }
    recObj = LiveRecording(room_id, headers=headers)
    qus, servers = recObj.get_support_qu_server()
    recObj.record_live('3')