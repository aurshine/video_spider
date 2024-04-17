import os
import json
from typing import List

import requests
from bs4 import BeautifulSoup

import setting
import m3u8
from url import UrlSet

DOWNLOAD_URL_PATH = os.path.join(setting.WANGYI_PUB_VIDEO_PATH, 'download_video_url')

WANGYI_PUB_INDEX_URL = 'https://open.163.com/newview/search/'

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


def download_wangyi_pub_video(data: dict):
    """
    下载网易公开课视频

    :param data: 网易公开课数据
    """
    pid = data['plid']
    title = ''.join(BeautifulSoup(data['title'], 'lxml').strings)

    if pid in video_urls:
        print(f'{title} 视频已下载')
        return

    html = m3u8.request_text(f'https://open.163.com/newview/movie/free?pid={pid}')
    soup = BeautifulSoup(html, 'lxml')
    video_url = soup.select_one('#open-video_html5_api')['src']

    print(f'开始下载 {title} 视频')
    m3u8.download_video(video_url, os.path.join(setting.WANGYI_PUB_VIDEO_PATH, pid), _video_info=data)
    video_urls.add(pid)
    print(f'{title} 视频下载完成')


if __name__ == '__main__':
    search_words = [tag.string for tag in BeautifulSoup(m3u8.request_text(WANGYI_PUB_INDEX_URL), 'lxml').select('span.link')]
    print(search_words)