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
                        "text": "這是一張新聞頭條截圖。請辨識圖片中的新聞標題文字，只輸出純文字內容。規則：1.只輸出新聞標題文字 2.不要輸出JSON、座標、說明 3.如果看不清楚就回覆空白 4.不要加引號或格式標記",
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
        return _clean_ocr_output(content)
    except Exception as e:
        print(f"[OCR] LLM 呼叫失敗: {e}")
        return ""


def _clean_ocr_output(text: str) -> str:
    """清理 LLM OCR 輸出，移除非文字內容"""
    import re
    text = text.strip()
    if not text:
        return ""

    # 移除 thinking tags（Gemma 4 thinking mode）
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    # 如果回傳 JSON → 丟棄
    if text.startswith("{") or text.startswith("["):
        return ""

    # 如果是 LLM 拒絕/解釋訊息 → 丟棄
    refusal_patterns = [
        "由於", "抱歉", "無法辨識", "解析度", "藝術化", "模糊",
        "I cannot", "I can't", "sorry", "unable to",
        "圖片中沒有", "看不清", "不包含文字",
    ]
    first_line = text.split("\n")[0]
    if any(p in first_line for p in refusal_patterns):
        return ""

    # 取第一行有意義的文字（LLM 有時多行解釋）
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines:
        text = lines[0]

    # 移除常見包裹符號
    text = text.strip('"\'「」『』【】')

    return text.strip()
