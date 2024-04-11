import os

import m3u8
import setting

if __name__ == '__main__':
    video_duration = 0
    for path in os.listdir(setting.WANGYI_VIDEO_PATH):
        video_path = os.path.join(setting.WANGYI_VIDEO_PATH, path, 'video.mp4')
        video_duration += m3u8.video_duration(video_path)

    print(f"Total video duration: {video_duration / 3600:.2f} h")
