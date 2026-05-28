"""HTML 報告產生模組"""

import os
import base64
import io
from storage import Storage
from PIL import Image


def image_to_base64(path: str, max_width: int = 800, quality: int = 60) -> str:
    """將圖片壓縮後轉為 base64 data URI（JPEG）"""
    if not os.path.exists(path):
        return ""
    try:
        img = Image.open(path)
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"
    except Exception:
        return ""


def _is_noise(text: str, min_len: int = 10) -> bool:
    """判斷 OCR 文字是否為雜訊（非新聞頭條）"""
    import re
    text = text.strip()

    # 太短
    if len(text) < min_len:
        return True

    # 無中文或英文字母（純數字/符號）
    if not any(c.isalpha() or '\u4e00' <= c <= '\u9fff' for c in text):
        return True

    # JSON / 座標
    if text.startswith("{") or text.startswith("[") or '"point"' in text:
        return True

    # LLM 拒絕/解釋訊息
    llm_noise = [
        "由於", "抱歉", "無法辨識", "解析度", "藝術化", "模糊",
        "I cannot", "I can't", "sorry", "圖片中沒有", "看不清",
        "沒有文字", "no text", "不包含文字",
    ]
    if any(p in text for p in llm_noise):
        return True

    # 股票報價格式（股票代號+數字、純漲跌幅）
    if re.match(r'^[\w\s]*\d{3,5}\s*[▲▼+-]?\s*\d', text):
        return True
    if re.match(r'^[▲▼+-]?\d+\.?\d*%?$', text):
        return True

    # 數字佔比過高（報價、統計數據）
    digits = re.findall(r'\d', text)
    if len(text) > 3 and len(digits) / len(text) > 0.5:
        return True

    # 廣告 / 贊助 / 節目宣傳
    ad_patterns = [
        "贊助播出", "贊助", "廣告", "諮詢專線", "0800", "免費專線",
        "7-ELEVEN", "7-eleven", "統一布丁", "康利舒胃",
        "本節目由", "感謝收看", "精彩內容",
        "萃滴精", "萃精", "葉黃素", "花萃", "潤膚", "轉大人",
        "LINE ID", "line.me",
    ]
    if any(p in text for p in ad_patterns):
        return True

    # 頻道 / 節目宣傳 / 人名標籤
    promo_patterns = [
        "頻道", "YouTube", "youtube", "訂閱", "按讚", "分享",
        "小姐不熙娣", "綜合報導", "主播", "記者.*報導",
        "連線來賓", "分析師",
    ]
    if any(re.search(p, text) for p in promo_patterns):
        return True

    # 非新聞格式：沒有中文字超過 4 個字（頭條至少幾個中文字）
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    if len(chinese_chars) < 4:
        return True

    return False


