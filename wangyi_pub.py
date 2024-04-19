import os
import sys
import json
from typing import List
from urllib.parse import urljoin, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor as Pool

from bs4 import BeautifulSoup

import setting
import m3u8
from url import UrlSet

DOWNLOAD_URL_PATH = os.path.join(setting.WANGYI_PUB_VIDEO_PATH, 'download_video_url')

WANGYI_PUB_INDEX_URL = 'https://open.163.com'

video_urls = UrlSet(DOWNLOAD_URL_PATH, DOWNLOAD_URL_PATH)


def make_search_url(search_word, tab_type=1):
    """
    生成搜索网址

    :param search_word: 搜索关键词

    :param tab_type: 1: 视频 2: 精品课 3: 课单 4: 音频
    :return: url
    """
    return f'https://c.open.163.com/open/mob/searchv2/v2/queryAll.do?keyword={search_word}&tabType={tab_type}'


def parse_wangyi_pub_response(data: str) -> List[dict]:
    """
    解析网易公开课响应数据
    """
    return json.loads(data)['data']['list']


def download_wangyi_pub_video(html: str, data: dict, mid: str):
    """
    下载网易公开课视频

    :param html: 网易公开课视频页面 HTML 内容

    :param data: 视频信息

    :param mid: 视频编号
    """

    if mid in video_urls:
        print(f'{mid} 视频已下载')
        return

    soup = BeautifulSoup(html, 'lxml')
    title = soup.select_one('.video-title').string

    video_url = urljoin(WANGYI_PUB_INDEX_URL, soup.select_one('.video-main-box > video').get('src'))

    print(f'开始下载 {title} 视频')

    m3u8.download_video(video_url, os.path.join(setting.WANGYI_PUB_VIDEO_PATH, mid), _video_info=data)
    video_urls.add(mid)
    print(f'{title} 视频下载完成')


def download_wangyi_pub_video_list(pool, data: dict):
    """
    下载网易公开课视频列表

    :param data:

    :num_workers: 线程数

    :return:
    """
    pid = data['plid']
    html = m3u8.request_text(f'https://open.163.com/newview/movie/free?pid={pid}')
    soup = BeautifulSoup(html, 'lxml')

    video_list = soup.select('.video-list a')

    for video in video_list:
        video_url = urljoin(WANGYI_PUB_INDEX_URL, video.get('href'))
        mid = parse_qs(urlparse(video_url).query).get('mid')[0]
        pool.submit(download_wangyi_pub_video, m3u8.request_text(video_url), data, mid)


def main():
    search_words = ['计算机科学', '电子工程', '机械工程', '材料科学与工程', '化学工程', '生物工程', '土木工程', '医学', '药学', '医疗保健管理', '公共卫生学', '心理学', '社会学', '经济学', '政治学', '法学', '教育学', '市场营销学', '媒体与传播学', '历史学', '文学', '艺术史与美术学', '文化研究', '语言学', '哲学', '宗教学']

    with Pool(max_workers=5) as pool:
        for search_word in search_words:
            url = make_search_url(search_word)
            datas = parse_wangyi_pub_response(m3u8.request_text(url))
            for data in datas:
                download_wangyi_pub_video_list(pool, data)


if __name__ == '__main__':
    main()