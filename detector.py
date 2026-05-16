"""黃色區塊偵測模組"""

import cv2
import numpy as np
import config


def crop_roi(frame: np.ndarray) -> np.ndarray:
    """裁切 ROI 區域（右半畫面）"""
    h, w = frame.shape[:2]
    x1 = int(w * config.ROI_X_START)
    x2 = int(w * config.ROI_X_END)
    y1 = int(h * config.ROI_Y_START)
    y2 = int(h * config.ROI_Y_END)
    return frame[y1:y2, x1:x2]


def detect_yellow_region(roi: np.ndarray):
    """
    在 ROI 中偵測黃色大面積區塊。
    回傳 (黃色區塊截圖, 邊界框座標) 或 (None, None)。
    邊界框座標為相對於 ROI 的 (x, y, w, h)。
    """
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    lower_yellow = np.array([config.YELLOW_H_MIN, config.YELLOW_S_MIN, config.YELLOW_V_MIN])
    upper_yellow = np.array([config.YELLOW_H_MAX, config.YELLOW_S_MAX, config.YELLOW_V_MAX])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # 形態學操作：去雜訊 + 連接相鄰區塊
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, None

    roi_area = roi.shape[0] * roi.shape[1]
    min_area = roi_area * config.MIN_YELLOW_AREA_RATIO

    # 找最大的黃色區塊
    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)

    if area < min_area:
        return None, None

    x, y, w, h = cv2.boundingRect(largest)

    roi_h, roi_w = roi.shape[:2]

    # 寬度必須佔 ROI 寬度的 60% 以上（頭條橫幅是寬條狀）
    if w < roi_w * 0.6:
        return None, None

    # 頭條位置必須在 ROI 的 30%~80% 範圍內（排除最頂部和最底部）
    if y < roi_h * 0.25 or y > roi_h * 0.8:
        return None, None

    # 稍微擴展邊界框，確保文字不被裁掉
    pad_x = int(w * 0.02)
    pad_y = int(h * 0.05)
    x = max(0, x - pad_x)
    y = max(0, y - pad_y)
    w = min(roi.shape[1] - x, w + 2 * pad_x)
    h = min(roi.shape[0] - y, h + 2 * pad_y)

    headline_crop = roi[y:y+h, x:x+w]
    return headline_crop, (x, y, w, h)
