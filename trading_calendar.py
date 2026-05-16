"""交易日曆：判斷今天是否為台股開盤日"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime


HOLIDAYS_PATH = os.environ.get("HOLIDAYS_JSON_PATH", "holidays.json")

# 行政院人事行政總處停班停課 API
TYPHOON_API_URL = "https://www.dgpa.gov.tw/api/typh"


def is_trading_day(today: datetime = None) -> tuple[bool, str]:
    """判斷是否為交易日，回傳 (是否開盤, 原因)

    優先順序：補班日(開盤) > 休市日(休市) > 週六日(休市) > 颱風假(休市) > 正常開盤
    """
    if today is None:
        today = datetime.now()

    year = str(today.year)
    mmdd = today.strftime("%m-%d")
    weekday = today.weekday()  # 0=Mon, 6=Sun

    # 讀取 holidays.json
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
    """查詢停班停課 API，檢查台北市是否停班

    API 失敗時預設回傳 False（正常執行）
    """
    try:
        req = urllib.request.Request(TYPHOON_API_URL, headers={"User-Agent": "headline-monitor/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        # API 回傳空陣列表示無停班停課
        if not data:
            return False, ""

        # 搜尋台北市的停班資訊
        for item in data:
            city = item.get("city", "") or item.get("CITY", "")
            is_work_off = item.get("isWorkOff", "") or item.get("IS_WORK_OFF", "")
            if "台北" in city and is_work_off == "是":
                return True, f"台北市停班 - {item.get('title', item.get('TITLE', ''))}"

        return False, ""
    except Exception as e:
        print(f"[交易日曆] 停班停課 API 查詢失敗: {e}（預設正常執行）")
        return False, ""


if __name__ == "__main__":
    trading, reason = is_trading_day()
    print(f"今天 ({datetime.now().strftime('%Y-%m-%d %A')}) {'開盤' if trading else '休市'}: {reason}")
