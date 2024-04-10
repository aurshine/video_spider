import os
import requests
from tqdm import tqdm
from urllib.parse import urljoin
from typing import List


import setting
import delay


@delay.Delay(0, 2)
def request_video(url: str) -> bytes:
    response = requests.get(url, headers=setting.HEADERS)
    response.raise_for_status()
    return response.content


def parse_m3u8(url: str) -> List[str]:
    """
    解析m3u8文件，返回ts文件列表

    :param url: m3u8文件url

    :return:
    """
    # 解析m3u8文件
    response = requests.get(url, headers=setting.HEADERS)
    delay.random_delay(0, 2)
    response.raise_for_status()

    ts_files = []
    for line in response.text.split('\n'):
        if line.endswith('.ts'):
            ts_files.append(urljoin(url, line))
        elif line.endswith('.m3u8'):
            ts_files += parse_m3u8(urljoin(url, line))

    return ts_files


def download_ts_files(ts_files: List[str], save_path: str):
    """
    下载ts文件列表

    :param ts_files: ts文件列表

    :param save_path: 保存路径
    """
    os.makedirs(save_path, exist_ok=True)

    for i, ts_file in enumerate(ts_files):
        with open(os.path.join(save_path, f'{i: 04d}.ts'), 'wb') as f:
            f.write(request_video(ts_file))
            print(f'Downloaded {i+1}/{len(ts_files)}')


def merge_download_ts_files(ts_files: List[str], save_path: str):
    """
    合并下载ts文件

    :param ts_files: ts文件列表

    :param save_path: 保存路径
    """
    with open(save_path, 'ab') as f:
        for ts_file in tqdm(ts_files):
            f.write(request_video(ts_file))


def download_mp4_video(mp4_url: str, save_path: str):
    """ 下载视频文件 """
    with open(save_path, 'wb') as f:
        f.write(request_video(mp4_url))


def download_m3u8_video(m3u8_url: str, save_path: str):
    """ 下载m3u8视频文件 """
    ts_files = parse_m3u8(m3u8_url)
    merge_download_ts_files(ts_files, save_path)


def download_video(video_url, save_path, video_info: dict, download_func=None):
    """
    从给定的 url 下载视频并保存到指定路径

    视频信息通过 video_info 参数传入，并保存在 video_info.txt 中

    文件结构为 save_path/video.mp4 和 save_path/video_info.txt

    :param video_url: 视频url

    :param save_path: 保存地址

    :param video_info: 视频信息

    :param download_func: 下载函数, 需要接受下载地址和保存地址两个参数, 默认为download_mp4_video
    """
    if download_func is None:
        download_func = download_mp4_video

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    download_func(video_url, os.path.join(save_path, 'video.mp4'))
    with open(os.path.join(save_path, 'video_info.txt'), 'w', encoding='utf-8') as f:
        for k, v in video_info.items():
            f.write(f'{k}: {v}\n')