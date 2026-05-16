#!/bin/bash
# Synology NAS 排程腳本
# 在 Synology 排程任務中設定：週一~週五 08:30 執行
# 腳本會自動在 13:30 停止監控

PROJECT_DIR="/volume1/docker/youtube-headline-monitor"
CONTAINER_NAME="youtube-headline-monitor"
LOG_FILE="$PROJECT_DIR/output/monitor_$(date +%Y%m%d).log"

cd "$PROJECT_DIR"

echo "$(date) [排程] 啟動監控" >> "$LOG_FILE"

# 計算到 13:30 的秒數
END_HOUR=13
END_MIN=30
NOW_EPOCH=$(date +%s)
END_EPOCH=$(date -d "$(date +%Y-%m-%d) ${END_HOUR}:${END_MIN}:00" +%s 2>/dev/null)

# Synology 的 date 可能不支援 -d，用另一種方式
if [ -z "$END_EPOCH" ]; then
    CURRENT_H=$(date +%H)
    CURRENT_M=$(date +%M)
    CURRENT_S=$(date +%S)
    NOW_SECS=$((CURRENT_H * 3600 + CURRENT_M * 60 + CURRENT_S))
    END_SECS=$((END_HOUR * 3600 + END_MIN * 60))
    DURATION=$((END_SECS - NOW_SECS))
else
    DURATION=$((END_EPOCH - NOW_EPOCH))
fi

if [ "$DURATION" -le 0 ]; then
    echo "$(date) [排程] 已過 13:30，跳過" >> "$LOG_FILE"
    exit 0
fi

echo "$(date) [排程] 將執行 $((DURATION / 60)) 分鐘" >> "$LOG_FILE"

# 啟動 Docker 容器
docker compose up -d >> "$LOG_FILE" 2>&1

# 等待到 13:30
sleep "$DURATION"

# 發送 SIGINT 讓程式正常結束（產生報告 + 部署）
docker kill --signal=SIGINT "$CONTAINER_NAME" >> "$LOG_FILE" 2>&1

# 等待容器結束
docker wait "$CONTAINER_NAME" >> "$LOG_FILE" 2>&1

echo "$(date) [排程] 完成" >> "$LOG_FILE"
