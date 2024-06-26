import os
import json
import random
import time
from typing import List
from concurrent.futures import ThreadPoolExecutor as Pool
import traceback

import m3u8
import delay
import setting
from url import UrlSet


TAB_TYPES = ['vlog', 'game', 'funny', 'music', 'redian', 'foodie', 'travel', 'movies', 'sports',
             'farmer', 'knowledge', 'military', 'adorable', 'entertain', 'opusculum']

USER_IDS = '1de58dbf334697e9a42c9532ca857c98'

video_urls = UrlSet(setting.WANGYI_VIDEO_PATH)


def make_wy_api_url(tab_type: str, user_id: str, size: int = 20) -> str:
    """
    构造网易视频API的URL

    :param tab_type: 频道类型

    :param user_id: 用户ID

    :param size: 返回数据量大小
    """
    t = int(time.time() * 1000)

    return f'https://v.163.com/pcvideo/nc/api/v1/pc/video/detail/list?tabType=news_video_tab_{tab_type}&userId={user_id}&size={size}&t={t}'


def parse_wy_api_response(data: str) -> List[dict]:
    """
    解析网易视频API的响应
    """
    return json.loads(data)['data']['item']


def download_wangyi_video(data: dict, delay_min: int = 2, delay_max: int = 5):
    """
    下载网易视频
    """
    title = data['title']
    vid = data['vid']
    video_url = data['video_data']['sd_url']

    if vid in video_urls:
        print(f'{title} 视频已下载')
        return

    print(f'开始下载 {title} {vid}')
    m3u8.download_video(video_url, os.path.join(setting.WANGYI_VIDEO_PATH, vid), _video_info=data, cover=True)
    video_urls.add(vid)
    delay.random_delay(delay_min, delay_max)
    print(f'{title} 视频下载完成')


def main():
        num_page, size = 30, 30
        # 下载量 = len(TAB_TYPES) * num_page * size

        for i in range(num_page):
            random.shuffle(TAB_TYPES)  # 随机打乱TAB_TYPES列表
            for tab_type in TAB_TYPES:
                url = make_wy_api_url(tab_type, USER_IDS, size=size)
                text = m3u8.request_text(url, timeout=50, stream=True)
                datas = parse_wy_api_response(text)

                try:
                    for data in datas:
                        download_wangyi_video(data, 1, 2)

                except Exception as e:
                    traceback.print_exc()
                    print(f'下载 {tab_type} 频道视频失败: {e}')
                    break


if __name__ == '__main__':
    main()