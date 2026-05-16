## Why

自動監控 YouTube 東森財經新聞直播，當畫面出現黃色橫幅的重要訊息（獨家消息、最新消息等）時，自動截圖並 OCR 辨識文字內容。手動盯盤容易遺漏，自動化可完整記錄所有重要頭條，最終產出 HTML 方便回顧。

## What Changes

從零建立 Python CLI 工具：
- yt-dlp + OpenCV 擷取 YouTube 直播串流
- HSV 色彩偵測黃色頭條區塊（右半畫面）
- 圖像比對 + 文字歷史比對雙層去重，避免同一條新聞重複擷取（含隔段時間重播）
- 落地 LLM（192.168.0.242:8081）對黃色區塊進行多模態 OCR
- 存檔：全幀截圖 + 黃色區塊截圖 + OCR 文字 + 時間戳記
- 監控結束後產生 HTML 瀏覽頁面

## Capabilities

### New Capabilities
- 輸入 YouTube 直播 URL，自動開始監控
- 每 1-2 秒取樣一幀，掃描右半畫面偵測黃色大面積區塊
- 偵測到黃色區塊 → 裁切該區塊 → 圖像比對去重 → OCR
- 即時在 terminal 顯示辨識結果
- 存檔：全幀 PNG + 黃色區塊 PNG + SQLite（時間戳、OCR 文字、截圖路徑）
- 產生 HTML 頁面，可瀏覽搜尋所有擷取記錄

### Modified Capabilities
（無，全新專案）

## Impact

### 新增檔案
- `main.py` — 主程式入口 + CLI
- `stream.py` — YouTube 串流擷取（yt-dlp + OpenCV）
- `detector.py` — 黃色區塊偵測（HSV + 輪廓）
- `ocr_engine.py` — OCR 辨識封裝（EasyOCR）
- `storage.py` — 截圖存檔 + SQLite 操作
- `dedup.py` — 圖像比對去重
- `html_report.py` — 產生 HTML 瀏覽頁面
- `config.py` — 可調參數（HSV 閾值、取樣間隔、ROI 範圍等）
- `requirements.txt` — Python 依賴

### 外部依賴
- Python 3.10+
- yt-dlp、ffmpeg、opencv-python、scikit-image（SSIM）、requests（呼叫落地 LLM）
- 落地 LLM：192.168.0.242:8081

### 輸出
- `output/frames/` — 全幀截圖
- `output/headlines/` — 黃色區塊截圖
- `output/headlines.db` — SQLite 資料庫
- `output/report.html` — HTML 瀏覽頁面
