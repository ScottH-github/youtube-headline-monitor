FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# eMudhra CA 事件（2026-10）：先升級 pip/certifi，舊 pip 內嵌的 certifi 仍信任遭破解的 emSign CA
RUN pip install --no-cache-dir -U "pip>=26.2.2" "certifi>=2026.10.19"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./
COPY holidays.json ./

RUN mkdir -p output/frames output/headlines output/debug

ENV PYTHONUNBUFFERED=1
ENV DEPLOY_REPO_URL=https://github.com/ScottH-github/youtube-headline-monitor.git

ENTRYPOINT ["python3", "main.py"]
