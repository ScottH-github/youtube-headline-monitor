## 1. 報告外部儲存 + 月份結構
- [x] 1.1 html_report.py：報告改為按月份資料夾輸出（`YYYYMM/YYYY-MM-DD.html`）
- [x] 1.2 html_report.py：調整圖片壓縮參數，確保單日報告 < 80MB
- [x] 1.3 deploy.py：產生主頁 index.html（月份連結清單，只顯示有資料的月份）
- [x] 1.4 deploy.py：產生月份子頁 index.html（該月每日報告連結）
- [ ] 1.5 Docker 改用 bind mount 掛載到 NAS 實體路徑
- [x] 1.6 Code Review：檢查目錄結構、路徑處理、HTML 產出正確性
  - Fixed: deploy.py 移除 unused import sys
  - OK: 月份結構 YYYYMM/YYYY-MM-DD.html 路徑正確
  - OK: 兩層 index 產生邏輯正確，back-link 相對路徑正確
  - OK: 圖片壓縮降至 max_width=480/quality=35

## 2. 交易日曆檢查（休市日 + 補班日 + 颱風假）
- [x] 2.1 新增 trading_calendar.py：讀取 holidays.json，判斷邏輯：補班日(開盤) > 休市日(休市) > 週六日(休市) > 颱風假(休市) > 正常開盤
- [x] 2.2 trading_calendar.py：呼叫停班停課 API 判斷颱風假（失敗時預設正常執行）
- [x] 2.3 建立 holidays.json（2026 年台股休市日 + 補班日清單）
- [x] 2.4 main.py：啟動時呼叫交易日曆檢查，非開盤日直接退出
- [x] 2.5 Code Review：檢查 API 錯誤處理、時區、邊界條件
  - OK: 優先順序正確：補班日 > 休市日 > 週末 > 颱風假 > 正常
  - OK: API timeout=10s，失敗 fallback 正常執行
  - OK: holidays.json 不存在時預設正常執行
  - OK: 測試 6 個邊界日期全部通過

## 3. NAS 排程調整
- [x] 3.1 整理新的 docker run 指令（bind mount + --rm）
- [x] 3.2 整理新的 NAS crontab 設定（每天排程，含週六日）
- [x] 3.3 文件更新：更新 MEMORY.md 中的部署流程與 docker run 指令
- [x] 3.4 Code Review：檢查排程邏輯、容器生命週期
  - OK: --rm 確保非交易日容器自動清除
  - OK: crontab 每天排程，交易日判斷由程式負責
  - OK: docker kill 在 13:35 停止，留 5 分鐘給報告產出

## 4. 端對端測試
- [x] 4.1 本機測試：產生報告 → 驗證月份結構 → 驗證 index 頁面
  - OK: 主頁正確列出月份（202605, 202604）含報告數量
  - OK: 月份頁正確列出每日報告，back-link 正確
  - OK: 最新報告連結指向正確檔案
- [ ] 4.2 NAS 測試：bind mount → docker run --rm → 報告產出 → GitHub Pages 部署
- [x] 4.3 測試休市日跳過邏輯 + 補班日正常執行邏輯
- [x] 4.4 測試颱風假 API 判斷（含 API 失敗 fallback）
- [ ] 4.5 Code Review：最終整合檢查
