import os

PATHS = []
# 凤凰网视频文件夹地址
IFENG_VIDEO_PATH = os.path.join(os.path.dirname(__file__), 'ifeng')
PATHS.append(IFENG_VIDEO_PATH)

# 网易视频文件夹地址
WANGYI_VIDEO_PATH = os.path.join(os.path.dirname(__file__), 'wangyi')
PATHS.append(WANGYI_VIDEO_PATH)

# 网易直播视频文件夹地址
WANGYI_LIVE_VIDEO_PATH = os.path.join(os.path.dirname(__file__), 'wangyi_live')
PATHS.append(WANGYI_LIVE_VIDEO_PATH)

# 北京卫视视频文件夹地址
BRTV_VIDEO_PATH = os.path.join(os.path.dirname(__file__), 'brtv')
PATHS.append(BRTV_VIDEO_PATH)

# acfun视频文件夹地址
ACFUN_VIDEO_PATH = os.path.join(os.path.dirname(__file__), 'acfun')
PATHS.append(ACFUN_VIDEO_PATH)

for path in PATHS:
    if not os.path.exists(path):
        os.makedirs(path)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'
}

PROXY = {
    'http': '',
    'https': ''
}