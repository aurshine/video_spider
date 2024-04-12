import os

from tqdm import tqdm

import m3u8
import setting
import wangyi


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
        not_exist_paths += check_paths_exist(dir_path, check_paths)

        video_path = os.path.join(dir_path, 'video.mp4')
        audio_path = os.path.join(dir_path, 'audio.mp3')
        m3u8.video2audio(video_path, audio_path, m3u8.audio_info(audio_path))
        m3u8.write_audio_info(audio_path)
        not_exist_paths += check_paths_exist(dir_path, check_paths)

        video_duration += m3u8.video_duration(video_path)
    return not_exist_paths, video_duration


def main():
    video_duration = 0
    not_exist_paths = []

    video_duration += dir_batch_operation(setting.WANGYI_VIDEO_PATH)[1]
    video_duration += dir_batch_operation(setting.IFENG_VIDEO_PATH)[1]

    print(f"Total video duration: {video_duration / 3600:.2f} h")
    print(f"Not exist paths:\n[{'\n'.join(not_exist_paths)}]")


if __name__ == '__main__':
    main()