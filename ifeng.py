import os
import json
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import List

import m3u8
import delay
import setting
from url import UrlSet

CHANNEL_IDS = ['27-95119-95123-', '27-95283-', '27-95199-', '27-95288-', '27-95259-', '27-95144-', '27-95273-',
               '27-95212-', '27-95022-', '27-95095-', '27-95273-95280-', '27-95171-', '27-95233-', '27-95366-',
               '27-95224-95227-', '27-95109-', '27-95022-95036-', '27-95047-', '27-95078-', ]

DOWNLOAD_URL_PATH = os.path.join(setting.IFENG_VIDEO_PATH, 'download_video_url')

video_urls = UrlSet(DOWNLOAD_URL_PATH, DOWNLOAD_URL_PATH)


def make_ifeng_api_url(page: int, step: int, channel_id: str) -> str:
    """
    生成 ifeng api 地址

    :param page: page从 1 开始

    :param step: 步长

    :param channel_id: 频道 id

    :return: url
    """
    return f'https://shankapi.ifeng.com/api/getVideoStream/{page}/{step}/{channel_id}/1/getVideoStream?callback=getVideoStream'


def parse_ifeng_response(data: str) -> List[dict]:
    """
    解析 ifeng api 的响应数据

    :param data: ifeng api 返回的数据

    :return: dict
    """
    json_data = data.lstrip('getVideoStreamm(')[:-1]

    # 解析 json 数据
    return json.loads(json_data)["data"]["data"]


def download_ifeng_video(data: dict, delay_min: int = 2, delay_max: int = 5):
    """
    下载凤凰网视频
    """
    title = data["title"]
    if data["url"] in video_urls:
        print(f'{title} 已下载')
        return

    print(f'开始下载 {title}')
    resp = requests.get(urljoin('https://', data["url"]), headers=setting.HEADERS, timeout=100, stream=True)
    soup = BeautifulSoup(resp.text, 'html.parser')

    video_url = soup.select_one('meta[name="og:img_video"]').get('content')
    m3u8.download_video(video_url, os.path.join(setting.IFENG_VIDEO_PATH, data['url'].split('/')[-1]), data)
    video_urls.add(data["url"])
    delay.random_delay(delay_min, delay_max)
    print(f'下载 {title} 完成')
