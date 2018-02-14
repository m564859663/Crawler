# -*- coding: utf-8 -*-
import os
import json
import re
import requests
import pymongo
from hashlib import md5
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from config import *
from multiprocessing import Pool
import numpy as np

np.set_printoptions(threshold=np.inf)
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


# 取得索引页的get返回值
def get_page_index(offset, keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': 3,
        'from': 'gallery'
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except requests.RequestException:
        print('请求索引页错误！')
        return None


# 解析取得索引页的链接(Json)
def parse_page_index(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')


# 取得详情页的get返回值
def get_page_detail(url):
    # http转化为https
    url_pattern = re.compile('http://toutiao.com/group/(.*?)/', re.S)
    result = re.search(url_pattern, url)
    if result:
        url = 'https://toutiao.com/group/' + result.group(1) + '/'
    pass
    try:
        # 301重定向，Location问题
        result = requests.Session()
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate, sdch, br',
                   'Accept-Language': 'zh-CN,zh;q=0.8',
                   'Connection': 'keep-alive',
                   'Host': 'www.toutiao.com',
                   'Upgrade-Insecure-Requests': '1',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
        response = result.get(url, headers=headers, allow_redirects=False)
        try:
            url = response.headers['Location']
        except KeyError:
            pass
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except requests.RequestException:
        print('请求详情页错误！', url)
        return None


# 解析详情页的信息，返回result字典
def parse_page_detail(html, url):
    soup = BeautifulSoup(html, "lxml")
    title = soup.select('title')[0].get_text()
    images_pattern = re.compile('gallery: JSON.parse\((.*?)\),', re.S)
    result = re.search(images_pattern, html)
    if result:
        data = json.loads(json.loads(result.group(1)))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [items.get('url') for items in sub_images]
            for image in images: download_image(image, title)
            return {
                'title': title,
                'url': url,
                'images': images
            }


# 保存到Mongo数据库
def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储到MongoDB成功')
        return True
    return False


# 访问图片链接，发出下载指令save_image()
def download_image(url, file_name):
    print('正在下载：' + url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content, file_name)
        return None
    except requests.RequestException:
        print('请求图片错误！')
        return None


# 下载指令，规定路径、存储方式等
def save_image(content, file_name):
    file_path = '{0}\{1}'.format(os.getcwd() + '\\images', file_name)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        print('创建文件夹:' + file_path)
    file_path = '{0}\{1}.{2}'.format(file_path, md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def main(offset):
    html = get_page_index(offset, KEY_WORD)
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html, url)
            if result:
                print(result['title'], ':', result['url'])


if __name__ == '__main__':
    groups = [x * 20 for x in range(GROUP_START, GROUP_END)]
    pool = Pool()
    pool.map(main, groups)  # 多线程
