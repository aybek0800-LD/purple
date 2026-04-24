"""
Утилиты для конвертации временных меток браузеров.
"""

from datetime import datetime, timezone, timedelta


def chrome_time(microseconds: int) -> str:
    """Chrome timestamp (мкс с 1601-01-01) → 'YYYY-MM-DD HH:MM'."""
    try:
        epoch = datetime(1601, 1, 1, tzinfo=timezone.utc)
        dt = epoch + timedelta(microseconds=int(microseconds))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ""


def unix_time(seconds: int | float) -> str:
    """Unix timestamp → 'YYYY-MM-DD HH:MM'."""
    try:
        return datetime.fromtimestamp(float(seconds)).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ""


def firefox_time(microseconds: int) -> str:
    """Firefox timestamp (мкс с Unix epoch) → 'YYYY-MM-DD HH:MM'."""
    try:
        return unix_time(int(microseconds) / 1_000_000)
    except Exception:
        return ""
