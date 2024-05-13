import os
from typing import List, Optional, Iterator, Union

import requests
from urllib.parse import urljoin
import cv2
import ffmpeg

import setting


def video_duration(video_path, video_capture=None) -> float:
    """
    获取视频时长 (单位: 秒)

    :param video_path: 视频文件地址

    :param video_capture: 视频捕获器, 若为 None 则使用 cv2.VideoCapture(video_path) 获取视频捕获器

    :return: 视频时长
    """
    if not os.path.exists(video_path):
        print(video_path, '不存在')
        return 0

    video = cv2.VideoCapture(video_path) if video_capture is None else video_capture
    fps = video.get(cv2.CAP_PROP_FPS)

    if fps == 0:
        print(video_path, '无法获取帧率')
        return 0

    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)

    video.release()

    return frame_count / fps


def request_video(url: str, headers=None, **kwargs) -> Optional[requests.Response]:
    """
    请求视频文件的响应

    :param url: 视频文件url

    :param headers:  请求头

    :param kwargs:  其他参数

    :return: 请求的响应, 发生异常时返回 None
    """
    if headers is None:
        headers = setting.HEADERS

    response = requests.get(url, headers=headers, stream=True, **kwargs)
    try:
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        print(f'请求 {url} 失败')
        return None


def request_video_stream(url: str, headers=None, **kwargs) -> Optional[requests.Response]:
    """
    请求视频文件字节流响应

    :param url: 视频文件url

    :param headers: 请求头

    :param kwargs: 其他参数

    :return: 视频文件字节流响应, 发生异常时返回 None
    """
    if headers is None:
        headers = setting.HEADERS

    with requests.get(url, headers=headers, stream=True, **kwargs) as response:
        try:
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            print(f'请求 {url} 失败')
            return None


def request_text(url: str, headers=None, **kwargs) -> str:
    if headers is None:
        headers = setting.HEADERS

    response = requests.get(url, headers=headers, **kwargs)
    try:
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        print(f'请求 {url} 失败')
        return ''


def parse_m3u8(url: str) -> list:
    """
    解析m3u8文件，返回ts文件列表

    :param url: m3u8文件url

    :return: ts文件列表
    """
    ts_files = []
    # 解析m3u8文件
    text = request_text(url)
    for line in text.split('\n'):
        if line.startswith('#'):
            continue

        if '.ts' in line:
            ts_files.append(urljoin(url, line))
        elif '.m3u8' in line:
            ts_files.extend(parse_m3u8(urljoin(url, line)))

    return ts_files


def _download_video(video_stream: Union[bytes, Iterator[bytes], requests.Response], save_path: str):
    """
    下载视频文件

    :param video_stream: 视频文件字节流

    :param save_path: 保存地址 xxx.mp4

    :return:
    """
    if video_stream is None:
        return

    with open(save_path, 'wb') as f:
        if isinstance(video_stream, bytes):
            f.write(video_stream)
        elif isinstance(video_stream, Iterator):
            for chunk in video_stream:
                f.write(chunk)
        elif isinstance(video_stream, requests.Response):
            with video_stream as r:
                f.write(r.content)
        else:
            raise TypeError('video_stream 类型错误, 应为 bytes 或 Iterator[bytes]')


def download_ts_files(ts_files: List[str], save_path: str):
    """
    下载ts文件列表

    :param ts_files: ts文件列表

    :param save_path: 保存路径
    """
    os.makedirs(save_path, exist_ok=True)

    for i, ts_file in enumerate(ts_files):
        _download_video(request_video(ts_file), os.path.join(save_path, f'({i: 04d}).ts'))
        print(f'Downloaded {i+1}')


def merge_download_ts_files(ts_files: list, save_path: str, cover: bool = False):
    """
    合并下载ts文件

    :param ts_files: ts文件列表

    :param save_path: 保存路径 xxx.ts

    :param cover: 当文件存在时是否覆盖, 默认为 False
    """
    if os.path.exists(save_path) and not cover:
        print(save_path, '已存在')
        return

    with open(save_path, 'wb') as f:
        for ts_file in ts_files:
            with request_video(ts_file) as r:
                f.write(r.content)


