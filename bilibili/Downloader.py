import requests
import os
import configparser
import urllib
import sys
import time
import math
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
        info_dict = requests.get(url=url, params=param, headers=self.headers).json()
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

    def download_with_resume(self, url:str, path:str, file_name:str, 
                            callback=None, chunk_size=1024) -> int:
        file_path = os.path.join(path, file_name)
        # get the total file size
        response = requests.get(url, stream=True, headers=self.headers) 
        file_size = int(response.headers['Content-Length']) 
        # resume or from the begining
        if os.path.exists(file_path):
            first_byte = os.path.getsize(file_path)  
            block_index = math.ceil(first_byte/chunk_size)
        else:
            first_byte = 0
            block_index = 0
        # if download complete, finished
        if first_byte >= file_size: 
            return 0
        # get the download stream
        headers = self.headers
        headers["Range"] = f"bytes={first_byte}-{file_size}"
        req = requests.get(url, headers=headers, stream=True)  
        # callback function
        callback = callback if callback is not None else \
                lambda blocknum,blocksize,totalsize:self._progress(
                blocknum,blocksize,totalsize,
                'bit')
        # start to download
        with open(file_path, 'ab') as f:
            for chunk in req.iter_content(chunk_size=chunk_size):  
                if chunk:
                    f.write(chunk)
                    block_index += 1
                    callback(block_index, chunk_size, file_size)
        return 0
        

class CoverDownloader(BaseDownloader):
    def __init__(self, headers: dict, path: str, api_path='./api.cfg'):
        super().__init__(headers, path, api_path)

    def download_Cover(self, info_dict: dict, callback=None):
        opener = urllib.request.build_opener()
        opener.addheaders = [item for item in self.headers.items()]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(
            url=info_dict['pic'], 
            filename=os.path.join(self.path, "{}_cover.png".format(info_dict['bvid'])),
            reporthook=callback if callback is not None else \
                lambda blocknum,blocksize,totalsize:self._progress(
                blocknum,blocksize,totalsize,
                'bit'))


class VideoDownloader(BaseDownloader):
    def __init__(self, headers: dict, path: str, api_path='./api.cfg'):
        super().__init__(headers, path, api_path)

    def get_supported_quality(self, info_dict: str) -> list:
        # return [description, quality_param, video_format]
        link_datas = self.get_video_link(info_dict, "")
        qualities = link_datas[0]['data']['support_formats']
        qu = []
        for quality in qualities:
            qu.append([
                quality['new_description'],
                quality['quality'],
                quality['format']
            ])
        return qu

    def get_video_link(self, info_dict: dict, quality_param: str, piece_idx=0, t_slp=0.01) -> dict:
        url = str(self.parser.get("video", "FLV_API"))
        # fourk = 1 --> enable 4k video stream
        link_datas = []
        param = {
                    'cid':'',
                    'bvid':'%s'%info_dict['data']['bvid'],
                    'qn':'%s'%quality_param,
                    'fourk': 1
        }
        if piece_idx == -1:
            for item in info_dict['data']['pages']:
                param['cid'] = item['cid']
                link_data = requests.get(url, params=param, headers=self.headers).json()
                link_datas.append(link_data)
                time.sleep(t_slp)
        else:
            param['cid'] = info_dict['data']['pages'][piece_idx]['cid']
            link_data = requests.get(url, params=param, headers=self.headers).json()
            link_datas.append(link_data)
        return link_datas

    def operate_download_cache(self, bvid=None, quality_param=None, 
                                piece_idx=None, title=None, mode='n'):
        # mode:
        # n -> new cache; rm -> remove cache; r -> read cache
        if mode == 'n':
            cache_f = open(os.path.join(
                self.path, 
                "{}_{}_video.cache".format(bvid, piece_idx)),
                'w')
            cache_f.write(bvid+"\n")
            cache_f.write(str(quality_param)+"\n")
            cache_f.write(str(piece_idx)+"\n")
            # cache_f.write(str(title)+"\n")
            cache_f.close()
            return 0
        elif mode == "rm":
            os.remove(os.path.join(
                self.path, 
                "{}_{}_video.cache".format(bvid, piece_idx)))
            return 0
        elif mode == 'r':
            cache_f = open(os.path.join(
                self.path, 
                "{}_{}_video.cache".format(bvid, piece_idx)),
                'r')
            lines = [line.strip('\n') for line in cache_f.readlines()]
            cache = {}
            cache['bvid'] = lines[0]
            cache['qu'] = int(lines[1])
            cache['piece_idx'] = int(lines[2])
            # cache['title'] = str(line[3])
            cache_f.close()
            return cache
        else:
            return -1

    def download(self, info_dict: str, quality_param: str, piece_idx=0, callback=None):
        link_data = self.get_video_link(info_dict, quality_param, piece_idx)
        flv_url = link_data[0]['data']['durl'][0]['url']
        status = self.download_with_resume(
            flv_url, 
            self.path, 
            "{}_{}_video.flv".format(info_dict['data']['bvid'], piece_idx+1),
            callback)
        return status


