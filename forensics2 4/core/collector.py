"""
ForensicsCollector — собирает данные со всех экстракторов,
дедуплицирует и сортирует.
"""

from datetime import datetime
from typing import List

from core.models import BrowserData, ForensicsReport


class ForensicsCollector:
    def __init__(self, limit: int = 500):
        self.limit = limit
        self._datasets: List[BrowserData] = []
        self._cache: ForensicsReport | None = None  # кэш для избежания двойного build()

    def add(self, data: BrowserData) -> None:
        self._datasets.append(data)
        self._cache = None  # сбрасываем кэш при добавлении новых данных

    def build(self) -> ForensicsReport:
        if self._cache is not None:
            return self._cache

        report = ForensicsReport(generated=datetime.now().strftime("%Y-%m-%d %H:%M"))
        for d in self._datasets:
            report.history.extend(d.history)
            report.cookies.extend(d.cookies)
            report.bookmarks.extend(d.bookmarks)
            report.autofill.extend(d.autofill)

        # Сортировка истории от новых к старым (пустые time — в конец)
        report.history.sort(key=lambda x: x.time or "", reverse=True)

        # Лимит записей истории
        report.history = report.history[: self.limit]

        self._cache = report
        return report

    def summary(self) -> dict:
        browsers_found = []
        for d in self._datasets:
            if d.history or d.cookies or d.bookmarks or d.autofill:
                # Определяем имя по первой записи
                for collection in [d.history, d.cookies, d.bookmarks, d.autofill]:
                    if collection:
                        browsers_found.append(collection[0].browser)
                        break

        # Переиспользуем кэшированный отчёт — не вызываем build() повторно
        report = self.build()
        return {
            "history":        len(report.history),
            "cookies":        len(report.cookies),
            "bookmarks":      len(report.bookmarks),
            "autofill":       len(report.autofill),
            "browsers_found": list(set(browsers_found)),
        }
