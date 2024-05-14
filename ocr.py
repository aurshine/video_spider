from typing import Optional, Union, List

import numpy as np
from paddleocr import PaddleOCR
import cv2
import pysrt


# 识别器
OCR = PaddleOCR(use_angle_cls=True, lang="ch")


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

        # 一帧的时间间隔
        self.frame_duration = 1 / self.video.get(cv2.CAP_PROP_FPS)

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
                # 单位: ms
                # 截取下半部分图片进行识别
                subtitle_boxes = image_ocr(frame[2 * frame.shape[0] // 3:])

                start = max(0, int((frame_count - skip_frames) * self.frame_duration * 1000))
                end = int(frame_count * self.frame_duration * 1000)

                # 从下往上放入
                for box in subtitle_boxes[::-1]:
                    subitems.append(SubTitleBox(l_bottom=box.l_bottom, r_bottom=box.r_bottom, l_top=box.l_top, r_top=box.r_top, text=box.text, confidence=box.confidence, start_time=start, end_time=end))
            frame_count += 1

        return subitems


def subtitle_ocr(video: Union[cv2.VideoCapture, str], srt_path: str, skip_frames: int = 10, eps: float = 3, max_count: int = 5):
    """
    识别视频中的字幕, 智能过滤背景噪声

    :param video: 视频路径或cv2.VideoCapture对象

    :param srt_path: 字幕文件路径

    :param skip_frames: 跳过的帧数，默认10

    :param eps: 字幕框x轴的中点与视频x轴的中点的可接受误差，若在误差内则认为字幕框为有效

    :param max_count: 字幕出现的最大次数，超过次数则将该字幕加入黑名单

    :return:
    """
    with VideoOCR(video) as video:
        # 视频x轴的中点
        half_w = video.video.get(cv2.CAP_PROP_FRAME_WIDTH) / 2
        # 字幕时间戳
        timestamp = {}
        # 字幕黑名单
        black_list = set()
        # 每个字幕出现的次数
        counter = {}

        def check_black_list(_box):
            """
            检查当前字幕是否在黑名单中
            """
            if _box.text in black_list:
                return True

            counter.setdefault(_box.text, 0)
            counter[_box.text] += 1
            if counter[_box.text] > max_count:
                black_list.add(_box.text)

            return _box.text in black_list

        def check_neighbour(_box: SubTitleBox):
            """
            检查当前字幕是否与上一个字幕相邻

            并跟新_box.text出现的时间戳
            """
            last_time = timestamp.get(_box.text, None)
            timestamp[_box.text] = _box.end_time
            return last_time is None or _box.start_time - last_time > int(1000 * video.frame_duration * skip_frames)

        def check_middle(_box: SubTitleBox):
            """
            检查当前字幕是否在视频中间
            """
            return abs((_box.l_top[0] + _box.r_top[0] + _box.l_bottom[0] + _box.r_bottom[0]) / 4 - half_w) < eps

        selected_boxes = []
        for box in video.ocr(skip_frames):
            if not check_black_list(box) and check_middle(box) and check_neighbour(box):
                if selected_boxes and selected_boxes[-1].text == box.text:
                    # 上一个字幕框与当前字幕框相同, 更新结束时间
                    selected_boxes[-1].end = box.end_time
                else:
                    # 新增字幕框
                    selected_boxes.append(pysrt.SubRipItem(index=len(selected_boxes) + 1,
                                                           text=box.text,
                                                           start=box.start_time,
                                                           end=box.end_time))
        # 保存字幕文件
        pysrt.SubRipFile([box for box in selected_boxes if box.text not in black_list]).save(srt_path, encoding='utf-8')
