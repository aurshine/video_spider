import os
import re
import json
from typing import Tuple

import m3u8
import delay
import setting
from url import UrlSet

DOWNLOAD_URL_PATH = os.path.join(setting.ACFUN_VIDEO_PATH, 'download_url.txt')

video_urls = UrlSet(DOWNLOAD_URL_PATH, DOWNLOAD_URL_PATH)


def make_up_index_url(uid: str, page: int):
    """
    构造 up主 的主页 url

    :param uid: up主的uid

    :param page: 请求的页码, 下标从1开始
    """
    return (f'https://www.acfun.cn/u/{uid}?'
            f'quickViewId=ac-space-video-list'
            f'&reqID=1'
            f'&ajaxpipe=1'
            f'&type=video'
            f'&order=newest'
            f'&page={page}'
            f'&pageSize=100'
            f'&t={delay.get_time(13)}')


def parse_page_with_av(text: str) -> list:
    """
    解析文本里的 av号, 带去重

    :param text:

    :return: 以list的形式返回每个解析页面的所有av号
    """
    pattern = r'v/ac(\d+)'
    return list(set(re.findall(pattern, text)))


def parse_av_video_page(html: str) -> Tuple[str, dict]:
    """
    解析视频页面, 获取视频下载地址

    :param html: 视频页面的html文本

    :return: 视频url 以及 视频信息
    """
    begin_index = html.find('{', html.find('"ksPlayJson"'))
    end_index = begin_index + 1

    stk = 1  # 维护存储 {}匹配的栈
    while stk != 0:
        if html[end_index] == '{':
            stk += 1
        elif html[end_index] == '}':
            stk -= 1

        end_index += 1

    json_str = json.loads(html[begin_index:end_index].replace(r'\"', '"'))
    return json_str['adaptationSet'][0]['representation'][0]['url'], json_str


def download_video(av_id: str):
    """
    根据av号下载视频

    :param av_id: av 号
    """
    av_id = str(av_id)
    if av_id in video_urls:
        print(f'{av_id} 视频已存在')
        return

    print(f'开始下载 {av_id} 视频')
    html = m3u8.request_text(f'https://www.acfun.cn/v/ac{av_id}')
    video_url, video_datas = parse_av_video_page(html)

    m3u8.download_video(video_url, os.path.join(setting.ACFUN_VIDEO_PATH, av_id), _video_info=video_datas, cover=True)

    video_urls.add(av_id)
    delay.random_delay(1, 3)


def download_all_videos(uid :str):
    """
    下载up主的所有视频
    """
    page = 0
    while True:
        page += 1
        url = make_up_index_url(uid, page)
        html = m3u8.request_text(url)
        av_ids = parse_page_with_av(html)

        if not av_ids:  # 已经到达最后一页
            print(f'uid:{uid} up视频已经下载完成')
            break

        for av_id in av_ids:
            download_video(av_id)


if __name__ == '__main__':
    uid = input('请输入up主的uid: ')
    download_all_videos(uid)