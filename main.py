import os
import time
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor as Pool

import m3u8
import setting
import delay


def main():

    m3u8.download_m3u8_video('http://flv5.bn.netease.com/live163/videoedit/2024/03/11/20240311155241VID18809CROPgmit9SEP_29886.m3u8', 'a.mp4', cover=True)


@delay.Delay(3, 3)
def delay_test():
    print('test delay')


if __name__ == '__main__':
    with Pool(max_workers=5) as pool:
        for i in range(10):
            pool.submit(delay_test)
    print('over')