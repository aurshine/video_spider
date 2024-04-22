import os
import time
from tqdm import tqdm

import m3u8
import setting


def main():
    url = """https://v9-xg-web-pc.ixigua.com/c781e82bdc109039cdab5e9467a980f4/6625d56b/video/tos/cn/tos-cn-o-0004/364299e10cab46a2b3674de4f3adab11/media-video-avc1/?a=1768&ch=0&cr=0&dr=0&er=0&cd=0%7C0%7C0%7C0&cv=1&br=339&bt=339&cs=0&ds=1&eid=21760&mime_type=video_mp4&qs=0&rc=OjY5O2Y3ZTQ8ZWc4M2hpZUBpamdycDQ6ZnZncjMzNDczM0BgYzBjMzI0Nl4xYjQyXzUzYSNzM2hlcjRnZjJgLS1kLWFzcw%3D%3D&btag=e00030000&dy_q=1713751338&l=2024042210021898AEB000CF4D370B4659"""
    m3u8.download_mp4_video(url, 'video.mp4')


if __name__ == '__main__':
    print(os.getcwd())
    # main()