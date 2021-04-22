import selenium
import time
import json
from selenium import webdriver
import configparser
import requests
import qrcode
from PIL import Image

__all__ = ["LoginWeb", "LoginApp", "BilibiliUser"]

class LoginWeb(object):
    def __init__(self, headers: dict, driver_path: str, cookie_path: str, api_path='./api.cfg'):
        self.driver_path = driver_path
        self.cookie_path = cookie_path
        self.parser = configparser.ConfigParser()
        self.parser.read(api_path)
        self.headers = headers

    def login(self, t_slp=20):
        web = webdriver.Chrome(self.driver_path)
        web.get(self.parser.get("general", "HOMEPAGE_API"))
        web.delete_all_cookies()
        time.sleep(t_slp)  # wait for user to login
        cookies = web.get_cookies()
        web.close()
        # write cookies to txt
        self.write_cookies(cookies)

    def write_cookies(self, cookies: list):
        f = open(self.cookie_path, 'w')
        cookie = ""
        for i, item in enumerate(cookies):
            if i+1 != len(cookies):
                cookie += "{}={}; ".format(item['name'], item['value'])
            else:
                cookie += "{}={}".format(item['name'], item['value'])
        f.write(cookie)
        f.close()

    def check_login(self) -> bool:
        # evaluate cookies
        headers = self.headers
        f = open(self.cookie_path, 'r')
        headers['cookie'] = f.readline().strip('\n')
        url = self.parser.get("user", "ACCOUNT_API")
        res = requests.get(url=url, headers=headers)
        if res.json()['code'] == 0:
            return True
        else:
            return False


class LoginApp(object):
    def __init__(self, headers: dict, cookie_path: str, api_path='./api.cfg'):
        self.cookie_path = cookie_path
        self.parser = configparser.ConfigParser()
        self.parser.read(api_path)
        self.headers = headers

    def get_login_qrcode(self) -> (Image.Image, dict):
        get_url = self.parser.get("user", "LOGIN_r_API")
        qrcode_dict = requests.get(url=get_url, headers=self.headers).json()
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1
        )
        qr.add_data(qrcode_dict['data']['url'])
        qr.make(fit=True)
        img = qr.make_image()
        return img, qrcode_dict

    def login(self, qrcode_dict: dict, t_slp=30) -> int:
        post_url = self.parser.get("user", "LOGIN_s_API")
        data = {
            'oauthKey': qrcode_dict['data']['oauthKey'],
        }
        flag = False
        for i in range(t_slp):
            time.sleep(1)
            response = requests.post(
                url=post_url, headers=self.headers, data=data)
            if response.json()['status']:
                # write cookies to txt
                cookies=response.cookies.get_dict()
                cookie = ""
                for i, key in enumerate(cookies.keys()):
                    if i != len(cookies.keys()):
                        cookie += key+"="+cookies[key]+"; "
                    else:
                        cookie += key+"="+cookies[key]
                f = open(self.cookie_path, 'w')
                f.write(cookie)
                f.close()
                flag = True
                break
        return flag

    def check_login(self) -> bool:
        # evaluate cookies
        headers = self.headers
        f = open(self.cookie_path, 'r')
        headers['cookie'] = f.readline().strip('\n')
        url = self.parser.get("user", "ACCOUNT_API")
        res = requests.get(url=url, headers=headers)
        if res.json()['code'] == 0:
            return True
        else:
            return False


class BilibiliUser(object):
    def __init__(self, headers: dict, api_path="./api.cfg"):
        self.headers = headers
        self.parser = configparser.ConfigParser()
        self.parser.read(api_path)
        self.account_info = {}
        self.uid = -1

    def get_user_info(self, api_cls: str, uid=-1) -> dict:
        # mid == uid
        url = self.parser.get("user", api_cls)
        if api_cls != "ACCOUNT_INFO_API":
            param = {
                "mid":uid
            }
            res = requests.get(url=url, params=param, headers=self.headers)
        else:
            res = requests.get(url=url, headers=self.headers)
        json_dict = json.loads(res.text)
        if json_dict['code'] == 0:
            if api_cls == "ACCOUNT_INFO_API": 
                self.account_info = json_dict['data'] 
                self.uid = json_dict['data']['mid']
            return json_dict['data']
        else:
            return None

    def get_account_info(self) -> dict:
        return self.get_user_info('ACCOUNT_INFO_API')

    def get_card_info(self, uid: dict):
        # mid == uid
        return self.get_user_info('USER_CARD_API', uid)

    def get_space_info(self, uid: dict):
        # mid == uid
        return self.get_user_info('USER_SPACE_API', uid)

    def update_headers(self, headers: dict):
        self.headers = headers

    def info(self):
        return self.account_info


if __name__ == "__main__":
    headers = {
        'Referer':'https://www.bilibili.com/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        'cookie':"",
    }    

    f = open("./cookie.txt", "r")
    headers['cookie'] = f.readline().strip('\n')
    f.close()

    # ---------------------- test LoginWeb --------------------- #
    """ login_obj = LoginWeb(headers, "./driver/chromedriver.exe", "./cookie.txt", "./api.cfg")
    login_obj.login()
    status = login_obj.check_login()
    if status:
        print("Login succsessful")
    else:
        print("Login Failed") """
    # ------------------------------------------------------- #

    # ---------------------- test LoginAPP --------------------- #
    login_obj = LoginApp(headers, "./cookie.txt", "./api.cfg")
    img, qrcode_dict = login_obj.get_login_qrcode()
    img.show()
    print("You have 30 seconds to scan the QR code")
    status = login_obj.login(qrcode_dict, 30)
    if status:
        if login_obj.check_login():
            print("Login succsessful")
        else:
            print("Login Failed")
    else:
        print("Login Failed")
    # ------------------------------------------------------- #

    # ----------------- test BilibiliUser ------------------- #
    user = BilibiliUser(headers)
    info = user.get_account_info()
    if info is not None:
        print(user.info())
    else:
        print("Failed to load user info")
    # ------------------------------------------------------- #

