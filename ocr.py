from typing import Optional, Union, List
import logging

import numpy as np
from paddleocr import PaddleOCR
import cv2
import pysrt

from delay import run_date

# 关闭paddleocr的日志输出
logging.disable(logging.DEBUG)
# paddleocr识别器
OCR = None  # PaddleOCR(use_angle_cls=True, lang="ch")


class SubTitleBox:
    """
    OCR识别出的字幕框

    包含左上角、右下角坐标、文字内容、置信度
    """
    def __init__(self, l_top=None, r_top=None, r_bottom=None, l_bottom=None, text=None, confidence=None,
                 paddle_ocr_ret=None,
                 start_time: int = 0,
                 end_time: int = 0):
        """
        初始化字幕框

        :param l_top: 左上角x坐标

        :param r_top: 右上角x坐标

        :param r_bottom: 右下角x坐标

        :param l_bottom: 左下角x坐标

        :param text: 文字内容

        :param confidence: 置信度

        :param paddle_ocr_ret: paddleocr识别结果，包含位置信息、文字内容、置信度

        :param start_time: 字幕开始时间, 单位: ms

        :param end_time: 字幕结束时间, 单位: ms
        """
        if paddle_ocr_ret:
            self.l_top = paddle_ocr_ret[0][0]
            self.r_top = paddle_ocr_ret[0][1]
            self.r_bottom = paddle_ocr_ret[0][2]
            self.l_bottom = paddle_ocr_ret[0][3]
            self.text = paddle_ocr_ret[1][0]
            self.confidence = paddle_ocr_ret[1][1]
        else:
            self.l_top = l_top
            self.l_bottom = l_bottom
            self.r_top = r_top
            self.r_bottom = r_bottom
            self.text = text
            self.confidence = confidence

        self.start_time = pysrt.SubRipTime.coerce(start_time)
        self.end_time = pysrt.SubRipTime.coerce(end_time)

    def __le__(self, other: 'SubTitleBox'):
        t1 = (self.start_time, self.end_time, self.l_top, self.l_bottom, self.r_top, self.r_bottom, self.confidence)
        t2 = (other.start_time, other.end_time, other.l_top, other.l_bottom, other.r_top, other.r_bottom, other.confidence)
        return t1 <= t2


def image_ocr(img: Union[np.ndarray, str, bytes, list]) -> Optional[List[SubTitleBox]]:
    """
    识别图片中的文字

    :param img: 图片路径或图片数据

    :return: 识别结果列表，每个元素为字典，包含文字位置信息、文字内容、置信度, 若识别失败则返回空列表
    """
    global OCR
    if OCR is None:
        OCR = PaddleOCR(use_angle_cls=True, lang="ch")
    try:
        return [SubTitleBox(paddle_ocr_ret=ret) for ret in OCR.ocr(img, cls=True)[0]]
    except Exception:
        return []


class VideoOCR:
    def __init__(self, video: Union[cv2.VideoCapture, str]):
        if isinstance(video, str):
            self.video = cv2.VideoCapture(video)
        else:
            self.video = video

        if not self.video.isOpened():
            raise cv2.error("Error opening video stream or file")

        # 一帧的时间间隔, 单位: ms
        self.frame_duration = 1000 / self.video.get(cv2.CAP_PROP_FPS)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.video.release()

    def get(self, prop_id):
        return self.video.get(prop_id)

    def ocr(self, skip_frames: int = 10) -> List[SubTitleBox]:
        """
        识别视频中的所有文字

        :param skip_frames: 跳过的帧数，默认10

        :return: 返回识别的字幕列表, 列表按升序排列
        """
        assert skip_frames > 0, "skip_frames must be greater than 0"

        if skip_frames is None:
            skip_frames = self.get(cv2.CAP_PROP_FPS)

        # 已经读取的帧数
        frame_count = 0
        subitems: List[SubTitleBox] = []
        while True:
            ret, frame = self.video.read()
            if not ret:
                break

            if frame_count % skip_frames == 0:
                # 截取下半部分图片进行识别
                subtitle_boxes = image_ocr(frame[2 * frame.shape[0] // 3:])

                start = max(0, int((frame_count - skip_frames) * self.frame_duration))
                end = int(frame_count * self.frame_duration)

                # 从下往上放入
                for box in subtitle_boxes[::-1]:
                    subitems.append(SubTitleBox(l_bottom=box.l_bottom, r_bottom=box.r_bottom, l_top=box.l_top, r_top=box.r_top, text=box.text, confidence=box.confidence, start_time=start, end_time=end))
            frame_count += 1

        return subitems


@run_date
def subtitle_ocr(video: Union[cv2.VideoCapture, str], srt_path: str, skip_frames: int = 10, eps: float = 3, max_sec: int = 5) -> int:
    """
    识别视频中的字幕, 智能过滤背景噪声

    :param video: 视频路径或cv2.VideoCapture对象

    :param srt_path: 字幕文件路径

    :param skip_frames: 跳过的帧数，默认10

    :param eps: 字幕框x轴的中点与视频x轴的中点的可接受误差，若在误差内则认为字幕框为有效

    :param max_sec: 字幕出现的最大秒数，超过秒数则将该字幕加入黑名单

    :return: 返回实际保存的字幕数量
    """
    with VideoOCR(video) as video:
        # 视频x轴的中点
        half_w = video.video.get(cv2.CAP_PROP_FRAME_WIDTH) / 2
        # 字幕黑名单
        black_list = set()
        # 每个字幕出现的次数
        counter = {}
        # 字幕出现的最大次数, 时间 * 每秒的帧数 // 跳过的帧数
        max_count = max_sec * video.get(cv2.CAP_PROP_FPS) // skip_frames

        def check_black_list(_box):
            """
            检查当前字幕是否在黑名单中
            """
            if _box.text not in black_list and counter.get(_box.text, 0) > max_count:
                black_list.add(_box.text)

            return _box.text in black_list

        def check_middle(_box: SubTitleBox):
            """
            检查当前字幕是否在视频中间
            """
            return abs((_box.l_top[0] + _box.r_top[0]) / 2 - half_w) < eps

        selected_boxes = []
        for box in video.ocr(skip_frames):
            # 不在黑名单中, 且在识别框居中
            if not check_black_list(box) and check_middle(box):
                counter.setdefault(box.text, 0)
                counter[box.text] += 1  # 字幕出现次数 + 1

                if selected_boxes and selected_boxes[-1].text == box.text:
                    # 上一个字幕框与当前字幕框相同, 更新结束时间
                    selected_boxes[-1].end = box.end_time
                else:
                    # 新增字幕框
                    selected_boxes.append(pysrt.SubRipItem(index=len(selected_boxes) + 1,
                                                           text=box.text,
                                                           start=box.start_time,
                                                           end=box.end_time))

        # print(black_list)
        # print([box.text for box in selected_boxes])
        # print(counter)

        save_srt = filter(lambda _box: _box.text not in black_list, selected_boxes)
        # 保存字幕文件
        sub_rip_file = pysrt.SubRipFile(save_srt)
        sub_rip_file.save(srt_path, encoding='utf-8')
        return len(sub_rip_file)
