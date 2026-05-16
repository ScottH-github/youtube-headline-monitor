"""OCR 辨識模組：透過落地 LLM 進行多模態辨識"""

import base64
import cv2
import numpy as np
import requests
import config


def ocr_headline(headline_crop: np.ndarray) -> str:
    """將黃色區塊截圖送至落地 LLM 進行 OCR"""
    h, w = headline_crop.shape[:2]
    if w > config.LLM_RESIZE_WIDTH:
        ratio = config.LLM_RESIZE_WIDTH / w
        headline_crop = cv2.resize(headline_crop, (config.LLM_RESIZE_WIDTH, int(h * ratio)))

    _, buffer = cv2.imencode(".jpg", headline_crop, [cv2.IMWRITE_JPEG_QUALITY, 85])
    b64_image = base64.b64encode(buffer).decode("utf-8")

    payload = {
        "model": config.LLM_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "請辨識圖片中的所有文字，只輸出辨識到的文字內容，不要加任何說明或格式。",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_image}"
                        },
                    },
                ],
            }
        ],
        "max_tokens": config.LLM_MAX_TOKENS,
        "temperature": 0.1,
    }

    try:
        resp = requests.post(config.LLM_API_URL, json=payload, timeout=config.LLM_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"].get("content", "")
        return content.strip()
    except Exception as e:
        print(f"[OCR] LLM 呼叫失敗: {e}")
        return ""
