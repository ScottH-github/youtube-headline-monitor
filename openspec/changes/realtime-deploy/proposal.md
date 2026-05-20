## Why
目前報告只在容器停止時（13:35）一次性產生並部署，使用者無法在盤中即時查看已擷取的頭條。

## What Changes
每次偵測到新頭條並儲存後，立即更新 HTML 報告並部署到 GitHub Pages。

## Capabilities
### Modified Capabilities
- main.py：每次儲存新頭條後觸發報告產生 + 部署
- 部署使用背景執行緒，不阻塞偵測循環
- 同一時間只允許一個部署任務，避免 git 衝突

## Impact
- main.py：主迴圈新增即時部署邏輯
- deploy.py / html_report.py：無需修改，直接複用
