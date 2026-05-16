#!/bin/bash
# 每日排程腳本：啟動監控 → 到 13:30 自動停止 → 產生報告 → 部署

PROJECT_DIR="$HOME/Documents/vibecoding/youtube-cutScreen"
YOUTUBE_URL="https://www.youtube.com/live/AEBeWMM1atA?si=2FK3jfOGq9CpOa5C"
LOG_FILE="$PROJECT_DIR/output/monitor_$(date +%Y%m%d).log"

cd "$PROJECT_DIR"
source venv/bin/activate

echo "$(date) [排程] 開始監控" >> "$LOG_FILE"

# 計算到 13:30 還有多少秒
END_HOUR=13
END_MIN=30
NOW_SEC=$(date +%s)
END_SEC=$(date -j -f "%Y%m%d%H%M" "$(date +%Y%m%d)${END_HOUR}${END_MIN}" +%s 2>/dev/null)

if [ "$NOW_SEC" -ge "$END_SEC" ]; then
    echo "$(date) [排程] 已過 13:30，跳過" >> "$LOG_FILE"
    exit 0
fi

DURATION=$((END_SEC - NOW_SEC))
echo "$(date) [排程] 將執行 $((DURATION / 60)) 分鐘" >> "$LOG_FILE"

# 啟動監控（背景）
export PYTHONUNBUFFERED=1
python3 main.py "$YOUTUBE_URL" >> "$LOG_FILE" 2>&1 &
PID=$!

# 等待指定時間後發送 SIGINT（讓程式正常結束並產生報告+部署）
sleep "$DURATION"
kill -INT "$PID" 2>/dev/null
wait "$PID" 2>/dev/null

echo "$(date) [排程] 完成" >> "$LOG_FILE"
