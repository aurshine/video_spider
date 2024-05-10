import os
import re
import gc
import json
import atexit
from typing import List
from m_threadpool import NoWaitThreadPool as Pool

import m3u8
import setting
import delay
from url import UrlSet

DOWNLOAD_URL_PATH = os.path.join(setting.BRTV_VIDEO_PATH, 'download_url.txt')

video_urls = UrlSet(DOWNLOAD_URL_PATH, DOWNLOAD_URL_PATH)


def make_callback() -> str:
    """
    构造 brtv 请求里的 callback参数

    :return:
    """

    return 'jQuery3600' + delay.get_ramdom_num(16) + '_' + delay.get_time(13)


def make_br_tv_api(gid: str) -> str:
    """
    生成 北京卫视 视频播放api

    :param gid: 视频id
    """
    return (f'https://app.api.btime.com/video/play?'
            f'callback={make_callback()}'
            f'&id={gid}'
            f'&_={delay.get_time(13)}')


def parse_br_tv_api_response(data: str) -> dict:
    data = data[data.find('(') + 1: -1]
    return json.loads(data)


def download_br_tv_video(gid: str):
    """
    根据 gid 下载 北京卫视 视频

    :param gid: 视频id
    """
    if gid in video_urls:
        print(f'视频 {gid} 已下载')
        return

    print(f'开始下载 视频 {gid}')
    api_url = make_br_tv_api(gid)
    data = parse_br_tv_api_response(m3u8.request_text(api_url))

    video_url = data['data']['video_stream'][0]['stream_url']
    m3u8.download_video(video_url, os.path.join(setting.BRTV_VIDEO_PATH, gid), _video_info=data, cover=True)
    video_urls.add(gid)
    delay.random_delay(1, 3)
    print(f'视频 {gid} 下载完成')


def get_programme_id(guide_name: str) -> List[str]:
    """
    根据栏目名称获取栏目id

    :param guide_name: 栏目名称

    :return: 所有年份的栏目id
    """
    url = f'https://www.btime.com/btv/{guide_name}'
    html = m3u8.request_text(url)

    years = json.loads(m3u8.match(html[html.find('"list"'):], '[', ']'))

    return [year['listId'] for year in years]


def get_guide_programs(guide_name: str):
    """
    获取 北京卫视 一个栏目的节目表gid

    即一个栏目每一期节目的gid

    :return: 所有年份每期节目的 gid
    """
    for program_id in get_programme_id(guide_name):
        url = (f'https://pc.api.btime.com/btimeweb/infoFlow?'
               f'callback={make_callback()}'
               f'&list_id={program_id}'
               f'&refresh=1'
               f'&count=1000'
               f'&expands=pageinfo'
               f'&_={delay.get_time(13)}')

        res = m3u8.request_text(url)
        res = res[res.find('(') + 1: -1]
        data = json.loads(res)['data']['list']
        for program in data:
            yield program['gid']


def get_all_btv_guides() -> list:
    """
    获取 北京卫视 所有栏目
    :return:
    """
    pattern = r'open_url":"https:\\/\\/www.btime.com\\/btv\\/(.*?)"'
    url = 'https://www.brtn.cn/btvprogram'
    html = m3u8.request_text(url)
    return re.findall(pattern, html)


def download_guide(guide_name: str):
    """
    下载 北京卫视 guide_name 栏目下的所有节目

    :param guide_name: 栏目名称
    """
    if guide_name in video_urls:
        print(f'栏目 {guide_name} 的所有节目已下载')
        return

    print(f'开始下载 栏目 {guide_name} 的所有节目')

    with Pool(max_workers=4) as pool:
        pool.map(download_br_tv_video, get_guide_programs(guide_name))

    video_urls.add(guide_name)


def main():
    for guide_name in get_all_btv_guides():
        download_guide(guide_name)


if __name__ == '__main__':
    atexit.register(gc.collect)
    main()