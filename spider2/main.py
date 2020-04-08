import imghdr
import os
import shutil
import threading
import time

import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"}
proxies = {'http': 'http://127.0.0.1:1080'}


def download_page(url):
    """
    用于下载页面
    """
    r = requests.get(url, headers=headers, proxies=proxies)
    r.encoding = 'gb2312'
    return r.text


def get_pic_list(html):
    """
    获取每个页面的套图列表,之后循环调用get_pic函数获取图片
    """
    soup = BeautifulSoup(html, 'html.parser')
    pic_list = soup.find_all('li', class_='wp-item')
    for i in pic_list:
        a_tag = i.find('h3', class_='tit').find('a')
        link = a_tag.get('href')
        text = a_tag.get_text()
        get_pic(link, text)


def get_pic(link, text):
    """
    获取当前页面的图片,并保存
    """
    html = download_page(link)  # 下载界面
    soup = BeautifulSoup(html, 'html.parser')
    pic_list = soup.find('div', id="picture").find_all('img')  # 找到界面所有图片
    create_dir('pic/{}'.format(text))
    for index, val in enumerate(pic_list):
        pic_link = val.get('src')  # 拿到图片的具体 url
        r = requests.get(pic_link, headers=headers, proxies=proxies)  # 下载图片，之后保存到文件
        file_name = 'pic/{}/{}'.format(text, str(index) + '.' + (pic_link.split('.')[-1]))
        with open(file_name, 'wb') as f:
            f.write(r.content)
            time.sleep(1)  # 休息一下，不要给网站太大压力，避免被封
        if imghdr.what(file_name) is None:
            get_pic(link, text)
            break


def create_dir(name):
    """
    新建或者清空文件夹
    """
    if os.path.exists(name):
        shutil.rmtree(name)
    os.makedirs(name)


def execute(url):
    """
    单线程执行方法
    """
    page_html = download_page(url)
    get_pic_list(page_html)


def main():
    create_dir('pic')
    queue = [i for i in range(1, 72)]  # 构造 url 链接 页码。
    threads = []
    while len(queue) > 0:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < 5 and len(queue) > 0:  # 最大线程数设置为 5
            cur_page = queue.pop(0)
            url = 'http://meizitu.com/a/more_{}.html'.format(cur_page)
            thread = threading.Thread(target=execute, args=(url,))
            thread.setDaemon(True)
            thread.start()
            print('{}正在下载{}页'.format(threading.current_thread().name, cur_page))
            threads.append(thread)


if __name__ == '__main__':
    main()
