import requests
from concurrent.futures import ThreadPoolExecutor as Pool

import setting
import ifeng

with Pool(max_workers=4) as pool:
    for channel_id in ifeng.CHANNEL_IDS[3:]:
        resp = requests.get(ifeng.make_ifeng_api_url(1, 1000, channel_id), headers=setting.HEADERS)
        # 解析 json 数据
        datas = ifeng.parse_ifeng_response(resp.text)

        try:
            # 下载视频
            for data in datas:
                pool.submit(ifeng.download_ifeng_video, data, 2, 5)
        except Exception as e:
            print(f'下载出错: {e}')
