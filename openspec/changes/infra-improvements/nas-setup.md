## NAS 部署設定（更新後）

### 實體路徑
```
/volume1/docker/youtube-headline-monitor/
├── output/       ← bind mount → /app/output
├── deploy/       ← bind mount → /app/deploy
└── holidays.json ← bind mount → /app/holidays.json
```

### docker run 指令
```bash
/usr/local/bin/docker run --rm --name headline-monitor \
  -e TZ=Asia/Taipei -e PYTHONUNBUFFERED=1 \
  -e GIT_AUTHOR_NAME=Scott -e GIT_AUTHOR_EMAIL=scott@headline-monitor \
  -e GIT_COMMITTER_NAME=Scott -e GIT_COMMITTER_EMAIL=scott@headline-monitor \
  -e DEPLOY_REPO_URL=<從.env取得> \
  -v /volume1/docker/youtube-headline-monitor/output:/app/output \
  -v /volume1/docker/youtube-headline-monitor/deploy:/app/deploy \
  -v /volume1/docker/youtube-headline-monitor/holidays.json:/app/holidays.json:ro \
  youtube-headline-monitor:latest \
  'https://www.youtube.com/live/AEBeWMM1atA?si=2FK3jfOGq9CpOa5C'
```

### NAS crontab（/etc/crontab）
```
# 每天 08:30 啟動（含週六日，由程式判斷是否為交易日）
30 8 * * * root /usr/local/bin/docker run --rm --name headline-monitor -e TZ=Asia/Taipei -e PYTHONUNBUFFERED=1 -e GIT_AUTHOR_NAME=Scott -e GIT_AUTHOR_EMAIL=scott@headline-monitor -e GIT_COMMITTER_NAME=Scott -e GIT_COMMITTER_EMAIL=scott@headline-monitor -e DEPLOY_REPO_URL=<URL> -v /volume1/docker/youtube-headline-monitor/output:/app/output -v /volume1/docker/youtube-headline-monitor/deploy:/app/deploy -v /volume1/docker/youtube-headline-monitor/holidays.json:/app/holidays.json:ro youtube-headline-monitor:latest 'https://www.youtube.com/live/AEBeWMM1atA?si=2FK3jfOGq9CpOa5C' >> /volume1/docker/youtube-headline-monitor/cron.log 2>&1 &

# 每天 13:35 停止（用 docker stop 送 SIGTERM，讓程式正常結束產生報告+部署）
35 13 * * * root /usr/local/bin/docker stop headline-monitor 2>/dev/null
```

### 注意事項
- 必須用 `docker stop`（SIGTERM）而非 `docker kill`（SIGKILL），否則程式無法正常結束、不會產生報告
- 容器名稱改為 `headline-monitor`（--rm 自動刪除，不衝突）
- holidays.json 以 `:ro` 唯讀掛載
- cron 改為每天（`* * *`），交易日判斷由 trading_calendar.py 負責
- 非交易日容器啟動後會立即退出，--rm 自動清除
