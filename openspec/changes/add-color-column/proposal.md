## Why
多色頭條偵測已上線，但 DB 未儲存偵測到的顏色，無法回溯分析各色頭條的比例與準確度，不利於後續調參。

## What Changes
在 headlines DB 加 `color` 欄位，儲存偵測顏色（yellow/red/blue），並在 HTML 報告中顯示。

## Capabilities
### New Capabilities
- DB 記錄每則頭條的偵測顏色
- HTML 報告顯示顏色標籤（色塊）

### Modified Capabilities
- `storage.py`: save() 接受 color 參數，schema 加 color 欄位
- `main.py`: 傳 headline_color 給 store.save()
- `html_report.py`: 顯示顏色標籤

## Impact
- `storage.py` — DB schema + save/get_all_records
- `main.py` — 一行改動
- `html_report.py` — 表格加一欄
