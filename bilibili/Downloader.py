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
        text = self.get_video_link(info_dict, "")
        qualities = text['data']['support_formats']
        qu = []
        for quality in qualities:
            qu.append([
                quality['new_description'],
                quality['quality'],
                quality['format']
            ])
        return qu

    def get_video_link(self, info_dict: dict, quality_param: str) -> dict:
        url = str(self.parser.get("video", "FLV_API"))
        # fourk = 1 --> enable 4k video stream
        param = {
            'cid':'%s'%info_dict['cid'],
            'bvid':'%s'%info_dict['bvid'],
            'qn':'%s'%quality_param,
            'fourk': 1
        }
        link_data = requests.get(url, params=param, headers=self.headers).json()
        return link_data

    def print_qu_table(self, qualities: list):
        print("Supported Qualities:")
        table = PrettyTable()
        table.field_names = ["Index", "Description", "Quality Param", "Video Format"]
        for i, quality in enumerate(qualities):
            table.add_row([str(i), quality[0], quality[1], quality[2]])
        print(table)
        print("\n")

    def download_Video(self, info_dict: str, quality_param: str, callback=None):
        link_data = self.get_video_link(info_dict, quality_param)
        flv_url = link_data['data']['durl'][0]['url']
        opener = urllib.request.build_opener()
        opener.addheaders = [item for item in self.headers.items()]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(
            url=flv_url, 
            filename=os.path.join(self.path, "{}_video.flv".format(info_dict['bvid'])),
            reporthook= callback if callback is not None else \
                lambda blocknum,blocksize,totalsize:self._progress(
                blocknum,blocksize,totalsize,
                'bit'))


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


if __name__ == "__main__":
    headers = {
        'Referer':'https://www.bilibili.com/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        'cookie':"_uuid=0A90EC93-44D6-40C5-2749-401C3210B3B483136infoc; buvid3=F7709BFF-B2B3-4848-852B-7B32D9281DC9184992infoc; sid=ig5gtah2; buvid_fp=F7709BFF-B2B3-4848-852B-7B32D9281DC9184992infoc; CURRENT_FNVAL=80; blackside_state=1; rpdid=|(u)~lR~YYmm0J'uYuYukYkJl; bp_t_offset_401883935=505658177784576438; finger=158939783; bp_video_offset_401883935=506852827230355536; fingerprint3=7ec25fd4a5ca2dda017c8248b8a316ba; fingerprint_s=e9095f132ef64672259e824eab5416de; PVID=1; bsource=search_baidu; fingerprint=de20d9205bb95b934d77a12457f3ea59; buvid_fp_plain=4B279B0E-6EC7-48FB-9C36-5F4698B7278058503infoc; DedeUserID=401883935; DedeUserID__ckMd5=ba4ce3ef45bf8016; SESSDATA=14b5ad2e,1632463963,4e897*31; bili_jct=4254bd21824f5cbf8279473ddfe6820d",
    }
    link = "https://www.bilibili.com/video/BV1BK411c7VC"
    path = "./output"


    # ----------------- test VideoDownloader ---------------- #
    downloader = VideoDownloader(headers, path)
    info_dict = downloader.get_video_info(link=link)
    print("Video Name: {}".format(info_dict['title']))
    print("Video bvid: {}\n".format(info_dict['bvid']))

    qualities = downloader.get_supported_quality(info_dict)
    downloader.print_qu_table(qualities)

    user_qu = input("Download Quality_Param: ")
    downloader.download_Video(info_dict, user_qu)
    del downloader
    print("Download complete")
    # ------------------------------------------------------- #


    # ----------------- test CoverDownloader ---------------- #
    """ downloader = CoverDownloader(headers, path)
    info_dict = downloader.get_video_info(link=link)
    print("Video Name: {}".format(info_dict['title']))
    print("Video bvid: {}\n".format(info_dict['bvid']))

    downloader.download_cover(info_dict)
    print("Download complete") """
    # ------------------------------------------------------- #


    # ------------ test BulletScreenDownloader -------------- #
    """ downloader = BulletScreenDownloader(headers, path)
    info_dict = downloader.get_video_info(link=link)
    print("Video Name: {}".format(info_dict['title']))
    print("Video bvid: {}\n".format(info_dict['bvid']))

    bullet_screen = downloader.download_BulletScreen(info_dict)
    downloader.write_csv(info_dict, bullet_screen)
    print("Download complete") """
    # ------------------------------------------------------- #


    #------------------ test CommentDownloader ---------------#
    """ downloader = CommentDownloader(headers, path)
    info_dict = downloader.get_video_info(link=link)
    print("Video Name: {}".format(info_dict['title']))
    print("Video bvid: {}\n".format(info_dict['bvid']))

    comments = downloader.download_Comment(info_dict, page=-1)
    downloader.write_csv(info_dict, comments)
    print("Download complete") """
    # ------------------------------------------------------- #
    