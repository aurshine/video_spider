import os
import re
import json

import m3u8
import setting
import delay
from url import UrlSet

DOWNLOAD_URL_PATH = os.path.join(setting.BRTV_VIDEO_PATH, 'download_url.txt')

video_urls = UrlSet(DOWNLOAD_URL_PATH, DOWNLOAD_URL_PATH)


def make_br_tv_api(gid: str) -> str:
    """
    生成 北京卫视 视频播放api

    :param gid: 视频id
    """
    return f'https://app.api.btime.com/video/play?id={gid}&_={delay.get_time(13)}'


def parse_br_tv_api_response(data: str) -> dict:
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


def get_programme_id(guide_name: str) -> str:
    """
    根据栏目名称获取栏目id

    :param guide_name: 栏目名称

    :return: 栏目id
    """
    url = f'https://www.btime.com/btv/{guide_name}'
    html = m3u8.request_text(url)
    flag_str = '"listId":'
    begin_index = html.find(flag_str)

    # 提取"listId": "programme_id" -> programme_id
    if begin_index != -1:
        begin_index = html.find('"', begin_index + len(flag_str)) + 1
        if begin_index != 0:
            end_index = html.find('"', begin_index)
            return html[begin_index:end_index]
    raise RuntimeError(f'未找到栏目 {guide_name} 的 id')


def get_guide_programs(guide_name: str) -> list:
    """
    获取 北京卫视 一个栏目的节目表gid

    即一个栏目每一期节目的gid

    :return: 每期节目的 gid 列表
    """
    url = (f'https://pc.api.btime.com/btimeweb/infoFlow?'
           f'list_id={get_programme_id(guide_name)}'
           f'&refresh=1'
           f'&count=10000'
           f'&expands=pageinfo'
           f'&_={delay.get_time(13)}')
    data = json.loads(m3u8.request_text(url))['data']['list']
    return [program['gid'] for program in data]


def get_all_btv_guides() -> list:
    """
    获取 北京卫视 所有栏目
    :return:
    """
    pattern = r'"open_url":"(.*?)"'
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
    for gid in get_guide_programs(guide_name):
        download_br_tv_video(gid)

    video_urls.add(guide_name)


def main():
    for guide_name in get_all_btv_guides():
        download_guide(guide_name)


if __name__ == '__main__':
    main()