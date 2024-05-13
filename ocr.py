from typing import Union, List

import numpy as np
from paddleocr import PaddleOCR, draw_ocr
import cv2


# 识别器
OCR = PaddleOCR(use_angle_cls=True, lang="ch")


def ocr(img: Union[np.ndarray, str, bytes, list]) -> List[dict]:
    """
    识别图片中的文字

    :param img: 图片路径或图片数据

    :return: 识别结果列表，每个元素为字典，包含文字位置信息、文字内容、置信度
    """
    rets = OCR.ocr(img, cls=True)[0]

    return [{
            "l_top": ret[0][0],
            "l_bottom": ret[0][1],
            "r_top": ret[0][2],
            "r_bottom": ret[0][3],
            "text": ret[1][0],
            "confidence": ret[1][1],
            } for ret in rets]