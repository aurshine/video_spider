import os
import shutil
from typing import List, Union, Tuple, Optional

from tqdm import tqdm

import ocr
import m3u8
from url import UrlSet


ROOT = os.path.dirname(os.path.abspath(__file__))


class Command:
    name = 'Command'

    cmd = ''

    helo_doc = """暂无帮助文档"""

    def __call__(self, root, *args, **kwargs):
        raise NotImplementedError()

    def __hash__(self):
        return hash(self.cmd)

    def __eq__(self, other):
        if isinstance(other, Command):
            return self.cmd == other.cmd
        elif isinstance(other, str):
            return self.cmd == other


class CheckDuration(Command):
    name = 'check_duration'

    cmd = 'duration'

    help_doc = ('检查文件夹包含视频的总时长: 单位(h)\n'
                '传入一个视频文件或文件夹地址, 程序会自动检查该文件夹下所有视频文件的总时长\n'
                '返回视频时间 float\n')

    def __call__(self, path: str, root=True, *args, **kwargs) -> float:
        video_duration = 0

        if os.path.isdir(path):
            for sub_path in os.listdir(path):
                sub_path = os.path.join(path, sub_path)
                video_duration += self(sub_path, root=False)
        elif path.endswith('.mp4'):
            video_duration = m3u8.video_duration(path) / 3600

        if root:
            print(f'视频总时长: {video_duration: .2f}h')

        return video_duration


class CheckDFSNumFiles(Command):
    name = 'check_dfs_num_files'

    cmd = 'dfs_num_files'

    help_doc = '递归检查一个文件夹下的文件数量'

    def __call__(self, path: str = None, root=True, *args, **kwargs) -> int:
        num_files = 0
        if os.path.isdir(path):
            for sub_path in os.listdir(path):
                num_files += self(os.path.join(path, sub_path), root=False)
        else:
            num_files = 1

        if root:
            print(f'文件夹 {path} 下共有 {num_files} 个文件')

        return num_files


class CheckDelete(Command):
    name = 'check_delete'

    cmd = 'del'

    help_doc = '删除一个文件或文件夹'

    def __call__(self, path: str, root=True, *args, **kwargs) -> None:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f'删除文件夹 {path}')
            else:
                os.remove(path)
                print(f'删除文件 {path}')


class CheckSize(Command):
    name = 'check_size'

    cmd = 'size'

    help_doc = '检查文件或文件夹大小, 并计算文件数量'

    def __call__(self, path: str, root=True, *args, **kwargs) -> Tuple[float, int]:
        size, cnt = 0, 0
        if os.path.isdir(path):
            for sub_path in os.listdir(path):
                _size, _cnt = self(os.path.join(path, sub_path), root=False)
                size += _size
                cnt += _cnt
        else:
            size = os.path.getsize(path) / (1024 ** 3)
            cnt = 1

        if root:
            print(f'{path} 大小为{size: .2f}G 共有{cnt}个文件)')

        return size, cnt


class CheckLs(Command):
    name = 'check_ls'

    cmd = 'ls'

    help_doc = '列出文件夹下的文件'

    def __call__(self, path: str, root=True, *args, **kwargs) -> List[str]:
        return [os.path.join(path, sub_path) for sub_path in os.listdir(path)]


class CheckVideoIsError(Command):
    name = 'check_video_is_error'

    cmd = 'is_error'

    help_doc = '检查video.mp4 是否损坏'

    def __call__(self, video_paths: Union[str, List[str]], root=True, *args, **kwargs) -> List[str]:

        if isinstance(video_paths, str):
            video_paths = [video_paths]

        broken_videos = [video_path for video_path in video_paths if not m3u8.video_is_ok(video_path)]
        return broken_videos


class CheckVideo2Audio(Command):
    name = 'check_video2audio'

    cmd = 'v2a'

    help_doc = '视频格式转换 mp4 -> wav'

    def __call__(self, video_path: Union[str, List[str]], root=True, *args, **kwargs):
            if isinstance(video_path, str):
                video_path = [video_path]

            for video in video_path:
                if os.path.exists(video) and not m3u8.video2audio(video):
                    shutil.rmtree(os.path.dirname(video))


