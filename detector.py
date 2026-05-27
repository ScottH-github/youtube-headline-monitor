"""頭條區塊偵測模組（固定區塊 + 多色判斷）"""

import cv2
import numpy as np
import config


def crop_headline_region(frame: np.ndarray) -> np.ndarray:
    """裁切頭條固定區塊"""
    h, w = frame.shape[:2]
    x1 = int(w * config.HEADLINE_X_START)
    x2 = int(w * config.HEADLINE_X_END)
    y1 = int(h * config.HEADLINE_Y_START)
    y2 = int(h * config.HEADLINE_Y_END)
    return frame[y1:y2, x1:x2]


def detect_headline(region: np.ndarray):
    """
    判斷裁切區塊內是否有頭條（黃/紅/藍色背景）。
    回傳 (區塊截圖, 顏色名稱) 或 (None, None)。
    """
    if region is None or region.size == 0:
        return None, None

    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    total_pixels = region.shape[0] * region.shape[1]

    # 黃色
    yellow_mask = cv2.inRange(
        hsv,
        np.array([config.YELLOW_H_MIN, config.YELLOW_S_MIN, config.YELLOW_V_MIN]),
        np.array([config.YELLOW_H_MAX, 255, 255]),
    )
    yellow_ratio = cv2.countNonZero(yellow_mask) / total_pixels

    # 紅色（兩段 H 範圍）
    red_mask1 = cv2.inRange(
        hsv,
        np.array([config.RED_H_MIN1, config.RED_S_MIN, config.RED_V_MIN]),
        np.array([config.RED_H_MAX1, 255, 255]),
    )
    red_mask2 = cv2.inRange(
        hsv,
        np.array([config.RED_H_MIN2, config.RED_S_MIN, config.RED_V_MIN]),
        np.array([config.RED_H_MAX2, 255, 255]),
    )
    red_ratio = (cv2.countNonZero(red_mask1) + cv2.countNonZero(red_mask2)) / total_pixels

    # 藍色
    blue_mask = cv2.inRange(
        hsv,
        np.array([config.BLUE_H_MIN, config.BLUE_S_MIN, config.BLUE_V_MIN]),
        np.array([config.BLUE_H_MAX, 255, 255]),
    )
    blue_ratio = cv2.countNonZero(blue_mask) / total_pixels

    # 取最高比例的顏色
    ratios = {"yellow": yellow_ratio, "red": red_ratio, "blue": blue_ratio}
    best_color = max(ratios, key=ratios.get)
    best_ratio = ratios[best_color]

    if best_ratio >= config.MIN_HEADLINE_RATIO:
        return region, best_color

    return None, None


# 向後相容：保留舊函式供參考，但不再使用
def crop_roi(frame: np.ndarray) -> np.ndarray:
    """裁切 ROI 區域（右半畫面）— 已棄用，改用 crop_headline_region"""
    h, w = frame.shape[:2]
    x1 = int(w * config.ROI_X_START) if hasattr(config, 'ROI_X_START') else int(w * 0.5)
    x2 = int(w * config.ROI_X_END) if hasattr(config, 'ROI_X_END') else w
    return frame[0:h, x1:x2]
