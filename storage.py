"""存檔模組：SQLite + 截圖檔案"""

import os
import sqlite3
import cv2
import numpy as np
from datetime import datetime
import config


class Storage:
    def __init__(self):
        os.makedirs(config.FRAMES_DIR, exist_ok=True)
        os.makedirs(config.HEADLINES_DIR, exist_ok=True)
        self.conn = sqlite3.connect(config.DB_PATH)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS headlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                ocr_text TEXT NOT NULL,
                frame_path TEXT NOT NULL,
                headline_path TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def save(self, frame: np.ndarray, headline_crop: np.ndarray, ocr_text: str) -> int:
        """存全幀截圖 + 黃色區塊截圖 + OCR 文字"""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        frame_path = os.path.join(config.FRAMES_DIR, f"frame_{ts}.png")
        headline_path = os.path.join(config.HEADLINES_DIR, f"headline_{ts}.png")

        cv2.imwrite(frame_path, frame)
        cv2.imwrite(headline_path, headline_crop)

        cursor = self.conn.execute(
            "INSERT INTO headlines (timestamp, ocr_text, frame_path, headline_path) VALUES (?, ?, ?, ?)",
            (datetime.now().isoformat(), ocr_text, frame_path, headline_path),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_all_texts(self) -> list[str]:
        """取得所有歷史 OCR 文字（供去重比對）"""
        rows = self.conn.execute("SELECT ocr_text FROM headlines").fetchall()
        return [r[0] for r in rows]

    def get_all_records(self) -> list[dict]:
        """取得所有記錄（供 HTML 報告）"""
        rows = self.conn.execute(
            "SELECT id, timestamp, ocr_text, frame_path, headline_path FROM headlines ORDER BY id DESC"
        ).fetchall()
        return [
            {
                "id": r[0],
                "timestamp": r[1],
                "ocr_text": r[2],
                "frame_path": r[3],
                "headline_path": r[4],
            }
            for r in rows
        ]

    def close(self):
        self.conn.close()
