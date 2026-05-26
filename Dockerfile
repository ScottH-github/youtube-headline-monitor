FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./
COPY holidays.json ./

RUN mkdir -p output/frames output/headlines output/debug

ENV PYTHONUNBUFFERED=1
ENV DEPLOY_REPO_URL=https://github.com/ScottH-github/youtube-headline-monitor.git

ENTRYPOINT ["python3", "main.py"]
