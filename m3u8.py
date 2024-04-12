import os
from typing import List, Optional

import requests
from urllib.parse import urljoin
import cv2
import ffmpeg

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
        for ts_file in ts_files:
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


def video_duration(video_path) -> float:
    """
    获取视频时长 (单位: 秒)

    :param video_path: 视频文件地址

    :return: 视频时长
    """
    if not os.path.exists(video_path):
        print(video_path, '不存在')
        return 0

    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)

    if fps == 0:
        print(video_path, '无法获取帧率')
        return 0

    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)

    video.release()

    return frame_count / fps


def video2audio(video_path, audio_path, audio_info=None):
    """
    视频转音频

    需要下载ffmpeg工具 并添加到环境变量中

    :param video_path: 视频文件地址 xxx/video.mp4

    :param audio_path: 音频文件地址 xxx/audio.mp3

    :param audio_info: 音频信息字典, 默认为 None
    """
    if not os.path.exists(video_path):
        print(video_path, '不存在')
        return

    if os.path.exists(audio_path):
        print(audio_path, '已存在')
        return

    print(video_path, '转码为', audio_path)
    try:
        ffmpeg.input(video_path).output(audio_path).run()
        with open(os.path.join(os.path.dirname(audio_path), 'audio_info.txt'), 'w', encoding='utf-8') as f:
            f.write(str(audio_info))

    except ffmpeg.Error as e:
        print(f'Error occurred: {e.stderr}\n Video: {video_path}\n')


def audio_info(audio_path) -> Optional[dict]:
    """
    获取音频信息

    :param audio_path: 音频文件地址 xxx/audio.mp3

    :return: 音频信息字典, 出现错误时返回 None
    """
    try:
        probe = ffmpeg.probe(audio_path)
        audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)

        if audio_stream:
            sample_rate = int(audio_stream['sample_rate'])
            channels = int(audio_stream['channels'])
            bit_rate = int(audio_stream['bit_rate']) if 'bit_rate' in audio_stream else None

            return {
                'sample_rate': sample_rate,
                'channels': channels,
                'bit_rate': bit_rate
            }
    except ffmpeg.Error as e:
        e.with_traceback(None)
        print(f'Audio: {audio_path}\n')

    return None