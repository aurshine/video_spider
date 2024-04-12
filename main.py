import os

from tqdm import tqdm

import m3u8
import setting

if __name__ == '__main__':
    video_duration = 0
    for path in tqdm(os.listdir(setting.WANGYI_VIDEO_PATH)):
        dir_path = os.path.join(setting.WANGYI_VIDEO_PATH, path)
        if not os.path.isdir(dir_path):
            continue

        video_path = os.path.join(dir_path, 'video.mp4')
        audio_path = os.path.join(dir_path, 'audio.mp3')
        # m3u8.video2audio(video_path, audio_path)
        with open(os.path.join(dir_path, 'audio_info.txt'), 'w', encoding='utf-8') as f:
            f.write(str(m3u8.audio_info(audio_path)))

        video_duration += m3u8.video_duration(video_path)

    for path in tqdm(os.listdir(setting.IFENG_VIDEO_PATH)):
        dir_path = os.path.join(setting.IFENG_VIDEO_PATH, path)
        if not os.path.isdir(dir_path):
            continue

        video_path = os.path.join(dir_path, 'video.mp4')
        audio_path = os.path.join(dir_path, 'audio.mp3')
        # m3u8.video2audio(video_path, audio_path)
        with open(os.path.join(dir_path, 'audio_info.txt'), 'w', encoding='utf-8') as f:
            f.write(str(m3u8.audio_info(audio_path)))

        video_duration += m3u8.video_duration(video_path)

    print(f"Total video duration: {video_duration / 3600:.2f} h")