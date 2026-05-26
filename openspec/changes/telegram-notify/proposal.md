## Why
目前頭條擷取後只部署到 GitHub Pages，使用者需要主動開網頁才能看到最新頭條。
加入 Telegram 通知可以即時推送到手機，不用盯著網頁。

## What Changes
每次部署到 GitHub Pages 後，同時透過 Telegram Bot API 發送通知，包含：
- 最新擷取的頭條文字
- 頭條截圖（圖片）
- GitHub Pages 報告連結

## Capabilities
### New Capabilities
- 新增 `telegram_notify.py`：封裝 Telegram Bot API 發送訊息 + 圖片
- 部署成功後自動觸發 Telegram 通知

### Modified Capabilities
- `main.py`：在 `deploy_in_background()` 部署成功後呼叫 Telegram 通知
- `config.py`：新增 Telegram 相關設定（從環境變數讀取）

## Impact
- 新增檔案：`telegram_notify.py`
- 修改：`main.py`、`config.py`
- 環境變數：`TELEGRAM_BOT_TOKEN`、`TELEGRAM_CHAT_ID`
- Docker：docker run 需加 `-e TELEGRAM_BOT_TOKEN` `-e TELEGRAM_CHAT_ID`
