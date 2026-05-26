"""Telegram 通知模組 - 發送頭條截圖到 Telegram"""

import os
import json
import uuid
import urllib.request
import urllib.error


def _build_caption(text: str, report_url: str) -> str:
    """組合 caption HTML"""
    return f'<b>{text}</b>\n\n<a href="{report_url}">完整報告</a>'


def _send_message(token: str, chat_id: str, caption: str) -> None:
    """純文字訊息 fallback"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": caption,
        "parse_mode": "HTML",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=30)


def _send_photo(token: str, chat_id: str, image_path: str, caption: str) -> None:
    """multipart/form-data 上傳圖片"""
    boundary = uuid.uuid4().hex
    crlf = b"\r\n"

    body = b""
    # chat_id field
    body += f"--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
    body += chat_id.encode() + crlf
    # parse_mode field
    body += f"--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="parse_mode"\r\n\r\n'
    body += b"HTML" + crlf
    # caption field
    body += f"--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="caption"\r\n\r\n'
    body += caption.encode("utf-8") + crlf
    # photo file field
    filename = os.path.basename(image_path)
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="photo"; filename="{filename}"\r\n'.encode()
    body += b"Content-Type: image/jpeg\r\n\r\n"
    with open(image_path, "rb") as f:
        body += f.read()
    body += crlf
    # closing boundary
    body += f"--{boundary}--\r\n".encode()

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    urllib.request.urlopen(req, timeout=30)


def send_headline(text: str, image_path: str, report_url: str) -> None:
    """發送頭條通知到 Telegram。

    Args:
        text: 頭條文字
        image_path: 截圖檔案路徑
        report_url: 完整報告連結
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    if not token or not chat_id:
        print("[Telegram] TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID 未設定，跳過通知")
        return

    try:
        caption = _build_caption(text, report_url)
        use_photo = image_path and os.path.isfile(image_path) and os.path.getsize(image_path) > 0

        if use_photo:
            _send_photo(token, chat_id, image_path, caption)
        else:
            _send_message(token, chat_id, caption)

        print("[Telegram] 通知已發送")
    except Exception as e:
        print(f"[Telegram] 發送失敗: {e}")
