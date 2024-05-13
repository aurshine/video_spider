from typing import Optional, Union, List

import numpy as np
from paddleocr import PaddleOCR
import cv2
import pysrt


# 识别器
OCR = PaddleOCR(use_angle_cls=True, lang="ch")


def image_ocr(img: Union[np.ndarray, str, bytes, list]) -> Optional[List[dict]]:
    """
    识别图片中的文字

    :param img: 图片路径或图片数据

    :return: 识别结果列表，每个元素为字典，包含文字位置信息、文字内容、置信度, 若识别失败则返回None
    """
    rets = OCR.ocr(img, cls=True)[0]
    if not rets:
        return None

    return [{
            "l_top": ret[0][0],
            "l_bottom": ret[0][1],
            "r_top": ret[0][2],
            "r_bottom": ret[0][3],
            "text": ret[1][0],
            "confidence": ret[1][1],
            } for ret in rets]


class VideoOCR:
    def __init__(self, video: Union[cv2.VideoCapture, str]):
        if isinstance(video, str):
            self.video = cv2.VideoCapture(video)
        else:
            self.video = video

        if not self.video.isOpened():
            raise cv2.error("Error opening video stream or file")

        # 一帧的时间间隔
        self.frame_duration = 1 / self.video.get(cv2.CAP_PROP_FPS)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.video.release()

    def get(self, prop_id):
        return self.video.get(prop_id)

    def ocr(self, srt_path: str, skip_frames: int = 10):
        """
        识别视频中的字幕, 只识别最下面出现的字体

        :param srt_path: 字幕文件路径

        :param skip_frames: 跳过的帧数，默认10
        """
        assert skip_frames > 0, "skip_frames must be greater than 0"

        if skip_frames is None:
            skip_frames = self.get(cv2.CAP_PROP_FPS)

        # 已经读取的帧数
        frame_count = 0
        subitems = []
        while True:
            ret, frame = self.video.read()
            if not ret:
                break

            if frame_count % skip_frames == 0:
                # 单位: ms
                img_ocr = image_ocr(frame)
                if not img_ocr:
                    continue

                # 取最下面出现的字体
                text = img_ocr[-1]["text"]
                start = max(0, int((frame_count - 1) * skip_frames * self.frame_duration * 1000))
                end = int(frame_count * skip_frames * self.frame_duration * 1000)
                if subitems and subitems[-1].text == text:
                    subitems[-1].end = pysrt.SubRipTime.coerce(end)
                else:
                    subitems.append(pysrt.SubRipItem(index=len(subitems) + 1,
                                                     text=text,
                                                     start=start,
                                                     end=end))
            frame_count += 1

        subtitles = pysrt.SubRipFile()
        subtitles.extend(subitems)
        subtitles.save(srt_path, encoding="utf-8")


def video_ocr(video: Union[cv2.VideoCapture, str], srt_path: str, skip_frames: int = 10):
    """
    识别视频中的文字

    :param video: 视频路径或cv2.VideoCapture对象

    :param srt_path: 字幕文件路径

    :param skip_frames: 跳过的帧数，默认10

    :return: 识别成功返回True
    """
    try:
        with VideoOCR(video) as video:
            video.ocr(srt_path, skip_frames)

        return True
    except cv2.error:
        return False
