import os
import time
from tqdm import tqdm

import m3u8
import setting
import delay


def main():

    m3u8.download_m3u8_video('http://flv5.bn.netease.com/live163/videoedit/2024/03/11/20240311155241VID18809CROPgmit9SEP_29886.m3u8', 'a.mp4', cover=True)


if __name__ == '__main__':
    print(delay.get_time(30))