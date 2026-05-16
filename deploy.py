"""部署 HTML 報告到 GitHub Pages（月份結構）"""

import os
import shutil
import subprocess
from datetime import datetime


DEPLOY_DIR = "deploy"


def deploy_report(report_path: str = "output/report.html"):
    """將 HTML 報告部署到 GitHub Pages（月份資料夾結構）"""
    if not os.path.exists(report_path):
        print(f"[部署] 找不到報告: {report_path}")
        return False

    today = datetime.now()
    month_dir = today.strftime("%Y%m")
    day_file = today.strftime("%Y-%m-%d") + ".html"

    os.makedirs(DEPLOY_DIR, exist_ok=True)

    # 初始化 git repo
    if not os.path.exists(os.path.join(DEPLOY_DIR, ".git")):
        repo_url = _get_repo_url()
        if not repo_url:
            return False
        _run("git init", cwd=DEPLOY_DIR)
        _run(f"git remote add origin {repo_url}", cwd=DEPLOY_DIR)
        _run("git checkout -b gh-pages", cwd=DEPLOY_DIR)

    # 建立月份資料夾並複製報告
    target_dir = os.path.join(DEPLOY_DIR, month_dir)
    os.makedirs(target_dir, exist_ok=True)
    shutil.copy2(report_path, os.path.join(target_dir, day_file))

    # 產生月份子頁 index
    _generate_month_index(target_dir, month_dir)

    # 產生主頁 index
    _generate_main_index(DEPLOY_DIR)

    # git add + commit + push
    _run("git add -A", cwd=DEPLOY_DIR)

    result = _run("git diff --cached --quiet", cwd=DEPLOY_DIR, check=False)
    if result.returncode == 0:
        print("[部署] 無變更，跳過")
        return True

    commit_msg = f"Update report {today.strftime('%Y-%m-%d')}"
    _run(f'git commit -m "{commit_msg}"', cwd=DEPLOY_DIR)
    _run("git push -u origin gh-pages --force", cwd=DEPLOY_DIR)

    print(f"[部署] 報告已發佈!")
    return True


def _get_repo_url():
    """取得 GitHub repo URL（環境變數 > 檔案 > 互動輸入）"""
    env_url = os.environ.get("DEPLOY_REPO_URL")
    if env_url:
        return env_url

    config_file = os.path.join(DEPLOY_DIR, ".repo_url")
    if os.path.exists(config_file):
        with open(config_file) as f:
            return f.read().strip()

    try:
        url = input("[部署] 請輸入 GitHub repo URL (例如 git@github.com:user/repo.git): ").strip()
    except EOFError:
        url = ""

    if not url:
        print("[部署] 未設定 repo URL，取消部署。可設定環境變數 DEPLOY_REPO_URL")
        return None

    with open(config_file, "w") as f:
        f.write(url)
    return url


def _generate_month_index(month_path: str, month_dir: str):
    """產生月份子頁 index.html（列出該月每日報告）"""
    reports = sorted(
        [f for f in os.listdir(month_path) if f.endswith(".html") and f != "index.html"],
        reverse=True,
    )

    year = month_dir[:4]
    month = month_dir[4:]
    display_month = f"{year}-{month}"

    rows = ""
    for r in reports:
        date = r.replace(".html", "")
        rows += f'        <li><a href="{r}">{date}</a></li>\n'

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<title>新聞頭條 - {display_month}</title>
<style>
    body {{ font-family: -apple-system, "Microsoft JhengHei", sans-serif; background: #1a1a2e; color: #eee; padding: 40px; }}
    h1 {{ color: #f0c040; margin-bottom: 10px; }}
    .back-link {{ margin-bottom: 20px; }}
    .back-link a {{ color: #6cb4ee; text-decoration: none; font-size: 16px; }}
    .back-link a:hover {{ text-decoration: underline; }}
    a {{ color: #6cb4ee; text-decoration: none; font-size: 18px; }}
    a:hover {{ text-decoration: underline; }}
    li {{ margin: 12px 0; }}
    .count {{ color: #aaa; font-size: 14px; margin-bottom: 20px; }}
</style>
</head>
<body>
    <div class="back-link"><a href="../index.html">&larr; 回主頁</a></div>
    <h1>{display_month} 每日報告</h1>
    <p class="count">共 {len(reports)} 份報告</p>
    <ul>
{rows}    </ul>
</body>
</html>"""

    with open(os.path.join(month_path, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def _generate_main_index(deploy_dir: str):
    """產生主頁 index.html（列出所有月份連結）"""
    months = sorted(
        [d for d in os.listdir(deploy_dir)
         if os.path.isdir(os.path.join(deploy_dir, d)) and d.isdigit() and len(d) == 6],
        reverse=True,
    )

    rows = ""
    for m in months:
        display = f"{m[:4]}-{m[4:]}"
        # 計算該月報告數量
        month_path = os.path.join(deploy_dir, m)
        report_count = len([f for f in os.listdir(month_path) if f.endswith(".html") and f != "index.html"])
        rows += f'        <li><a href="{m}/index.html">{display}</a> <span class="count">({report_count} 份)</span></li>\n'

    # 找最新的報告連結
    latest_link = ""
    if months:
        latest_month = months[0]
        month_path = os.path.join(deploy_dir, latest_month)
        reports = sorted([f for f in os.listdir(month_path) if f.endswith(".html") and f != "index.html"], reverse=True)
        if reports:
            latest_link = f'{latest_month}/{reports[0]}'

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<title>新聞頭條擷取 - 歷史報告</title>
<style>
    body {{ font-family: -apple-system, "Microsoft JhengHei", sans-serif; background: #1a1a2e; color: #eee; padding: 40px; }}
    h1 {{ color: #f0c040; margin-bottom: 20px; }}
    a {{ color: #6cb4ee; text-decoration: none; font-size: 18px; }}
    a:hover {{ text-decoration: underline; }}
    li {{ margin: 12px 0; }}
    .count {{ color: #888; font-size: 14px; }}
    .latest {{ margin: 20px 0; padding: 15px; background: #16213e; border-radius: 8px; }}
    .latest a {{ font-size: 20px; color: #f0c040; }}
</style>
</head>
<body>
    <h1>新聞頭條擷取 - 歷史報告</h1>
    <div class="latest">
        <a href="{latest_link}">最新報告: {latest_link.replace('/', ' / ').replace('.html', '') if latest_link else 'N/A'}</a>
    </div>
    <h2>月份報告</h2>
    <ul>
{rows}    </ul>
</body>
</html>"""

    with open(os.path.join(deploy_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def _run(cmd, cwd=None, check=True):
    """執行 shell 命令"""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"[部署] 命令失敗: {cmd}")
        print(f"  stderr: {result.stderr.strip()}")
    return result


if __name__ == "__main__":
    deploy_report()
