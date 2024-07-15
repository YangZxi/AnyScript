# -*- coding: utf-8 -*-
# flake8: noqa

from datetime import datetime
import os
from qiniu import Auth, put_file, etag
import logging
import argparse

access_key = '' or os.getenv('QINIU_ACCESS_KEY')
secret_key = '' or os.getenv('QINIU_SECRET_KEY')

OSS_DIR: str = None
FILE: str = None
FILTER_SUFFIX: str = None
regex = None

q = Auth(access_key, secret_key)

bucket_name = 'xiaosm-backup'


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
    key = file_name if file_name else os.path.basename(file)
    key = OSS_DIR + "/" + key
    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 300)
    #要上传文件的本地路径
    localfile = file
    file_size = int(os.path.getsize(localfile) / 1024 / 1024)
    logging.info('Start upload file: %s, size: %sMB' % (localfile, file_size))
    ret, info = put_file(token, key, localfile, version='v2') 
    logging.info('Upload file, info[%s]: %s' % (info.status_code, info.json()))
    assert ret['key'] == key
    assert ret['hash'] == etag(localfile)


def custom_upload(file: str):
    # file_name = None
    # return file, file_name
    # 文件名需要包含当前 yyyy_MM_dd
    now = datetime.now().strftime('%Y_%m_%d')
    prefix = ""
    suffix = ".zst"
    if not file.startswith(prefix):
        return None, None
    if not file.endswith(suffix):
        return None, None
    if (now not in file):
        return None, None
    file_name = now + "/" + file
    return file, file_name


def main():
    parser = argparse.ArgumentParser(description='Upload file to qiniu')
    parser.add_argument('--log-level', type=str, required=False, help='日志级别', default='INFO')
    parser.add_argument('--oss-dir', type=str, required=True, help='指定文件被上传的目录')
    parser.add_argument('--file', type=str, required=True, help='指定要上传的文件或目录')
    args = parser.parse_args()
    # 配置日志记录器
    logging.basicConfig(level=logging.getLevelName(args.log_level), format='%(asctime)s - [%(levelname)s]: %(message)s')

    global OSS_DIR, FILE
    OSS_DIR = args.oss_dir
    FILE = args.file
    logging.info('Start upload file to qiniu')
    files = load_files()
    for file in files:
        file, file_name = custom_upload(file)
        if file is None:
            continue
        upload(file, file_name)
    logging.info('Start upload file to qiniu is done~~~')


if __name__ == "__main__":
    main()
