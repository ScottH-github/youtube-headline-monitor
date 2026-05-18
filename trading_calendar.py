"""交易日曆：判斷今天是否為台股開盤日"""

import json
import os
import ssl
import urllib.request
import urllib.error
from datetime import datetime


# 本地行事曆（每年底從政府 data.gov.tw 下載 CSV 更新）
# 資料來源：https://data.gov.tw/dataset/14718
HOLIDAYS_PATH = os.environ.get("HOLIDAYS_JSON_PATH", "holidays.json")

# 行政院人事行政總處停班停課查詢頁面
TYPHOON_URL = "https://www.dgpa.gov.tw/typh/daily/nds.html"


def is_trading_day(today: datetime = None) -> tuple[bool, str]:
    """判斷是否為交易日，回傳 (是否開盤, 原因)

    優先順序：補班日(開盤) > 休市日(休市) > 週六日(休市) > 颱風假(休市) > 正常開盤

    holidays.json 資料來源為政府行政機關辦公日曆表，每年底更新一次。
    """
    if today is None:
        today = datetime.now()

    year = str(today.year)
    mmdd = today.strftime("%m-%d")
    weekday = today.weekday()  # 0=Mon, 6=Sun

    holidays, makeup_days = _load_calendar(year)

    # 1. 補班日 → 開盤
    if mmdd in makeup_days:
        return True, f"補班日 ({mmdd})"

    # 2. 休市日 → 休市
    if mmdd in holidays:
        return False, f"休市日 ({mmdd})"

    # 3. 週六日 → 休市
    if weekday >= 5:
        return False, f"週末 ({['六', '日'][weekday - 5]})"

    # 4. 颱風假 → 休市
    is_typhoon, typhoon_msg = _check_typhoon_day()
    if is_typhoon:
        return False, f"颱風假 ({typhoon_msg})"

    # 5. 正常開盤
    return True, "正常交易日"


def _load_calendar(year: str) -> tuple[set, set]:
    """讀取 holidays.json，回傳 (holidays set, makeup_days set)"""
    if not os.path.exists(HOLIDAYS_PATH):
        print(f"[交易日曆] 找不到 {HOLIDAYS_PATH}，預設為正常交易日")
        return set(), set()

    try:
        with open(HOLIDAYS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        year_data = data.get(year, {})
        holidays = set(year_data.get("holidays", []))
        makeup_days = set(year_data.get("makeup_days", []))
        return holidays, makeup_days
    except Exception as e:
        print(f"[交易日曆] 讀取 {HOLIDAYS_PATH} 失敗: {e}")
        return set(), set()


def _check_typhoon_day() -> tuple[bool, str]:
    """查詢停班停課頁面，檢查台北市是否停班

    查詢失敗時預設回傳 False（正常執行）
    """
    try:
        req = urllib.request.Request(TYPHOON_URL, headers={"User-Agent": "headline-monitor/1.0"})
        try:
            resp = urllib.request.urlopen(req, timeout=10)
        except (ssl.SSLError, urllib.error.URLError):
            ctx = ssl._create_unverified_context()
            resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        with resp:
            html = resp.read().decode("utf-8")

        if "無停班停課訊息" in html:
            return False, ""
        if ("臺北市" in html or "台北市" in html) and "停止上班" in html:
            return True, "台北市停班停課"
        return False, ""
    except Exception as e:
        print(f"[交易日曆] 停班停課查詢失敗: {e}（預設正常執行）")
        return False, ""


if __name__ == "__main__":
    trading, reason = is_trading_day()
    print(f"今天 ({datetime.now().strftime('%Y-%m-%d %A')}) {'開盤' if trading else '休市'}: {reason}")
