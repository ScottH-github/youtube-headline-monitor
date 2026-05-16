"""去重模組：圖像 SSIM + 文字相似度"""

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from difflib import SequenceMatcher
import config


class Deduplicator:
    def __init__(self):
        self._last_headline_gray = None

    def is_same_image(self, headline_crop: np.ndarray) -> bool:
        """SSIM 比對：跟上一張黃色區塊截圖比較"""
        gray = cv2.cvtColor(headline_crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (320, 80))

        if self._last_headline_gray is None:
            self._last_headline_gray = gray
            return False

        score = ssim(self._last_headline_gray, gray)
        self._last_headline_gray = gray
        return score > config.SSIM_THRESHOLD

    @staticmethod
    def is_duplicate_text(new_text: str, history_texts: list[str]) -> bool:
        """文字相似度比對：跟所有歷史記錄比較"""
        if not new_text.strip():
            return True

        for old_text in history_texts:
            ratio = SequenceMatcher(None, new_text, old_text).ratio()
            if ratio > config.TEXT_SIMILARITY_THRESHOLD:
                return True
        return False
