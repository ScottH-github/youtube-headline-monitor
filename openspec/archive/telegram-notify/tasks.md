## 1. Telegram 通知模組
- [x] 1.1 新增 `telegram_notify.py`：send_headline(text, image_path, report_url)
- [x] 1.2 使用 Telegram Bot API (urllib)，不額外裝套件
- [x] 1.3 環境變數未設定時靜默跳過（不影響現有功能）
- [x] 1.4 Code Review：檢查 API 錯誤處理、敏感資料、邊界條件
  - OK: 所有 exception 被 catch，不影響主程式
  - OK: token/chat_id 從環境變數讀取，無硬編碼
  - OK: 圖片不存在時 fallback 純文字訊息
  - OK: multipart/form-data 手動組裝正確

## 2. 整合到主程式
- [x] 2.1 config.py 新增 TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID
- [x] 2.2 main.py deploy_in_background() 部署成功後呼叫通知
- [x] 2.3 傳送最新一則頭條的文字 + 截圖 + 報告連結
- [x] 2.4 Code Review：檢查執行緒安全、通知失敗不影響主流程
  - OK: last_headline 寫入在主執行緒、讀取在背景執行緒，無 race condition
  - OK: send_headline 在 try/except 內，失敗不影響部署
  - OK: storage.get_headline_path() 查詢正確

## 3. 部署更新
- [x] 3.1 docker run 指令加入 TELEGRAM 環境變數
- [x] 3.2 NAS crontab 更新完成，crond 已重啟
- [x] 3.3 Code Review：檢查環境變數傳遞、NAS crontab 更新
  - OK: crontab 包含 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID
  - OK: 新容器已啟動，含 Telegram 環境變數
  - OK: NAS 上直接 build image（Dockerfile 修正 COPY *.py ./）
