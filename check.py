import os
import shutil
from typing import List

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


def check_duration(video_dirs: List[str] = None, unit: str = None) -> float:
    """
    检查 video_dirs 中所有视频文件的总时长

    :param video_dirs: 视频文件夹地址列表, 为空时会从控制台输入

    :param unit: 时间单位, 可选为 'h' (小时), 'm' (分钟) 's'(秒)

    :return: 视频总时长
    """
    video_duration = 0

    if video_dirs is None:
        video_dirs = input('输入文件夹地址, 用空格分隔: ').split()

    if unit is None:
        unit = input('输入时间单位, 可选: h (小时), m (分钟) s(秒): ').strip()

    while unit not in ['h', 'm', 's']:
        print('时间单位输入错误')
        unit = input('输入时间单位, 可选: h (小时), m (分钟) s(秒): ').strip()

    for video_dir in video_dirs:
        for path in tqdm(os.listdir(video_dir)):
            path = os.path.join(video_dir, path)
            if not os.path.isdir(path):
                continue

            video_path = os.path.join(path, 'video.mp4')
            video_duration += m3u8.video_duration(video_path)

    if unit == 'h':
        video_duration /= 3600
    elif unit == 'm':
        video_duration /= 60

    print(f'视频总时长: {video_duration: .2f}{unit}')

    return video_duration


def check_num_files(path: str = None):
    """
    检查 path 下的文件数量

    :param path: 文件夹地址

    :return:
    """
    if path is None:
        path = input('输入文件夹地址: ')

    if not os.path.exists(path):
        num_files = 0
    elif not os.path.isdir(path):
        num_files = 1
    else:
        num_files = len(os.listdir(path))

    print(f'文件夹 {path} 下共有 {num_files} 个文件')

    return num_files


def check_dfs_num_files(path: str = None, root=True):
    """
    递归检查 path 下的文件数量

    :param path: 文件夹地址

    :param root: 是否是根目录

    :return: 文件数量
    """
    if path is None:
        path = input('输入文件夹地址: ')

    num_files = 0
    if not os.path.exists(path):
        num_files = 0
    elif not os.path.isdir(path):
        num_files = 1
    else:
        for sub_path in os.listdir(path):
            sub_path = os.path.join(path, sub_path)
            num_files += check_dfs_num_files(sub_path, False)

    if root:
        print(f'文件夹 {path} 下共有 {num_files} 个文件')
    return num_files


def check_delete(dir_name):
    """
    删除 ./wangyi/dir_name 文件夹, 仅限wangyi文件夹使用

    :param dir_name: 文件夹名
    """
    dir_name = os.path.join(setting.WANGYI_VIDEO_PATH, dir_name)
    if os.path.exists(dir_name):
        if os.path.isdir(dir_name):
            shutil.rmtree(dir_name)
        else:
            os.remove(dir_name)


def check_deletes(dir_names: List[str] = None):
    """
    批量删除 ./wangyi/dir_name 文件夹, 仅限wangyi文件夹使用

    :param dir_names:
    """
    if dir_names is None:
        dir_names = input('输入文件夹名, 用空格分隔: ').split()

    lines = None
    with open(wangyi.DOWNLOAD_URL_PATH, 'r', encoding='utf-8') as f:
        lines = set(f.readlines())

    for dir_name in dir_names:
        check_delete(dir_name)
        if dir_name in lines:
            lines.remove(dir_name)

    with open(wangyi.DOWNLOAD_URL_PATH, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def check_complete_dir(dir_name):
    """
    判断 ./wangyi/dir_name 文件夹是否下载完成

    """
    COMPLETE_FILES = ['video.mp4']

    dir_name = os.path.join(setting.WANGYI_VIDEO_PATH, dir_name)
    if os.path.isdir(dir_name):
        for file_name in COMPLETE_FILES:
            file_path = os.path.join(dir_name, file_name)
            if not os.path.exists(file_path):
                return False

    return True


def delete_not_complete_dirs():
    """
    删除 ./wangyi/dir_name 不完整的文件夹, 仅限wangyi文件夹使用
    """
    dir_names = filter(lambda x: not check_complete_dir(x), os.listdir(setting.WANGYI_VIDEO_PATH))
    check_deletes(dir_names)
    print('删除:\n', '\n'.join(dir_names))


def check_help(commands):
    print('命令列表: ', ', '.join(commands.keys()))


if __name__ == '__main__':
    inputs = input('command: ')
    COMMANDS = {'help': check_help,
                'duration': check_duration,
                'num_files': check_num_files,
                'dfs_num_files': check_dfs_num_files,
                'del': check_deletes,
                'del_n_complete': delete_not_complete_dirs,
                }

    if inputs in COMMANDS.keys():
        if inputs == 'help':
            check_help(COMMANDS)
        else:
            COMMANDS[inputs]()
    else:
        print('输入错误')