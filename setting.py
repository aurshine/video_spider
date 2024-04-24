import os

# 央视频文件夹地址
YANG_VIDEO_PATH = os.path.join(os.getcwd(), 'yangshiping')

# 凤凰网视频文件夹地址
IFENG_VIDEO_PATH = os.path.join(os.getcwd(), 'ifeng')

# 网易视频文件夹地址
WANGYI_VIDEO_PATH = os.path.join(os.getcwd(), 'wangyi')

# 网易公开课视频文件夹地址
WANGYI_PUB_VIDEO_PATH = os.path.join(os.getcwd(), 'wangyi_pub')

# 网易直播视频文件夹地址
WANGYI_LIVE_VIDEO_PATH = os.path.join(os.getcwd(), 'wangyi_live')

# 一席演讲视频文件夹地址
YIXI_VIDEO_PATH = os.path.join(os.getcwd(), 'yixi')

# 洛谷文件夹
LUOGU_PATH = os.path.join(os.getcwd(), 'luogu')

for path in [YANG_VIDEO_PATH, IFENG_VIDEO_PATH, WANGYI_PUB_VIDEO_PATH, WANGYI_LIVE_VIDEO_PATH, YIXI_VIDEO_PATH, LUOGU_PATH]:
    if not os.path.exists(path):
        os.makedirs(path)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'
}

PROXY = {
    'http': '',
    'https': ''
}