def download_mp4_video(mp4_url: str, save_path: str, cover: bool = False):
    """
    下载MP4视频文件

    :param mp4_url: MP4视频文件url

    :param save_path: 保存路径 xxx/xxx.mp4

    :param cover: 当文件存在时是否覆盖, 默认为 False
    """
    if os.path.exists(save_path) and not cover:
        print(save_path, '已存在')
        return

    _download_video(request_video(mp4_url), save_path)


def download_m3u8_video(m3u8_url: str, save_path: str, cover: bool = False):
    """
    下载m3u8视频文件

    :param m3u8_url: m3u8视频文件url

    :param save_path: 保存路径 xxx/xxx.mp4

    :param cover: 当文件存在时是否覆盖, 默认为 False
    """

    ts_files = parse_m3u8(m3u8_url)
    merge_download_ts_files(ts_files, save_path, cover=cover)


def auto_download_video(video_url: str, save_path: str, cover: bool = False):
    """
    根据视频 url 自动选择下载函数

    :param video_url: 视频url

    :param save_path: 保存路径

    :param cover: 当前文件存在时是否覆盖, 默认为 False
    """

    if '.m3u8' in video_url:
        return download_m3u8_video(video_url, save_path, cover=cover)
    else:
        return download_mp4_video(video_url, save_path, cover=cover)


def video_info(video_path) -> Optional[dict]:
    """
    获取视频信息

    :param video_path:

    :return: 视频时长, 宽, 高, 帧率
    """
    if not os.path.exists(video_path):
        print(video_path, '不存在')
        return None

    video = cv2.VideoCapture(video_path)
    duration = video_duration(video_path, video)
    width, height = video.get(cv2.CAP_PROP_FRAME_WIDTH), video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cv2.CAP_PROP_FPS
    video.release()

    return {
        'duration': duration,
        'width': width,
        'height': height,
        'fps': fps
    }


def write_video_info(video_path, _video_info: any = None, cover=False):
    """
    在视频文件所在目录写入视频信息, 保存为 video_info.txt 文件

    :param video_path: 视频文件地址

    :param _video_info: 视频信息, 可为任何可以被转化为字符串的类型, 若为 None 则采用 cv2 获取视频信息

    :param cover: 当文件存在时是否覆盖, 默认为 False

    :return: 返回视频信息
    """
    if not os.path.exists(video_path):
        print(video_path, '不存在')
        return

    video_info_path = os.path.join(os.path.dirname(video_path), 'video_info.txt')
    if os.path.exists(video_info_path) and not cover:
        print(video_info_path, '已存在')
        return

    with open(video_info_path, 'w', encoding='utf-8') as f:
        if _video_info is None:
            _video_info = video_info(video_path)
        f.write(str(_video_info))

    return _video_info


def download_video(video_url, save_path, _video_info: Optional[dict] = None, cover: bool = False):
    """
    从给定的 url 下载视频并保存到指定路径

    视频信息通过 video_info 参数传入，并保存在 video_info.txt 中

    文件结构为 save_path/video.mp4 和 save_path/video_info.txt

    :param video_url: 视频url

    :param save_path: 保存地址

    :param _video_info: 视频信息, 若为 None 则不保存视频信息

    :param cover: 当文件存在时是否覆盖, 默认为 False
    """

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    video_path = os.path.join(save_path, 'video.mp4')
    auto_download_video(video_url, video_path, cover=cover)

    # audio_path = os.path.join(save_path, 'audio.mp3')
    # video2audio(video_path, audio_path, cover=cover)
    # write_audio_info(audio_path, cover=cover)

    if _video_info is not None:
        with open(os.path.join(save_path, 'video_info.txt'), 'w', encoding='utf-8') as f:
            for k, v in _video_info.items():
                f.write(f'{k}: {v}\n')


