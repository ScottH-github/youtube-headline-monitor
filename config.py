"""可調參數設定"""
import os

# YouTube 串流
STREAM_QUALITY = "720p"  # 串流畫質

# 取樣間隔（秒）
SAMPLE_INTERVAL = 1.5

# 頭條區塊位置（佔整個畫面的比例，從範例圖片測量）
HEADLINE_X_START = 0.53
HEADLINE_X_END = 0.91
HEADLINE_Y_START = 0.38
HEADLINE_Y_END = 0.55

# 頭條顏色 HSV 閾值（任一命中即視為頭條）
# 黃色背景（黑字）
YELLOW_H_MIN = 10
YELLOW_H_MAX = 40
YELLOW_S_MIN = 50
YELLOW_V_MIN = 150

# 紅色背景（白字）— H 在 0~10 或 160~180
RED_H_MIN1 = 0
RED_H_MAX1 = 10
RED_H_MIN2 = 160
RED_H_MAX2 = 180
RED_S_MIN = 80
RED_V_MIN = 100

# 藍色背景（白字）
BLUE_H_MIN = 90
BLUE_H_MAX = 130
BLUE_S_MIN = 50
BLUE_V_MIN = 100

# 頭條判定：顏色像素佔裁切區塊的最小比例
MIN_HEADLINE_RATIO = 0.15

# 去重：SSIM 閾值
SSIM_THRESHOLD = 0.85  # > 此值視為相同圖片

# 去重：文字相似度閾值
TEXT_SIMILARITY_THRESHOLD = 0.8  # > 此值視為相同新聞

# LLM OCR
LLM_API_URL = "http://192.168.0.242:8081/v1/chat/completions"
LLM_MODEL = "gemma-4-26B-A4B-it-UD-Q4_K_M.gguf"
LLM_MAX_TOKENS = 1500
LLM_TIMEOUT = 300  # 秒
LLM_RESIZE_WIDTH = 512  # 送 OCR 前縮小圖片寬度

# 輸出路徑
OUTPUT_DIR = "output"
FRAMES_DIR = "output/frames"
HEADLINES_DIR = "output/headlines"
DB_PATH = "output/headlines.db"

# Telegram 通知
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
