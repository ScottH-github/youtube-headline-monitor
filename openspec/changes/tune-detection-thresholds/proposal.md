## Why
多色偵測上線後，紅色/藍色閾值太寬鬆，股票報價表(暗紅)、廣告、主播名牌等大量誤觸發，
同時佔滿去重佇列導致真正頭條被漏抓。

## What Changes
1. 收緊紅色/藍色 HSV V_MIN，排除暗色背景
2. 提高顏色佔比門檻，排除小面積標籤
3. 加強 OCR 噪音過濾（股票報價、純數字、人名標籤）

## Capabilities
### Modified Capabilities
- `config.py`: 調整 RED_V_MIN、BLUE_V_MIN、MIN_HEADLINE_RATIO
- `html_report.py`: _is_noise() 加強過濾規則

## Impact
- `config.py` — 3 個參數
- `html_report.py` — 噪音過濾函式
