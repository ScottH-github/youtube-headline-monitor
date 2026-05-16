## Why

1. 報告 HTML 內嵌 base64 圖片導致單檔超過 100MB，無法推上 GitHub Pages
2. 所有產出檔案存在 Docker named volume 內，不方便直接存取與管理
3. 排程邏輯寫在 NAS crontab 但容器用 `docker run` 長駐，啟停不夠乾淨
4. 遇到國定假日、颱風假仍會啟動容器，浪費資源且產出空報告

## What Changes

### A. 報告外部儲存 + 月份結構
- Docker 改用 bind mount 掛載到 NAS 實體路徑
- 報告依月份分資料夾存放（`deploy/202605/2026-05-15.html`）
- 主頁 `index.html` 動態產生月份連結清單，每月子頁列出該月每日報告
- 圖片壓縮參數調低，確保單日報告不超過 GitHub 100MB 限制

### B. 排程改到 NAS crontab
- crontab 改為每天排程（含週六日），開盤判斷交由程式處理
- 用 `docker run --rm` 執行，跑完自動移除容器
- 用 `docker kill` 在收盤後停止
- 不再使用長駐容器 + restart policy

### C. 交易日曆過濾
- 外部 `holidays.json` 記錄每年休市日與補班日（每年底更新一次）
- 補班日（週六）視為開盤日，正常執行
- 容器啟動時檢查，非交易日直接退出
- JSON 放在 bind mount 路徑，不用重 build image 即可更新
- 判斷優先順序：補班日(開盤) > 休市日(休市) > 週六日(休市) > 颱風假(休市) > 正常開盤

### D. 颱風假即時檢查
- 容器啟動時呼叫行政院人事行政總處停班停課 API
- 檢查台北市當日是否停班，是則退出
- API 連線失敗時預設正常執行（寧可多跑，不漏抓）

## Capabilities

### New Capabilities
- 月份報告結構：主頁 → 月份頁 → 每日報告
- 休市日自動跳過執行
- 補班日（週六開盤）自動執行
- 颱風假自動跳過執行
- 報告檔案可直接在 NAS 檔案系統存取

### Modified Capabilities
- HTML 報告產生邏輯（月份結構 + 壓縮優化）
- 部署邏輯（配合新目錄結構）
- 容器啟動流程（加入開盤日檢查）
- Docker 運行方式（bind mount 取代 named volume，`--rm` 取代長駐）

## Impact

### 檔案變更
- `html_report.py` — 報告改為月份結構、壓縮優化
- `deploy.py` — 配合新目錄結構產生 index
- `main.py` — 啟動時加入開盤日檢查
- 新增 `trading_calendar.py` — 休市日 + 颱風假判斷
- 新增 `holidays.json` — 休市日 + 補班日清單（bind mount 外部）
- `Dockerfile` — 可能需微調（不影響 ENTRYPOINT）
- NAS `/etc/crontab` — 改用 `docker run --rm` + `docker kill`

### 外部依賴
- 行政院人事行政總處停班停課 API
- NAS 實體路徑 bind mount
