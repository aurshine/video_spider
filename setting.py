import os

# 央视频文件夹地址
YANG_VIDEO_PATH = os.path.join(os.path.dirname(__file__), 'yangshiping')

# 凤凰网视频文件夹地址
IFENG_VIDEO_PATH = os.path.join(os.path.dirname(__file__), 'ifeng')

# 网易视频文件夹地址
WANGYI_VIDEO_PATH = os.path.join(os.path.dirname(__file__), 'wangyi')

for path in [YANG_VIDEO_PATH, IFENG_VIDEO_PATH]:
    if not os.path.exists(path):
        os.makedirs(path)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'
    ''
}

PROXY = {
    'http': '',
    'https': ''
}