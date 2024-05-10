import gc
import os
import json
import atexit
from typing import List
from m_threadpool import NoWaitThreadPool as Pool

import m3u8
import delay
import setting
from url import UrlSet

DOWNLOAD_URL_PATH = os.path.join(setting.WANGYI_LIVE_VIDEO_PATH, 'download_url.txt')

video_urls = UrlSet(DOWNLOAD_URL_PATH, DOWNLOAD_URL_PATH)


def make_wy_live_api_url(index: int) -> str:
    """
    构造网易直播API的URL

    :param index: 直播列表索引
    """
    return f'https://v.163.com/pcvideo/livechannel/previewlist/{index}.json'


def parse_wy_live_api_response(data: str) -> List[dict]:
    """
    解析网易直播API的响应
    """
    return json.loads(data)["live_review"]


def download_wangyi_live(data: dict, delay_min: int = 0, delay_max: int = 1):
    """
    下载网易直播
    """
    room_name = data['roomName']
    room_id = str(data['roomId'])
    if 'videos' not in data:
        return

    video_url = data['videos'][0]["videoUrl"]

    if room_id in video_urls:
        print(f'{room_name} 直播已下载')
        return

    print(f'开始下载 {room_name} {room_id}')

    m3u8.download_video(video_url, os.path.join(setting.WANGYI_LIVE_VIDEO_PATH, room_id), _video_info=data, cover=True)
    video_urls.add(room_id)
    delay.random_delay(delay_min, delay_max)
    print(f'{room_name} 直播下载完成')


def main():
    for i in range(1, 240):
        if i in video_urls:
            print(f'第 {i} 页直播间已下载')
            continue

        url = make_wy_live_api_url(i)
        text = m3u8.request_text(url, timeout=50)
        datas = parse_wy_live_api_response(text)

        with Pool(max_workers=10) as pool:
            pool.map(download_wangyi_live, datas)

        print(f'第 {i} 页直播间下载完成')
        video_urls.add(str(i))


if __name__ == '__main__':
    atexit.register(gc.collect)
    main()