def generate_report(output_path: str = "output/report.html"):
    """從 SQLite 產生 HTML 報告"""
    store = Storage()
    records = store.get_all_records()
    store.close()

    min_text_len = 10

    color_labels = {
        "yellow": ("黃", "#f0c040", "#000"),
        "red": ("紅", "#e04040", "#fff"),
        "blue": ("藍", "#4080e0", "#fff"),
    }

    rows_html = ""
    for r in records:
        frame_b64 = image_to_base64(r["frame_path"], max_width=480, quality=35)
        headline_b64 = image_to_base64(r["headline_path"], max_width=400, quality=40)
        text = r['ocr_text']
        is_noise = _is_noise(text, min_text_len)
        noise_cls = ' class="noise"' if is_noise else ''
        color = r.get("color", "")
        if color in color_labels:
            label, bg, fg = color_labels[color]
            color_html = f'<span class="color-tag" style="background:{bg};color:{fg}">{label}</span>'
        else:
            color_html = ""
        rows_html += f"""
        <tr{noise_cls}>
            <td>{r['id']}</td>
            <td class="ts">{r['timestamp']}</td>
            <td>{color_html}</td>
            <td class="ocr-text">{text}</td>
            <td><img src="{headline_b64}" class="headline-img" onclick="showModal(this.src)"></td>
            <td><img src="{frame_b64}" class="frame-img" onclick="showModal(this.src)"></td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<title>新聞頭條擷取報告</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, "Microsoft JhengHei", sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }}
    h1 {{ text-align: center; margin-bottom: 10px; color: #f0c040; }}
    .stats {{ text-align: center; margin-bottom: 20px; color: #aaa; }}
    .search-box {{ display: block; margin: 0 auto 20px; padding: 10px 16px; width: 400px; max-width: 90%;
        border: 1px solid #444; border-radius: 8px; background: #16213e; color: #eee; font-size: 16px; }}
    .search-box::placeholder {{ color: #666; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th {{ background: #16213e; padding: 12px 8px; text-align: left; position: sticky; top: 0; }}
    td {{ padding: 10px 8px; border-bottom: 1px solid #2a2a4a; vertical-align: middle; }}
    tr:hover {{ background: #16213e; }}
    .ts {{ white-space: nowrap; font-size: 14px; color: #aaa; }}
    .ocr-text {{ font-size: 16px; max-width: 400px; line-height: 1.5; }}
    .headline-img {{ height: 60px; cursor: pointer; border-radius: 4px; }}
    .frame-img {{ height: 80px; cursor: pointer; border-radius: 4px; }}
    .color-tag {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 13px; font-weight: bold; }}
    .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.9); justify-content: center; align-items: center; z-index: 1000; cursor: pointer; }}
    .modal img {{ max-width: 90%; max-height: 90%; }}
    .modal.active {{ display: flex; }}
    .back-link {{ display: block; text-align: center; margin-bottom: 15px; }}
    .back-link a {{ color: #6cb4ee; text-decoration: none; font-size: 16px; }}
    .back-link a:hover {{ text-decoration: underline; }}
    .filter-bar {{ text-align: center; margin-bottom: 15px; }}
    .filter-bar label {{ cursor: pointer; color: #aaa; font-size: 15px; }}
    .filter-bar input {{ margin-right: 6px; }}
    tr.noise {{ display: none; }}
    tr.noise.show {{ display: table-row; }}
</style>
</head>
<body>
<div class="back-link"><a href="../index.html">&larr; 回主頁</a> | <a href="index.html">本月報告</a></div>
<h1>新聞頭條擷取報告</h1>
<p class="stats" id="stats">共 {len(records)} 則頭條</p>
<div class="filter-bar">
    <label><input type="checkbox" id="filterNoise" checked onchange="toggleNoise(this.checked)"> 過濾無效資料（廣告、太短、無文字）</label>
</div>
<input type="text" class="search-box" placeholder="搜尋文字..." oninput="filterRows(this.value)">
<table>
<thead><tr><th>#</th><th>時間</th><th>色</th><th>OCR 文字</th><th>頭條截圖</th><th>全幀截圖</th></tr></thead>
<tbody id="tbody">{rows_html}
</tbody>
</table>
<div class="modal" id="modal" onclick="this.classList.remove('active')">
    <img id="modal-img" src="">
</div>
<script>
function filterRows(q) {{
    const rows = document.querySelectorAll('#tbody tr');
    q = q.toLowerCase();
    rows.forEach(r => {{
        const text = r.querySelector('.ocr-text')?.textContent.toLowerCase() || '';
        r.style.display = text.includes(q) ? '' : 'none';
    }});
    updateCount();
}}
function toggleNoise(hide) {{
    document.querySelectorAll('tr.noise').forEach(r => {{
        r.classList.toggle('show', !hide);
    }});
    updateCount();
}}
function updateCount() {{
    const rows = document.querySelectorAll('#tbody tr');
    const total = rows.length;
    let visible = 0;
    rows.forEach(r => {{ if (r.offsetParent !== null || r.style.display === 'table-row') visible++; }});
    const el = document.getElementById('stats');
    el.textContent = visible < total ? '顯示 ' + visible + ' / ' + total + ' 則' : '共 ' + total + ' 則頭條';
}}
document.addEventListener('DOMContentLoaded', updateCount);
function showModal(src) {{
    document.getElementById('modal-img').src = src;
    document.getElementById('modal').classList.add('active');
}}
</script>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[報告] HTML 已產生: {output_path}")


if __name__ == "__main__":
    generate_report()