def audio_info(audio_path) -> Optional[dict]:
    """
    获取音频信息

    :param audio_path: 音频文件地址 xxx/xxx.mp3

    :return: 音频信息字典, 出现错误时返回 None
    """
    try:
        probe = ffmpeg.probe(audio_path)
        streams = probe['streams'][0]

        sample_rate = streams.get('sample_rate', None)
        channels = streams.get('channels', None)
        bit_rate = streams.get('bit_rate', None)

        return {
            'sample_rate': sample_rate,
            'channels': channels,
            'bit_rate': bit_rate
        }

    except ffmpeg.Error as e:
        print(e.stderr)
        print(f'Audio: {audio_path}\n')

    return None


def write_audio_info(audio_path, _audio_info: any = None, cover: bool = False):
    """
    在音频文件所在目录写入音频信息, 保存为 audio_info.txt 文件

    :param audio_path: 音频文件地址

    :param _audio_info: 音频信息, 可为任何可以被转化为字符串的类型, 若为 None 则采用 ffmpeg 获取音频信息

    :param cover: 当文件存在时是否覆盖, 默认为 False

    :return: 返回音频信息
    """
    if not os.path.exists(audio_path):
        print(audio_path, '不存在')
        return

    audio_info_path = os.path.join(os.path.dirname(audio_path), 'audio_info.txt')
    if os.path.exists(audio_info_path) and not cover:
        print(audio_info_path, '已存在')
        return

    with open(audio_info_path, 'w', encoding='utf-8') as f:
        if _audio_info is None:
            _audio_info = audio_info(audio_path)
        f.write(str(_audio_info))

    return _audio_info


def video2audio(video_path, audio_path=None, _audio_info=None, cover=False):
    """
    视频转音频

    若音频存在则不进行转码

    :param video_path: 视频文件地址 xxx/video.mp4

    :param audio_path: 音频文件地址 xxx/audio.wav, 默认为 None, 若为 None, 则保存为 video_path 所在目录的 audio.wav

    :param _audio_info: 音频信息, 可为任何可以被转化为字符串的类型, 默认为 None, 若不为 None, 则保存为 audio_info.txt 文件

    :param cover: 当文件存在时是否覆盖, 默认为 False

    :return: ffmpeg抛出异常返回 False, 否则返回 True
    """
    if not os.path.exists(video_path):
        print(video_path, '不存在')
        return

    if audio_path is None:
        audio_path = os.path.join(os.path.dirname(video_path), 'audio.wav')

    try:
        if cover or not os.path.exists(audio_path):
            print(f'Converting {video_path} to {audio_path}')
            ffmpeg.input(video_path, y=None).output(audio_path, format="wav").run()
            if _audio_info is not None:
                write_audio_info(audio_path, _audio_info, cover=cover)

        return True
    except ffmpeg.Error as e:
        print(f'Error occurred: {e.stderr}\n Video: {video_path}\n')
        return False


def video_is_ok(video_path):
    """
    判断视频是否正常

    :param video_path: 视频文件地址

    :return: True or False
    """
    try:
        probe = ffmpeg.probe(video_path)
        if probe['streams'][0]['codec_type'] == 'video':
            return True
        return False
    except ffmpeg.Error:
        return False


def match(text: str, pattern_l: str, patter_r: str) -> str:
    """
    匹配左右两边的字符串

    :param text: 原始文本

    :param pattern_l: 左匹配

    :param patter_r: 右匹配

    :return: 匹配结果
    """
    cnt, first = 0, -1
    for i, c in enumerate(text):
        if first != -1 and cnt == 0:
            return text[first: i]
        elif cnt < 0:
            raise RuntimeError('无法完成完整匹配, 请检查左右匹配是否配对')

        if c == pattern_l:
            if first == -1:
                first = i
            cnt += 1

        elif c == patter_r:
            cnt -= 1

    raise RuntimeError('无法完成完整匹配, 请检查左右匹配是否配对')