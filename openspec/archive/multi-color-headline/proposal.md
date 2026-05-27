## Why
目前只偵測黃色背景頭條，遺漏紅色和藍色頭條。

## What Changes
1. 改用固定區塊裁切（頭條位置固定）取代全 ROI 顏色掃描
2. 裁切後判斷區塊內是否有大面積黃/紅/藍色 → 有即為頭條
3. 先部署觀察幾天，再根據實際資料微調

## Capabilities
### Modified Capabilities
- `detector.py`：固定區塊裁切 + 多色判斷（黃/紅/藍）
- `config.py`：頭條區塊座標比例 + 三色 HSV 閾值

### Unchanged
- ROI 右半畫面裁切（保留但可能不再需要）
- OCR / 去重 / 報告 / 部署 / Telegram — 不變

## Impact
- 修改：`detector.py`、`config.py`、`main.py`（函式名稱）
