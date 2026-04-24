"""
Модели данных — все типы артефактов браузера.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class HistoryEntry:
    browser:  str
    url:      str
    title:    str
    time:     str
    visits:   int


@dataclass
class CookieEntry:
    browser:   str
    domain:    str
    name:      str
    http_only: bool
    secure:    bool
    expires:   str
    size:      int


@dataclass
class BookmarkEntry:
    browser: str
    folder:  str
    title:   str
    url:     str
    added:   str


@dataclass
class AutofillEntry:
    browser: str
    field:   str
    value:   str
    uses:    int
    last:    str


@dataclass
class BrowserData:
    """Все артефакты одного браузера."""
    history:   List[HistoryEntry]   = field(default_factory=list)
    cookies:   List[CookieEntry]    = field(default_factory=list)
    bookmarks: List[BookmarkEntry]  = field(default_factory=list)
    autofill:  List[AutofillEntry]  = field(default_factory=list)


@dataclass
class ForensicsReport:
    """Итоговый отчёт по всем браузерам."""
    history:   List[HistoryEntry]   = field(default_factory=list)
    cookies:   List[CookieEntry]    = field(default_factory=list)
    bookmarks: List[BookmarkEntry]  = field(default_factory=list)
    autofill:  List[AutofillEntry]  = field(default_factory=list)
    generated: str                  = ""
