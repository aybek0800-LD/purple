"""
ChromeExtractor — извлекает артефакты из Google Chrome.
"""

import json
import logging
from pathlib import Path

from core.db        import SafeDB
from core.models    import BrowserData, HistoryEntry, CookieEntry, BookmarkEntry, AutofillEntry
from core.timeutils import chrome_time, unix_time
from core.paths     import get_browser_paths
from extractors.base import BaseExtractor

log = logging.getLogger("forensics.chrome")

PROFILES = ["Default", "Profile 1", "Profile 2", "Profile 3", "Profile 4"]


class ChromeExtractor(BaseExtractor):
    name = "Chrome"

    def __init__(self, base_path: Path = None):
        if base_path is None:
            base_path = get_browser_paths().get("chrome", Path())
        self.base_path = Path(base_path)

    def extract(self) -> BrowserData:
        data = BrowserData()
        if not self.base_path.exists():
            log.debug("Chrome not found at %s", self.base_path)
            return data

        with SafeDB() as db:
            for profile in PROFILES:
                profile_dir = self.base_path / profile
                if not profile_dir.is_dir():
                    continue
                self._history(db, profile_dir, data)
                self._cookies(db, profile_dir, data)
                self._bookmarks(profile_dir, data)
                self._autofill(db, profile_dir, data)

        return data

    # ── История ──────────────────────────────────────────────
    def _history(self, db: SafeDB, profile: Path, data: BrowserData) -> None:
        rows = db.query(
            profile / "History",
            "SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC",
        )
        for r in rows:
            data.history.append(HistoryEntry(
                browser=self.name,
                url=r["url"],
                title=r["title"] or r["url"],
                time=chrome_time(r["last_visit_time"]),
                visits=r["visit_count"],
            ))

    # ── Cookies (только метаданные) ──────────────────────────
    def _cookies(self, db: SafeDB, profile: Path, data: BrowserData) -> None:
        cookie_db = profile / "Network" / "Cookies"
        if not cookie_db.exists():
            cookie_db = profile / "Cookies"
        rows = db.query(
            cookie_db,
            "SELECT host_key, name, is_httponly, is_secure, expires_utc FROM cookies",
        )
        for r in rows:
            data.cookies.append(CookieEntry(
                browser=self.name,
                domain=r["host_key"],
                name=r["name"],
                http_only=bool(r["is_httponly"]),
                secure=bool(r["is_secure"]),
                expires=chrome_time(r["expires_utc"]) if r["expires_utc"] else "Session",
                size=len(r["name"]),
            ))

    # ── Закладки ─────────────────────────────────────────────
    def _bookmarks(self, profile: Path, data: BrowserData) -> None:
        bm_file = profile / "Bookmarks"
        if not bm_file.exists():
            return
        try:
            with open(bm_file, encoding="utf-8") as f:
                bm = json.load(f)

            def walk(node, folder="Root"):
                if node.get("type") == "url":
                    data.bookmarks.append(BookmarkEntry(
                        browser=self.name,
                        folder=folder,
                        title=node.get("name", ""),
                        url=node.get("url", ""),
                        added=chrome_time(int(node.get("date_added", 0))),
                    ))
                for child in node.get("children", []):
                    walk(child, node.get("name", folder))

            for root in bm.get("roots", {}).values():
                walk(root)
        except Exception as e:
            log.debug("Bookmarks error: %s", e)

    # ── Автозаполнение ────────────────────────────────────────
    def _autofill(self, db: SafeDB, profile: Path, data: BrowserData) -> None:
        rows = db.query(
            profile / "Web Data",
            "SELECT name, value, count, date_last_used FROM autofill ORDER BY count DESC",
        )
        for r in rows:
            data.autofill.append(AutofillEntry(
                browser=self.name,
                field=r["name"],
                value=r["value"],
                uses=r["count"],
                last=unix_time(r["date_last_used"]),
            ))
