import os

# 凤凰网视频文件夹地址
IFENG_VIDEO_PATH = os.path.join(os.getcwd(), 'ifeng')

# 网易视频文件夹地址
WANGYI_VIDEO_PATH = os.path.join(os.getcwd(), 'wangyi')

# 网易直播视频文件夹地址
WANGYI_LIVE_VIDEO_PATH = os.path.join(os.getcwd(), 'wangyi_live')

# 北京卫视视频文件夹地址
BRTV_VIDEO_PATH = os.path.join(os.getcwd(), 'brtv')

# 洛谷文件夹
LUOGU_PATH = os.path.join(os.getcwd(), 'luogu')

for path in [IFENG_VIDEO_PATH, WANGYI_LIVE_VIDEO_PATH, LUOGU_PATH, BRTV_VIDEO_PATH]:
    if not os.path.exists(path):
        os.makedirs(path)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'
}

PROXY = {
    'http': '',
    'https': ''
}