"""可調參數設定"""

# YouTube 串流
STREAM_QUALITY = "720p"  # 串流畫質

# 取樣間隔（秒）
SAMPLE_INTERVAL = 1.5

# ROI：裁切右半畫面（比例）
ROI_X_START = 0.5   # 從畫面 50% 開始
ROI_X_END = 1.0     # 到畫面 100%
ROI_Y_START = 0.0
ROI_Y_END = 1.0

# HSV 黃色閾值
YELLOW_H_MIN = 10
YELLOW_H_MAX = 40
YELLOW_S_MIN = 50
YELLOW_S_MAX = 255
YELLOW_V_MIN = 150
YELLOW_V_MAX = 255

# 黃色區塊面積閾值（佔 ROI 面積的比例）
MIN_YELLOW_AREA_RATIO = 0.05  # 至少佔 ROI 的 5%

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
