# Browser Forensics — Digital Footprint Reconstructor

> Инструмент цифровой криминалистики для анализа браузерных артефактов.  
> Chrome · Firefox · Edge → единая хронология, cookies, закладки, автозаполнение.

---

## Быстрый старт

```bash
python main.py                          # все браузеры
python main.py --browsers chrome        # только Chrome
python main.py --out my_report --no-html  # только JSON
```

## Структура проекта

```
forensics/
├── main.py                  # точка входа, CLI
├── core/
│   ├── models.py            # dataclasses: HistoryEntry, CookieEntry, ...
│   ├── db.py                # SafeDB — безопасное чтение SQLite
│   ├── collector.py         # сборка и дедупликация данных
│   ├── report.py            # генерация JSON и HTML отчётов
│   └── timeutils.py         # конвертация временных меток
├── extractors/
│   ├── base.py              # абстрактный BaseExtractor (ABC)
│   ├── chrome.py            # ChromeExtractor
│   ├── edge.py              # EdgeExtractor (наследует Chrome)
│   └── firefox.py           # FirefoxExtractor
└── tests/
    └── test_forensics.py    # unit-тесты (pytest)
```

## Артефакты

| Тип | Chrome | Edge | Firefox |
|-----|--------|------|---------|
| История посещений | ✅ | ✅ | ✅ |
| Cookies (метаданные) | ✅ | ✅ | ✅ |
| Закладки | ✅ | ✅ | ✅ |
| Автозаполнение форм | ✅ | ✅ | ✅ |
| Пароли | ❌ | ❌ | ❌ |

> Пароли намеренно исключены — инструмент предназначен для аудита цифрового следа, а не извлечения credentials.

## Требования

- Python 3.10+
- Стандартная библиотека (sqlite3, json, shutil, dataclasses)
- Без сторонних зависимостей

## Тесты

```bash
python -m pytest tests/ -v
```

## Выходные файлы

- `forensics_report.json` — данные для импорта в веб-интерфейс
- `forensics_report.html` — автономный HTML-отчёт

## Добавить новый браузер

1. Создать `extractors/brave.py`
2. Унаследовать `ChromeExtractor` (Brave использует ту же структуру):

```python
from extractors.chrome import ChromeExtractor
class BraveExtractor(ChromeExtractor):
    name = "Brave"
    def __init__(self):
        super().__init__(base_path=Path(...) / "BraveSoftware" / "Brave-Browser" / "User Data")
```

3. Добавить `"brave": BraveExtractor` в `main.py`
