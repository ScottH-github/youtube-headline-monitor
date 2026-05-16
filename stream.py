"""YouTube 串流擷取模組"""

import subprocess
import cv2
import time
import config


def get_stream_url(youtube_url: str) -> str:
    """用 yt-dlp 取得直播串流的實際 URL"""
    cmd = [
        "yt-dlp",
        "-f", f"best[height<={config.STREAM_QUALITY.replace('p', '')}]",
        "-g",
        youtube_url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp 失敗: {result.stderr.strip()}")
    return result.stdout.strip()


class StreamReader:
    def __init__(self, youtube_url: str):
        self.youtube_url = youtube_url
        self.cap = None
        self._connect()

    def _connect(self):
        """建立或重新建立串流連線"""
        if self.cap is not None:
            self.cap.release()
        print(f"[串流] 取得串流 URL...")
        stream_url = get_stream_url(self.youtube_url)
        print(f"[串流] 連線中...")
        self.cap = cv2.VideoCapture(stream_url)
        if not self.cap.isOpened():
            raise RuntimeError("無法開啟串流")
        print(f"[串流] 連線成功")

    def read_frame(self):
        """讀取一幀，失敗時自動重連（最多重試 3 次）"""
        for attempt in range(3):
            if self.cap is None or not self.cap.isOpened():
                self._reconnect(attempt)
                continue

            ret, frame = self.cap.read()
            if ret and frame is not None:
                return frame

            self._reconnect(attempt)

        return None

    def _reconnect(self, attempt: int):
        """重連邏輯"""
        wait = (attempt + 1) * 5
        print(f"[串流] 讀取失敗，{wait} 秒後重連 (第 {attempt + 1} 次)...")
        time.sleep(wait)
        try:
            self._connect()
        except Exception as e:
            print(f"[串流] 重連失敗: {e}")

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
