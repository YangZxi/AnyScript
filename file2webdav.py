# -*- coding: utf-8 -*-
# flake8: noqa

from datetime import datetime
import os
import logging
import argparse
import requests
from requests.auth import HTTPBasicAuth
from tqdm import tqdm

webdav_url = '' or os.getenv('WEBDAV_URL')
username = '' or os.getenv('WEBDAV_USERNAME')
password = '' or os.getenv('WEBDAV_PASSWORD')

REMOTE_DIR: str = None
FILE: str = None
FILTER_SUFFIX: str = None
regex = None

class ProgressFile:
    def __init__(self, filename, mode='rb', chunk_size=65536):
        self._file = open(filename, mode)
        self._total_size = os.path.getsize(filename)
        self._chunk_size = chunk_size
        self._pbar = tqdm(total=self._total_size, unit='B', unit_scale=True, desc=filename)

    def __enter__(self):
        return self

    def read(self, size):
        data = self._file.read(size)
        if data:
            self._pbar.update(len(data))
        return data

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()
        self._pbar.close()

    def __getattr__(self, attr):
        return getattr(self._file, attr)

def load_files():
    # 加载 file 文件，判断文件是否存在
    file = FILE
    files = []
    if os.path.isfile(file):
        files.append(file)
    elif os.path.isdir(file):
        for entry in os.scandir(file):
            if entry.is_dir():
                continue
            files.append(entry.path)
    else:
        logging.error('File not found')
        exit(1)
    logging.debug('Files: %s' % files)
    return files


def upload(file, file_name=None):
    #上传后保存的文件名
    remote_file = file_name if file_name else os.path.basename(file)
    remote_file = REMOTE_DIR + "/" + remote_file
    #生成上传 Token，可以指定过期时间等
    #要上传文件的本地路径
    localfile = file
    file_size = int(os.path.getsize(localfile) / 1024 / 1024)
    logging.info('Start upload file: %s, size: %sMB' % (localfile, file_size))
    # 以二进制模式读取文件内容
    # with open(localfile, 'rb') as f:
    #     file_content = f.read()
    # response = requests.put(webdav_url + remote_file, data=file_content, auth=HTTPBasicAuth(username, password))
    with ProgressFile(localfile) as f:
        response = requests.put(webdav_url + remote_file, data=f, auth=HTTPBasicAuth(username, password))
    if response.status_code >= 400:
        logging.error('Upload file failed, code: %d, content: %s' % (response.status_code, response.text))
        return
    logging.info('Upload file success: %s' % remote_file)


# 只上传当天且后缀为 .zst 的文件 
def custom_upload(filePath: str):
    # 文件名需要包含当前 yyyy_MM_dd
    now = datetime.now().strftime('%Y_%m_%d')
    prefix = ""
    suffix = (".zst", ".notes")
    if not filePath.startswith(prefix):
        return None, None
    if not filePath.endswith(suffix): 
        return None, None
    if (now not in filePath):
        return None, None
    file_name = now + "/" + os.path.basename(filePath)
    return filePath, file_name


def main():
    parser = argparse.ArgumentParser(description='Upload file to WebDav')
    parser.add_argument('--log-level', type=str, required=False, help='日志级别', default='INFO')
    parser.add_argument('--remote-dir', type=str, required=True, help='文件在云端被存储的目录')
    parser.add_argument('--file', type=str, required=True, help='指定要上传的文件或目录')
    args = parser.parse_args()
    # 配置日志记录器
    logging.basicConfig(level=logging.getLevelName(args.log_level), format='%(asctime)s - [%(levelname)s]: %(message)s')

    global REMOTE_DIR, FILE, webdav_url
    REMOTE_DIR = args.remote_dir
    FILE = args.file

    if not webdav_url.endswith('/'): webdav_url += '/'

    logging.info("======== Start upload file to WebDav ========")
    files = load_files()
    for file in files:
        file, file_name = custom_upload(file)
        logging.debug('File: %s, file_name: %s' % (file, file_name))
        if file is None:
            continue
        upload(file, file_name)
    logging.info("======== Start upload file to WebDav is done!!! ========")


if __name__ == "__main__":
    main()
