import os
import shutil
from typing import List, Union, Tuple, Optional

from tqdm import tqdm

import m3u8


ROOT = os.path.dirname(os.path.abspath(__file__))


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


def check_duration(video_dirs: List[str] = None, unit: str = 'h') -> float:
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


def check_num_files(path: str = None) -> int:
    """
    检查 path 下的文件数量

    :param path: 文件夹地址

    :return: 文件数量
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


def check_dfs_num_files(path: str = None, root=True) -> int:
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


def check_delete(dir_name: str) -> None:
    """
    删除 dir_name 文件夹

    :param dir_name: 文件夹名
    """
    if os.path.exists(dir_name):
        if os.path.isdir(dir_name):
            shutil.rmtree(dir_name)
            print(f'删除文件夹 {dir_name}')
        else:
            os.remove(dir_name)
            print(f'删除文件 {dir_name}')


def check_deletes(dir_names: Union[str, List[str]]) -> None:
    """
    批量删除 ./dir_name 文件夹

    :param dir_names: 文件夹名列表
    """
    if isinstance(dir_names, str):
        dir_names = [dir_names]

    for dir_name in dir_names:
        check_delete(dir_name)


def check_size(dir_name, unit: Optional[str] = 'g') -> Tuple[float, int]:
    """
    检查 文件夹的大小

    :param dir_name:

    :param unit: 单位, 可选: b (B), k (KB), m (MB), g (GB) t(TB)

    :return: 文件夹大小
    """
    dir_name = os.path.join(ROOT, dir_name)

    size, cnt = 0, 0
    if os.path.isdir(dir_name):
        for sub_path in os.listdir(dir_name):
            _size, _cnt = check_size(os.path.join(dir_name, sub_path), None)

            size += _size
            cnt += _cnt
    else:
        cnt = 1
        size = os.path.getsize(dir_name)

    if unit == 'k':
        size /= 1024
    elif unit == 'm':
        size /= 1024 ** 2
    elif unit == 'g':
        size /= 1024 ** 3
    elif unit == 't':
        size /= 1024 ** 4

    if unit:
        print(f'{dir_name} 大小为 {size: .2f}{unit}  共有{cnt} 个文件)')
    return size, cnt


def ls(dir_name) -> List[str]:
    """
    列出文件夹下的文件

    :param dir_name: 文件夹名

    :return: 文件列表
    """
    paths = [os.path.join(ROOT, dir_name, name) for name in os.listdir(dir_name)]
    return paths


def video_is_error(dir_names: Union[str, List[str]]):
    """
    判断文件夹下的 video.pm4 是否损坏

    :param dir_names: 文件夹地址

    :return: 返回损坏的 video.mp4 路径
    """
    broken_videos = []
    for dir_names in tqdm(dir_names):
        video_path = os.path.join(dir_names, 'video.mp4')
        if not os.path.exists(video_path):
            continue

        if not m3u8.video_is_ok(video_path):
            broken_videos.append(video_path)

    return broken_videos


def dir_names(paths: Union[str, List[str]]):
    """
    获取路径的目录名

    :param paths: 路径列表

    :return: 路径的目录名列表
    """
    if isinstance(paths, str):
        paths = [paths]

    return [os.path.dirname(path) for path in paths if os.path.exists(path)]


def check_print(value):
    """
    打印一个值

    :param value: 值
    """
    if isinstance(value, list):
        value = '\n'.join(value) + f"\n\ntotal = {len(value)}"
    print(value)
    return value


def check_help(args=None) -> None:
    """
    打印命令列表
    """
    print('命令列表: ', '\n'.join(COMMANDS.keys()))


def run_command(command: str, args):
    """
    运行一个命令

    :param command: 命令名

    :param args: 命令参数

    :return: 命令的返回值
    """
    if command in COMMANDS.keys():
        return COMMANDS[command](args)
    else:
        # command 不存在的情况下将 command 解析为一个输入命令
        return command


def run_chain_commands(commands: str):
    """
    运行命令, 可以链式运行多个命令，每个命令用 > 隔开

    上一个命令的输出为下一个命令的输入

    :param commands: 一行输入的命令

    :return: 命令的返回值
    """
    commands = commands.split('>')
    ret = None
    for command in commands:
        command = command.strip()
        ret = run_command(command, ret)

    return ret


def get_history_returns(index=-1):
    """
    获取历史命令的返回值

    :param index: 历史命令的索引

    :return:
    """
    return HISTORY_RETURNS[int(index)]


def check_vi2au(dirs_path: Union[str, List[str]]):
    """
    视频格式转换 mp4 -> wav

    :param dirs_path: 存储视频的文件夹的路径列表, 如 xxx/video_path/video.mp4

    :return: None
    """
    if isinstance(dirs_path, str):
        dirs_path = [dirs_path]

    for dir_path in dirs_path:
        video_path = os.path.join(dir_path, 'video.mp4')

        if not os.path.exists(video_path) or not m3u8.video2audio(video_path):
            check_delete(dir_path)


# 历史命令返回值
HISTORY_RETURNS = []


COMMANDS = {'help': check_help,
            'duration': check_duration,
            'num_files': check_num_files,
            'dfs_num_files': check_dfs_num_files,
            'del': check_deletes,
            'size': check_size,
            'ls': ls,
            'is_error': video_is_error,
            'dir_names': dir_names,
            'len': len,
            'print': check_print,
            'split': str.split,
            'history': get_history_returns,
            'cwd': ROOT,
            'v2a': check_vi2au,
            }


def main():
    num_command = 0
    while True:
        command = input(f'command<{num_command}>: ').strip()
        num_command += 1

        ret = None
        if command == 'exit':
            break
        elif command == '':
            pass
        else:
            ret = run_chain_commands(command)

        HISTORY_RETURNS.append(ret)


if __name__ == '__main__':
    main()