## 1. DB schema + storage
- [x] 1.1 `storage.py`: CREATE TABLE 加 `color TEXT` 欄位
- [x] 1.2 `storage.py`: `save()` 加 `color` 參數並寫入 DB
- [x] 1.3 `storage.py`: `get_all_records()` 回傳 color 欄位
- [x] 1.4 Code Review：檢查 schema 變更與向後相容
  - OK: DEFAULT '' 確保向後相容，save() 有預設值

## 2. 主程式串接
- [x] 2.1 `main.py`: 傳 `headline_color` 給 `store.save()`
- [x] 2.2 Code Review：檢查傳參正確性
  - OK: headline_color 來自 detect_headline()，型別為 str

## 3. HTML 報告顯示
- [x] 3.1 `html_report.py`: 表格加「顏色」欄，顯示色塊標籤
- [x] 3.2 Code Review：檢查報告顯示正確性
  - OK: r.get("color", "") 安全處理舊資料，色塊樣式正確

## 4. 部署
- [x] 4.1 Build image 並上傳 NAS (method B: NAS 直接 build)