class BulletScreenDownloader(BaseDownloader):
    def __init__(self, headers: dict, path: str, api_path='./api.cfg'):
        super().__init__(headers, path, api_path)

    def download_BulletScreen(self, info_dict: dict) -> list:
        # time_in_video(sec),time_send(%Y-%m-%d %H:%M:%S),text
        bullet_screen = []
        url = self.parser.get('video', 'DM_API')
        url += "/{}.xml".format(info_dict['cid'])
        xml_text = requests.get(url=url, headers=self.headers)
        xml_text.encoding="utf8"
        soup = BeautifulSoup(xml_text.text,"html.parser")
        for item in soup.find_all('d'):
            dm_info = str(item['p']).split(',')
            time_in_video = float(dm_info[0])
            time_send = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(dm_info[4])))
            text = str(item.text)
            bullet_screen.append("{},{},{}".format(time_in_video, time_send, text))
        return bullet_screen

    def write_csv(self, info_dict: str, bullet_screen: list):
        f = open(os.path.join(
            self.path, "%s_dm.csv"%info_dict['bvid']), 'w', encoding = 'utf-8')
        for item in bullet_screen: f.write(item+'\n') 
        f.close()
            

class CommentDownloader(BaseDownloader):
    def __init__(self, headers: dict, path: str, api_path='./api.cfg'):
        super().__init__(headers, path, api_path)

    def download_Comment(self, info_dict: dict, page=-1, t_slp=0.01) -> list:
        # like, time, up_like, up_reply, comment
        # page -> [a, b)
        comments = []
        url = str(self.parser.get("video", "COMMENT_API"))
        download_multi = True if page == -1 or isinstance(page, list) else False
        param = {
            'type': 1,
            'oid': info_dict['aid'],
            'pn': 1
        }
        xml_text = requests.get(url=url, params=param, headers=self.headers)
        xml_text.encoding = "utf8"
        json_dict = xml_text.json()
        cm_num_page = int(json_dict['data']['page']['size'])
        total_page = math.ceil(
            int(json_dict['data']['page']['count']) / cm_num_page)
        if isinstance(page, list):
            page_num = page[1]-page[0]
            assert page_num <= total_page, \
                "Only have {} pages, but got page {}".format(total_page, page_num)
        else:
            assert page <= total_page, \
                "Only have {} pages, but got page {}".format(total_page, page)
        # download comment from single page
        def d_comment(page):
            comments = []
            param['pn'] = page
            xml_text = requests.get(url=url, params=param, headers=self.headers)
            xml_text.encoding = "utf8"
            json_dict = xml_text.json()
            for reply in json_dict['data']['replies']:
                comment = reply['content']['message'].replace('\n', '//')
                time_ = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(int(reply['ctime'])))
                like = int(reply['like'])
                up_like = True if reply['up_action']['like']=='true' else False
                up_reply = True if reply['up_action']['reply']=='true' else False
                comments.append([time_, like, up_like, up_reply, comment])
            return comments
        if download_multi:
            d_rg = [1, total_page+1] if page==-1 else page
            for i in range(d_rg[0], d_rg[1]):
                time.sleep(t_slp)
                comments += d_comment(i)
                self._progress(i, cm_num_page, (d_rg[1]-d_rg[0])*cm_num_page, 'comment')
        else:
            comments = d_comment(page)
        return comments

    def write_csv(self, info_dict: dict, comments: list):
        f = open(os.path.join(
            self.path, "%s_cm.csv"%info_dict['bvid']), "w", encoding="utf-8")
        for item in comments:
            line = ""
            for i, info in enumerate(item):
                if i != len(item)-1:
                    line += str(info)+','
                else:
                    line += str(info)+'\n'
            f.write(line)
        f.close() 



    