class CheckDirNames(Command):
    name = 'check_dir_names'

    cmd = 'dir_names'

    help_doc = ('获取路径的目录名\n'
                '传入任意数量的文件或文件夹路径, 程序会返回该路径的目录名\n')

    def __call__(self, paths: Union[str, List[str]], root=True, *args, **kwargs) -> List[str]:
        if isinstance(paths, str):
            paths = [paths]

        return [os.path.dirname(path) for path in paths if os.path.exists(path)]


class CheckUpdateDownloadUrls(Command):
    name = 'check_update_download_urls'

    cmd = 'update_urls'

    help_doc = '根据子文件夹名，更新下载链接'

    def __call__(self, dir_paths: Union[str, List[str]], root=True, *args, **kwargs):
        if isinstance(dir_paths, str):
            dir_paths = [dir_paths]

        for dir_path in dir_paths:
            url_set = UrlSet(dir_path)
            for sub_path in tqdm(os.listdir(dir_path)):
                if os.path.isdir(os.path.join(dir_path, sub_path)):
                    url_set.add(sub_path)


class CheckCls(Command):
    name = 'check_cls'

    cmd = 'cls'

    help_doc = '清屏'

    def __call__(self, root=True, *args, **kwargs):
        os.system('clear')


class CheckOCR(Command):
    name = 'check_ocr'

    cmd = 'ocr'

    help_doc = '调用百度ocr接口进行文字识别'

    def __call__(self, dir_names: Union[str, List[str]], root=True, *args, **kwargs):
        if isinstance(dir_names, str):
            dir_names = [dir_names]

        for dir_name in dir_names:
            if not os.path.isdir(dir_name):
                continue

            video_path = os.path.join(dir_name, 'video.mp4')
            srt_path = os.path.join(dir_name, 'subtitle.srt')
            audio_path = os.path.join(dir_name, 'audio.wav')
            if os.path.exists(video_path) and not os.path.exists(srt_path):
                if ocr.subtitle_ocr(video_path, srt_path) == 0:
                    CheckDelete()(dir_name, root=False)
                    CheckCls()(root=False)
                    continue

            CheckCls()(root=False)
            m3u8.video2audio(video_path, audio_path, cover=False)
            CheckDelete()(video_path, root=False)


class CheckPrint(Command):
    name = 'check_print'

    cmd = 'print'

    help_doc = '打印一个值'

    def __call__(self, value, root=True, *args, **kwargs):
        if isinstance(value, list):
            print('\n'.join(value) + f"\ntype = list\ntotal = {len(value)}")
        else:
            print(value)
        return value


class CheckHelp(Command):
    name = 'check_help'

    cmd = 'help'

    help_doc = '打印帮助信息'

    def __call__(self, _help=None, *args, **kwargs):
        if _help is None:
            print('可用命令:')
            for command in COMMANDS:
                print(f'name: {command.name}\n')
        else:
            for command in COMMANDS:
                if command.name == _help:
                    print(f'name: {command.name}\n'
                          f'cmd: {command.cmd}\n'
                          f'help_doc: {command.help_doc}\n')


class CheckHistoryReturns(Command):
    name = 'check_history_returns'

    cmd = 'his'

    help_doc = '获取历史命令的返回值'

    def __call__(self, index: int = -1, *args, **kwargs):
        return HISTORY_RETURNS[int(index)]


COMMANDS = {CheckDuration(), CheckDFSNumFiles(), CheckDelete(), CheckSize(), CheckLs(), CheckVideoIsError(),
            CheckVideo2Audio(), CheckDirNames(), CheckUpdateDownloadUrls(), CheckCls(), CheckOCR(), CheckPrint(),
            CheckHelp(), CheckHistoryReturns()}

# 历史命令返回值
HISTORY_RETURNS = []


def run_command(command: str, *args):
    """
    运行一个命令

    :param command: 命令名

    :param args: 命令参数

    :return: 命令的返回值
    """

    for cmd in COMMANDS:
        if cmd == command:
            return cmd(*args)

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