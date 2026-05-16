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


def generate_report(output_path: str = "output/report.html"):
    """從 SQLite 產生 HTML 報告"""
    store = Storage()
    records = store.get_all_records()
    store.close()

    noise_keywords = [
        "沒有文字", "no text", "諮詢專線", "0800", "7-ELEVEN", "7-eleven",
        "統一布丁", "康利舒胃", "綜合報導", "主播",
    ]
    min_text_len = 10

    rows_html = ""
    for r in records:
        frame_b64 = image_to_base64(r["frame_path"], max_width=480, quality=35)
        headline_b64 = image_to_base64(r["headline_path"], max_width=400, quality=40)
        text = r['ocr_text']
        is_noise = (
            len(text.strip()) < min_text_len
            or any(kw in text for kw in noise_keywords)
            or (not any(c.isalpha() or '\u4e00' <= c <= '\u9fff' for c in text))
        )
        noise_cls = ' class="noise"' if is_noise else ''
        rows_html += f"""
        <tr{noise_cls}>
            <td>{r['id']}</td>
            <td class="ts">{r['timestamp']}</td>
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
    tr.noise.hidden {{ display: none; }}
</style>
</head>
<body>
<div class="back-link"><a href="../index.html">&larr; 回主頁</a> | <a href="index.html">本月報告</a></div>
<h1>新聞頭條擷取報告</h1>
<p class="stats" id="stats">共 {len(records)} 則頭條</p>
<div class="filter-bar">
    <label><input type="checkbox" id="filterNoise" onchange="toggleNoise(this.checked)"> 過濾無效資料（廣告、太短、無文字）</label>
</div>
<input type="text" class="search-box" placeholder="搜尋文字..." oninput="filterRows(this.value)">
<table>
<thead><tr><th>#</th><th>時間</th><th>OCR 文字</th><th>頭條截圖</th><th>全幀截圖</th></tr></thead>
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
        r.classList.toggle('hidden', hide);
    }});
    updateCount();
}}
function updateCount() {{
    const total = document.querySelectorAll('#tbody tr').length;
    const visible = document.querySelectorAll('#tbody tr:not([style*="display: none"]):not(.hidden)').length;
    const el = document.getElementById('stats');
    el.textContent = visible < total ? '顯示 ' + visible + ' / ' + total + ' 則' : '共 ' + total + ' 則頭條';
}}
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
