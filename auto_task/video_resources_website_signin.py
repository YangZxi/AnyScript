import requests
import urllib3
import re
import json
import logging
from os import getenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

default_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36 Edg/83.0.478.45",
}
cookies = {
    "4ksj": '''
'''.strip() or getenv("siksj"),
    "bugutv": '''
'''.strip() or getenv("bugutv"),

}


def sign_4ksj():
    logging.info("4k世界签到")
    key = "4ksj"
    url = "https://www.4ksj.com/qiandao.php?sign=64c84eaa"
    headers = default_headers
    # headers["Referer"] = url
    headers["Cookie"] = cookies[key]
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        html = response.text
        result = re.findall(r"<div id=[\"']messagetext[\"'].*>[\s]*<p>(.*)<\/p>", html)
        # result = html.find("messagetext")
        if result.__len__() == 0:
            logging.error("签到失败，请检查 Cookie 是否过期")
            return
        logging.info(result[0])
    else:
        logging.error(f"状态码: {response.status_code}，签到失败，连接至 4ksj.com 失败")
    logging.info("4k世界签到 END")


def sign_bugutv():
    logging.info("布谷TV签到")
    key = "bugutv"
    url = "https://www.bugutv.org/wp-admin/admin-ajax.php"
    headers = default_headers
    # headers["Referer"] = url
    headers["Cookie"] = cookies[key]
    user_url = "https://www.bugutv.org/user/vip"
    user_response = requests.get(user_url, headers=headers, verify=False)
    data_nonce = ""
    if user_response.status_code == 200:
        html = user_response.text
        result = re.findall(r"<button class=['\"].*go-user-qiandao.*['\"][\w\s]*data-nonce=['\"]([\w\d]*)['\"]", html)
        # result = html.find("go-user-qiandao")
        if result.__len__() == 0:
            logging.error("签到失败，请检查 Cookie 是否过期")
            return
        data_nonce = result[0]
        logging.info("获取用户信息成功")
    else:
        logging.error(f"状态码: {user_response.status_code}，签到失败，连接至 bugutv.org 失败")
        return
    
    body = {
        "action": "user_qiandao",
        "nonce": data_nonce,
    }
    response = requests.post(url, headers=headers, data=body, verify=False)
    if response.status_code == 200:
        # unicode 解码
        data = response.text.encode("utf-8").decode("unicode_escape")[3:]
        data = json.loads(data)
        logging.info(data["msg"])
    else:
        logging.error(f"状态码: {response.status_code}，签到失败，连接至 bugutv.org 失败")
    logging.info("布谷TV签到 END")
    

def main():
    # 配置日志记录器
    logging.basicConfig(level=logging.getLevelName("INFO"), format="%(asctime)s - [%(levelname)s]: %(message)s")
    sign_4ksj()
    print()
    sign_bugutv()


main()