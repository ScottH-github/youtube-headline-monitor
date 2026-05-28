## 1. 收緊偵測閾值
- [x] 1.1 `config.py`: RED_V_MIN 100→160
- [x] 1.2 `config.py`: BLUE_V_MIN 100→150
- [x] 1.3 `config.py`: MIN_HEADLINE_RATIO 0.15→0.25
- [x] 1.4 Code Review
  - OK: 閾值調整合理，黃色不變(V_MIN=150已夠高)

## 2. 加強 OCR 噪音過濾
- [x] 2.1 `html_report.py`: 加入股票報價格式、純數字比例、人名標籤、廣告產品過濾
- [x] 2.2 Code Review
  - OK: 用今天57筆驗證，股票報價/廣告/主播名牌/來賓標籤皆能正確過濾

## 3. 部署
- [x] 3.1 Build image 並上傳 NAS (method B)
