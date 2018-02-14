# -*- coding: utf-8 -*-
import os
import re
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool

'''soup.select的方法
article_url = soup.select('#maincontent')  # id
article_url = soup.select('.metaRight')  # class
article_url = soup.select('h2')  #
'''


# 取得索引页的get返回值
def get_page_index(page):
    url = 'http://meizitu.com/a/more_{0}.html'.format(page)
    try:
        response = requests.get(url)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            return response.text
        return None
    except requests.RequestException:
        print('请求索引页错误！')
        return None


# 解析取得索引页的链接(Get)
def parse_page_index(html):
    soup = BeautifulSoup(html, "lxml")
    for article_url in soup.select('.wp-item'):
        if len(article_url.select('.pic')) > 0:
            url = article_url.select('.pic a')[0]['href']
            yield (url)


# 取得详情页的get返回值
def get_page_detail(url):
    try:
        response = requests.get(url)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            return response.text
        return None
    except requests.RequestException:
        print('请求索引页错误！')
        return None


# 解析详情页的信息，返回result字典
def parse_page_detail(html):
    soup = BeautifulSoup(html, "lxml")
    for item in soup.select('#picture img'):
        download_image(item['src'], item['alt'])


# 访问图片链接，发出下载指令save_image()
def download_image(url, file_name):
    print('正在下载：' + url)
    result = requests.Session()
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, sdch, br',
               'Accept-Language': 'zh-CN,zh;q=0.8',
               'Connection': 'keep-alive',
               'Host': 'mm.chinasareview.com',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    try:
        response = result.get(url, headers=headers, allow_redirects=False)
        if response.status_code == 200:
            save_image(response.content, file_name)
        return None
    except requests.RequestException:
        print('请求图片错误！')
        return None


# 下载指令，规定路径、存储方式等
def save_image(content, file_name):
    pattern = re.compile('(.*?)，第(.*?)张', re.S)
    result = re.search(pattern, file_name)
    file_path = '{0}\{1}'.format(os.getcwd() + '\\images', result.group(1))
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        print('创建文件夹:' + file_path)
    file_path = '{0}\{1}.{2}'.format(file_path, result.group(2), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def main(page):
    html = get_page_index(page)
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            parse_page_detail(html)


if __name__ == '__main__':
    pages = [x for x in range(1, 73)]
    pool = Pool()
    pool.map(main, pages)  # 多线程
