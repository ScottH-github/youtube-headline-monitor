## 1. 專案初始化
- [x] 1.1 建立 Python 專案結構（main.py 及各模組）
- [x] 1.2 建立 requirements.txt
- [x] 1.3 建立 config.py（HSV 閾值、ROI、取樣間隔等可調參數）
- [x] 1.4 Code Review：檢查專案結構與依賴完整性
  - OK: 所有模組（stream, detector, dedup, ocr_engine, storage, html_report, main）已建立
  - OK: requirements.txt 包含所有必要依賴
  - OK: config.py 參數可調，命名清晰

## 2. YouTube 串流擷取
- [x] 2.1 stream.py：用 yt-dlp 取得直播串流 URL
- [x] 2.2 stream.py：用 OpenCV VideoCapture 讀取串流幀
- [x] 2.3 stream.py：斷線自動重連機制
- [x] 2.4 Code Review：檢查串流擷取穩定性與錯誤處理
  - OK: 重連最多 3 次，間隔遞增（5/10/15 秒）
  - OK: release() 正確釋放資源

## 3. 黃色區塊偵測
- [x] 3.1 detector.py：裁切右半畫面
- [x] 3.2 detector.py：HSV 黃色範圍過濾 + 輪廓偵測 + 面積過濾
- [x] 3.3 detector.py：回傳黃色區塊的邊界框座標與裁切圖
- [x] 3.4 用提供的三張截圖測試偵測邏輯，調整閾值
- [x] 3.5 Code Review：檢查偵測準確性與邊界條件
  - OK: 三張截圖全部正確偵測到黃色區塊 (bbox=(0, 425, 1020, 150))
  - OK: 形態學操作去雜訊、邊界框 padding 防裁切

## 4. 去重（圖像 + 文字雙層）
- [x] 4.1 dedup.py：SSIM 圖像相似度比對（連續幀去重）
- [x] 4.2 dedup.py：文字歷史比對（跟 SQLite 所有記錄比，>80% 相似視為重複，防重播）
- [x] 4.3 Code Review：檢查去重邏輯正確性
  - OK: SSIM 統一 resize 到 320x80 再比對
  - OK: SequenceMatcher 文字相似度比對

## 5. OCR 辨識（落地 LLM）
- [x] 5.1 ocr_engine.py：確認落地 LLM API 格式（192.168.0.242:8081）
- [x] 5.2 ocr_engine.py：將黃色區塊截圖 base64 編碼送至 LLM 進行多模態辨識
- [x] 5.3 ocr_engine.py：解析 LLM 回應，提取 OCR 文字
- [x] 5.4 用提供的三張截圖測試 OCR 準確度
- [x] 5.5 Code Review：檢查 OCR 準確度與效能
  - OK: 圖片先 resize+JPEG 壓縮再送出，減少傳輸量
  - OK: max_tokens=1500（thinking 約佔 700 tokens）
  - OK: timeout=300 秒，足夠推理
  - Fixed: 原 max_tokens=500 不夠，已調至 1500

## 6. 存檔
- [x] 6.1 storage.py：建立 SQLite schema（id, timestamp, ocr_text, frame_path, headline_path）
- [x] 6.2 storage.py：存全幀截圖到 output/frames/
- [x] 6.3 storage.py：存黃色區塊截圖到 output/headlines/
- [x] 6.4 Code Review：檢查存檔邏輯與路徑處理
  - OK: 自動建立目錄、時間戳命名避免衝突
  - OK: get_all_texts() 供去重、get_all_records() 供 HTML

## 7. 主程式整合
- [x] 7.1 main.py：串接所有模組，完成主迴圈（取幀→偵測→去重→OCR→存檔）
- [x] 7.2 main.py：terminal 即時顯示偵測結果
- [x] 7.3 main.py：CLI 參數（YouTube URL、輸出目錄等）
- [x] 7.4 Code Review：檢查整合邏輯、錯誤處理、資源釋放
  - OK: SIGINT/SIGTERM 優雅退出 + 自動產生 HTML
  - OK: 資源正確釋放（reader.release, store.close）

## 8. HTML 報告
- [x] 8.1 html_report.py：從 SQLite 讀取所有記錄
- [x] 8.2 html_report.py：產生 HTML 頁面（時間、文字、全幀截圖、區塊截圖）
- [x] 8.3 html_report.py：搜尋功能
- [x] 8.4 Code Review：檢查 HTML 輸出正確性
  - OK: 圖片 base64 內嵌，HTML 單檔可攜帶
  - OK: 搜尋即時過濾、圖片點擊放大

## 9. 端對端測試
- [x] 9.1 用實際直播 URL 測試完整流程
- [x] 9.2 驗證去重、存檔、HTML 產出
- [x] 9.3 Code Review：最終檢查所有功能整合
  - Fixed: 增加寬度過濾（>70% ROI 寬度）和位置過濾（ROI 下半部），消除小面積黃色文字誤判
  - OK: 串流連線正常（1280x720）
  - OK: SSIM 去重正常（60 幀只觸發 1 次偵測）
  - OK: 三張樣本圖全部正確偵測，非目標畫面正確過濾
