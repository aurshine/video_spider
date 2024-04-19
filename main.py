import os
import time
from tqdm import tqdm

import m3u8
import setting
import check

def check_paths_exist(dir_path, other_paths: list) -> list:
    """
    检查 dir_path 下是否存在 other_paths 中所有的路径

    返回不存在的路径列表

    :param dir_path: 文件夹的地址

    :param other_paths: 需要检查的文件名或文件夹名组成的列表

    :return: 不存在的路径列表
    """
    not_exist_paths = []
    for other_path in other_paths:
        other_path = os.path.join(dir_path, other_path)
        if not os.path.exists(other_path):
            not_exist_paths.append(other_path)

    return not_exist_paths


def dir_batch_operation(base_dir_path):
    video_duration = 0
    check_paths = ['audio.mp3', 'audio_info.txt', 'video.mp4', 'video_info.txt']
    not_exist_paths = []
    for path in tqdm(os.listdir(base_dir_path)):
        dir_path = os.path.join(base_dir_path, path)
        if not os.path.isdir(dir_path):
            continue

        video_path = os.path.join(dir_path, 'video.mp4')
        audio_path = os.path.join(dir_path, 'audio.mp3')
        not_exist_paths += check_paths_exist(dir_path, check_paths)
        continue

        video_duration += m3u8.video_duration(video_path)
        m3u8.video2audio(video_path, audio_path, m3u8.audio_info(audio_path))
        m3u8.write_audio_info(audio_path)
        not_exist_paths += check_paths_exist(dir_path, check_paths)

    return not_exist_paths, video_duration


def main():
    video_duration = 0
    not_exist_paths = []

    not_exist_paths += dir_batch_operation(setting.WANGYI_VIDEO_PATH)[0]
    not_exist_paths += dir_batch_operation(setting.IFENG_VIDEO_PATH)[0]

    print(f"Total video duration: {video_duration / 3600:.2f} h")
    ret = '\n'.join(not_exist_paths)
    print(f"Not exist paths:[{ret}]")


if __name__ == '__main__':
    print(str(int(time.time())))
    # url = f"https://upos-sz-mirrorali.bilivideo.com/upgcxcode/53/61/3876153/3876153_da8-1-30216.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline={t}&gen=playurlv2&os=alibv&oi=3707331698&trid=3a80c0427da8456abae003a8541a690fp&mid=0&platform=pc&upsig=defd7b6bd54065ff246bde0e3e39434b&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&bvc=vod&nettype=0&orderid=0,3&buvid=18FA8D3C-729F-A603-6909-63DA246F8B6414403infoc&build=0&f=p_0_0&agrr=1&bw=8394&logo=80000000"
