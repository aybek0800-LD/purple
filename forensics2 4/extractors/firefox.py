"""
FirefoxExtractor — извлекает артефакты из Mozilla Firefox.
"""

import logging
from pathlib import Path

from core.db        import SafeDB
from core.models    import BrowserData, HistoryEntry, CookieEntry, BookmarkEntry, AutofillEntry
from core.timeutils import unix_time, firefox_time
from core.paths     import get_browser_paths
from extractors.base import BaseExtractor

log = logging.getLogger("forensics.firefox")


class FirefoxExtractor(BaseExtractor):
    name = "Firefox"

    def __init__(self, base_path: Path = None):
        if base_path is None:
            base_path = get_browser_paths().get("firefox", Path())
        self.base_path = Path(base_path)

    def extract(self) -> BrowserData:
        data = BrowserData()
        if not self.base_path.exists():
            log.debug("Firefox not found at %s", self.base_path)
            return data

        profiles = [p for p in self.base_path.iterdir()
                    if p.is_dir() and (p / "places.sqlite").exists()]
        with SafeDB() as db:
            for profile in profiles:
                self._history_and_bookmarks(db, profile, data)
                self._cookies(db, profile, data)
                self._autofill(db, profile, data)

        return data

    # ── История + Закладки (обе в places.sqlite) ─────────────
    def _history_and_bookmarks(self, db: SafeDB, profile: Path, data: BrowserData) -> None:
        # История
        rows = db.query(
            profile / "places.sqlite",
            """SELECT p.url, p.title, p.visit_count, h.visit_date
               FROM moz_places p
               JOIN moz_historyvisits h ON p.id = h.place_id
               ORDER BY h.visit_date DESC""",
        )
        for r in rows:
            data.history.append(HistoryEntry(
                browser=self.name,
                url=r["url"],
                title=r["title"] or r["url"],
                time=firefox_time(r["visit_date"]),
                visits=r["visit_count"],
            ))

        # Закладки
        rows = db.query(
            profile / "places.sqlite",
            """SELECT p.url, b.title, b.dateAdded
               FROM moz_bookmarks b
               JOIN moz_places p ON b.fk = p.id
               WHERE b.type = 1""",
        )
        for r in rows:
            data.bookmarks.append(BookmarkEntry(
                browser=self.name,
                folder="Firefox",
                title=r["title"] or r["url"],
                url=r["url"],
                added=firefox_time(r["dateAdded"]),
            ))

    # ── Cookies (только метаданные) ──────────────────────────
    def _cookies(self, db: SafeDB, profile: Path, data: BrowserData) -> None:
        rows = db.query(
            profile / "cookies.sqlite",
            "SELECT host, name, isHttpOnly, isSecure, expiry FROM moz_cookies",
        )
        for r in rows:
            data.cookies.append(CookieEntry(
                browser=self.name,
                domain=r["host"],
                name=r["name"],
                http_only=bool(r["isHttpOnly"]),
                secure=bool(r["isSecure"]),
                expires=unix_time(r["expiry"]) if r["expiry"] else "Session",
                size=len(r["name"]),
            ))

    # ── Автозаполнение ────────────────────────────────────────
    def _autofill(self, db: SafeDB, profile: Path, data: BrowserData) -> None:
        rows = db.query(
            profile / "formhistory.sqlite",
            "SELECT fieldname, value, timesUsed, lastUsed FROM moz_formhistory ORDER BY timesUsed DESC",
        )
        for r in rows:
            data.autofill.append(AutofillEntry(
                browser=self.name,
                field=r["fieldname"],
                value=r["value"],
                uses=r["timesUsed"],
                last=firefox_time(r["lastUsed"]),
            ))
