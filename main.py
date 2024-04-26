import os
import time
import json
from tqdm import tqdm

import m3u8
import setting
import delay


def main():

    m3u8.download_m3u8_video('http://flv5.bn.netease.com/live163/videoedit/2024/03/11/20240311155241VID18809CROPgmit9SEP_29886.m3u8', 'a.mp4', cover=True)


if __name__ == '__main__':
    json_obj = m3u8.request_text('https://app.api.btime.com/video/play', params={'_': delay.get_time(13), 'id': '23dlbq3u4glmu2gpokto0jhlqmj'})
    video_url = json.loads(json_obj)['data']['video_stream'][0]['stream_url']
    m3u8.download_mp4_video(video_url, 'a.mp4', cover=True)