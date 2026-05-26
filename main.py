"""主程式：YouTube 直播新聞頭條擷取"""

import argparse
import os
import time
import signal
import sys
import threading
from datetime import datetime

# 抑制 ffmpeg/OpenCV 的 TLS 錯誤訊息
os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "-8"

import cv2
import config
from stream import StreamReader
from detector import crop_roi, detect_yellow_region
from dedup import Deduplicator
from ocr_engine import ocr_headline
from storage import Storage
from html_report import generate_report
from deploy import deploy_report
from telegram_notify import send_headline
from trading_calendar import is_trading_day


def main():
    parser = argparse.ArgumentParser(description="YouTube 直播新聞頭條擷取")
    parser.add_argument("url", help="YouTube 直播 URL")
    parser.add_argument("--interval", type=float, default=config.SAMPLE_INTERVAL, help="取樣間隔（秒）")
    parser.add_argument("--output", default=config.OUTPUT_DIR, help="輸出目錄")
    parser.add_argument("--preview", action="store_true", help="顯示即時預覽視窗")
    parser.add_argument("--debug", action="store_true", help="每次偵測都存 debug 幀到 output/debug/")
    parser.add_argument("--skip-calendar", action="store_true", help="跳過交易日曆檢查")
    args = parser.parse_args()

    # 交易日曆檢查
    if not args.skip_calendar:
        is_open, reason = is_trading_day()
        if not is_open:
            print(f"[交易日曆] 今天非交易日: {reason}，跳過執行")
            sys.exit(0)
        print(f"[交易日曆] {reason}")

    config.OUTPUT_DIR = args.output
    config.FRAMES_DIR = f"{args.output}/frames"
    config.HEADLINES_DIR = f"{args.output}/headlines"
    config.DB_PATH = f"{args.output}/headlines.db"

    # 每次啟動清空前次資料，確保每日報告獨立
    _clean_output(args.output)

    print("=" * 60)
    print("  YouTube 直播新聞頭條擷取")
    print("=" * 60)
    print(f"  URL: {args.url}")
    print(f"  取樣間隔: {args.interval} 秒")
    print(f"  輸出目錄: {args.output}")
    print("=" * 60)
    print(f"  即時預覽: {'開啟' if args.preview else '關閉'}")
    print("=" * 60)
    print("  按 Ctrl+C 停止監控並產生 HTML 報告")
    if args.preview:
        print("  預覽視窗中按 q 也可停止")
    print("=" * 60)

    reader = StreamReader(args.url)
    dedup = Deduplicator()
    store = Storage()

    running = True
    deploy_lock = threading.Lock()
    deploy_thread = None
    last_headline = None  # (ocr_text, headline_path)

    def deploy_in_background():
        """背景執行緒：產生報告並部署"""
        nonlocal last_headline
        if not deploy_lock.acquire(blocking=False):
            print("[部署] 上一次部署尚未完成，跳過")
            return
        try:
            report_path = f"{args.output}/report.html"
            generate_report(report_path)
            deploy_report(report_path)
            # Telegram 通知
            if last_headline:
                text, img_path = last_headline
                today = datetime.now()
                month_dir = today.strftime("%Y%m")
                day_file = today.strftime("%Y-%m-%d") + ".html"
                report_url = f"https://scotth-github.github.io/youtube-headline-monitor/{month_dir}/{day_file}"
                send_headline(text, img_path, report_url)
        except Exception as e:
            print(f"[部署] 背景部署失敗: {e}")
        finally:
            deploy_lock.release()

    def on_exit(sig, frame):
        nonlocal running
        running = False
        print("\n[主程式] 收到停止信號，準備結束...")

    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    debug_dir = f"{args.output}/debug"
    if args.debug:
        os.makedirs(debug_dir, exist_ok=True)

    count = 0
    last_detect_time = 0
    debug_count = 0

    while running:
        frame = reader.read_frame()
        if frame is None:
            print("[主程式] 無法讀取幀，等待重連...")
            time.sleep(5)
            continue

        now = time.time()
        do_detect = (now - last_detect_time) >= args.interval

        headline_crop = None
        bbox = None

        if do_detect:
            last_detect_time = now
            roi = crop_roi(frame)
            headline_crop, bbox = detect_yellow_region(roi)

            # debug 模式：每 30 秒存一張 debug 幀
            if args.debug:
                debug_count += 1
                if debug_count % 20 == 1:  # 每 20 次偵測（約 30 秒）存一張
                    ts = datetime.now().strftime("%H%M%S")
                    cv2.imwrite(f"{debug_dir}/debug_{ts}.png", frame)
                    cv2.imwrite(f"{debug_dir}/debug_{ts}_roi.png", roi)
                    detected = "YES" if headline_crop is not None else "NO"
                    print(f"[debug] 存 debug 幀 #{debug_count} detected={detected}")

        # 預覽視窗
        if args.preview:
            display = frame.copy()
            h, w = frame.shape[:2]
            roi_x1 = int(w * config.ROI_X_START)
            cv2.rectangle(display, (roi_x1, 0), (w, h), (0, 255, 0), 1)

            if headline_crop is not None:
                bx, by, bw, bh = bbox
                cv2.rectangle(display, (roi_x1 + bx, by), (roi_x1 + bx + bw, by + bh), (0, 255, 255), 2)

            status = "HEADLINE DETECTED" if headline_crop is not None else "monitoring..."
            cv2.putText(display, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (0, 255, 255) if headline_crop is not None else (200, 200, 200), 2)
            cv2.putText(display, f"saved: {count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

            cv2.imshow("YouTube Headline Monitor", display)
            key = cv2.waitKey(30) & 0xFF
            if key == ord("q"):
                running = False
                continue

        if not do_detect or headline_crop is None:
            if not args.preview:
                time.sleep(0.03)
            continue

        if dedup.is_same_image(headline_crop):
            continue

        print(f"\n[偵測] {datetime.now().strftime('%H:%M:%S')} 發現黃色頭條，進行 OCR...")

        ocr_text = ocr_headline(headline_crop)
        if not ocr_text:
            continue

        history = store.get_all_texts()
        if dedup.is_duplicate_text(ocr_text, history):
            print(f"[去重] 文字重複，跳過: {ocr_text[:40]}...")
            continue

        record_id = store.save(frame, headline_crop, ocr_text)
        count += 1
        print(f"[儲存] #{record_id} | {ocr_text}")
        last_headline = (ocr_text, store.get_headline_path(record_id))

        # 即時部署：背景執行緒產生報告並推送
        deploy_thread = threading.Thread(target=deploy_in_background, daemon=True)
        deploy_thread.start()

    # 結束：等待背景部署完成 + 最終部署
    if args.preview:
        cv2.destroyAllWindows()
    reader.release()

    # 等待進行中的背景部署完成
    if deploy_thread and deploy_thread.is_alive():
        print("[主程式] 等待背景部署完成...")
        deploy_thread.join(timeout=120)

    # 最終部署（確保包含所有資料）
    report_path = f"{args.output}/report.html"
    generate_report(report_path)
    store.close()
    print(f"\n[完成] 共擷取 {count} 則頭條")
    print(f"[完成] HTML 報告: {report_path}")

    if count > 0:
        print("[完成] 最終部署到 GitHub Pages...")
        deploy_report(report_path)
    else:
        print("[完成] 無新頭條，跳過部署")


def _clean_output(output_dir: str):
    """清空 output 目錄，確保每日報告獨立"""
    import shutil
    for sub in ["frames", "headlines"]:
        sub_dir = os.path.join(output_dir, sub)
        if os.path.exists(sub_dir):
            shutil.rmtree(sub_dir)
    db_path = os.path.join(output_dir, "headlines.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    report_path = os.path.join(output_dir, "report.html")
    if os.path.exists(report_path):
        os.remove(report_path)
    print("[主程式] 已清空前次資料")


if __name__ == "__main__":
    main()
