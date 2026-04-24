"""
Тесты для Browser Forensics Extractor
Запуск: python -m pytest tests/ -v
"""

import pytest
from datetime import datetime
from core.timeutils import chrome_time, unix_time, firefox_time
from core.models    import BrowserData, HistoryEntry, CookieEntry
from core.collector import ForensicsCollector


# ── timeutils ────────────────────────────────────────────────
class TestTimeUtils:
    def test_chrome_time_valid(self):
        # 13374046800000000 мкс ≈ 2024-07-17
        result = chrome_time(13374046800000000)
        assert result.startswith("2024-")

    def test_chrome_time_zero(self):
        assert chrome_time(0) == "1601-01-01 00:00"

    def test_chrome_time_invalid(self):
        assert chrome_time("bad") == ""

    def test_unix_time_valid(self):
        result = unix_time(1700000000)
        assert result.startswith("2023-")

    def test_unix_time_zero(self):
        result = unix_time(0)
        assert result != ""

    def test_unix_time_invalid(self):
        assert unix_time("bad") == ""

    def test_firefox_time_valid(self):
        result = firefox_time(1700000000 * 1_000_000)
        assert result.startswith("2023-")


# ── models ────────────────────────────────────────────────────
class TestModels:
    def test_browser_data_defaults(self):
        d = BrowserData()
        assert d.history == []
        assert d.cookies == []
        assert d.bookmarks == []
        assert d.autofill == []

    def test_history_entry_fields(self):
        e = HistoryEntry(
            browser="Chrome", url="https://example.com",
            title="Example", time="2024-01-01 10:00", visits=5
        )
        assert e.browser == "Chrome"
        assert e.visits == 5

    def test_cookie_entry_fields(self):
        c = CookieEntry(
            browser="Firefox", domain=".example.com",
            name="session", http_only=True, secure=True,
            expires="2025-01-01 00:00", size=7
        )
        assert c.http_only is True
        assert c.size == 7


# ── collector ─────────────────────────────────────────────────
class TestCollector:
    def _make_data(self, browser: str, n: int) -> BrowserData:
        data = BrowserData()
        for i in range(n):
            data.history.append(HistoryEntry(
                browser=browser,
                url=f"https://example.com/{i}",
                title=f"Page {i}",
                time=f"2024-01-{i+1:02d} 10:00",
                visits=i + 1,
            ))
        return data

    def test_merge_two_browsers(self):
        collector = ForensicsCollector()
        collector.add(self._make_data("Chrome", 3))
        collector.add(self._make_data("Firefox", 2))
        report = collector.build()
        assert len(report.history) == 5

    def test_history_sorted_desc(self):
        collector = ForensicsCollector()
        data = BrowserData()
        data.history = [
            HistoryEntry("Chrome", "https://a.com", "A", "2024-01-01 09:00", 1),
            HistoryEntry("Chrome", "https://b.com", "B", "2024-03-01 09:00", 1),
            HistoryEntry("Chrome", "https://c.com", "C", "2024-02-01 09:00", 1),
        ]
        collector.add(data)
        report = collector.build()
        times = [e.time for e in report.history]
        assert times == sorted(times, reverse=True)

    def test_limit_respected(self):
        collector = ForensicsCollector(limit=5)
        collector.add(self._make_data("Chrome", 20))
        report = collector.build()
        assert len(report.history) == 5

    def test_summary_keys(self):
        collector = ForensicsCollector()
        collector.add(self._make_data("Chrome", 2))
        s = collector.summary()
        assert "history" in s
        assert "browsers_found" in s
