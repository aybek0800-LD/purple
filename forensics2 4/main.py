"""
╔══════════════════════════════════════════════════════════╗
║         BROWSER FORENSICS — Digital Footprint Tool       ║
║  История · Cookies · Закладки · Автозаполнение           ║
║  Chrome · Firefox · Edge                                 ║
╚══════════════════════════════════════════════════════════╝

Использование:
    python main.py
    python main.py --browsers chrome firefox
    python main.py --out report --no-html
"""

import argparse
import logging
import sys
from pathlib import Path

from core.collector import ForensicsCollector
from core.report    import ReportBuilder
from core.paths     import get_os_name
from extractors.chrome  import ChromeExtractor
from extractors.edge    import EdgeExtractor
from extractors.firefox import FirefoxExtractor

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
log = logging.getLogger("forensics")

EXTRACTORS = {
    "chrome":  ChromeExtractor,
    "edge":    EdgeExtractor,
    "firefox": FirefoxExtractor,
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Browser Forensics Extractor")
    p.add_argument(
        "--browsers", nargs="+",
        choices=list(EXTRACTORS.keys()),
        default=list(EXTRACTORS.keys()),
        help="Список браузеров для анализа (по умолчанию — все)",
    )
    p.add_argument("--out",     default="forensics_report", help="Имя файла отчёта (без расширения)")
    p.add_argument("--no-html", action="store_true", help="Не генерировать HTML-отчёт")
    p.add_argument("--no-json", action="store_true", help="Не генерировать JSON-отчёт")
    p.add_argument("--limit",   type=int, default=500, help="Лимит записей на браузер (по умолчанию 500)")
    p.add_argument("--no-open", action="store_true", help="Не открывать HTML в браузере после генерации")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    print("""
  ██████╗ ██████╗  ██████╗ ██╗    ██╗███████╗███████╗██████╗
  ██╔══██╗██╔══██╗██╔═══██╗██║    ██║██╔════╝██╔════╝██╔══██╗
  ██████╔╝██████╔╝██║   ██║██║ █╗ ██║███████╗█████╗  ██████╔╝
  ██╔══██╗██╔══██╗██║   ██║██║███╗██║╚════██║██╔══╝  ██╔══██╗
  ██████╔╝██║  ██║╚██████╔╝╚███╔███╔╝███████║███████╗██║  ██║
  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝ ╚══════╝╚══════╝╚═╝  ╚═╝
  FORENSICS  —  Digital Footprint Reconstructor
    """)

    log.info("OS detected: %s", get_os_name())

    collector = ForensicsCollector(limit=args.limit)

    for name in args.browsers:
        extractor_cls = EXTRACTORS[name]
        extractor = extractor_cls()
        log.info("Extracting %-8s ...", name.capitalize())
        data = extractor.extract()
        collector.add(data)
        log.info(
            "  history=%-4d  cookies=%-4d  bookmarks=%-4d  autofill=%-4d",
            len(data.history), len(data.cookies),
            len(data.bookmarks), len(data.autofill),
        )

    report = collector.build()
    builder = ReportBuilder(report)

    if not args.no_json:
        json_path = Path(args.out).with_suffix(".json")
        builder.save_json(json_path)
        log.info("JSON → %s", json_path.resolve())

    if not args.no_html:
        html_path = Path(args.out).with_suffix(".html")
        builder.save_html(html_path)
        log.info("HTML → %s", html_path.resolve())
        if not args.no_open:
            import webbrowser
            webbrowser.open(str(html_path.resolve()))

    summary = collector.summary()
    print("\n" + "─" * 50)
    print(f"  Total history  : {summary['history']}")
    print(f"  Total cookies  : {summary['cookies']}")
    print(f"  Total bookmarks: {summary['bookmarks']}")
    print(f"  Total autofill : {summary['autofill']}")
    print(f"  Browsers found : {', '.join(summary['browsers_found'])}")
    print("─" * 50)
    print("  Done.\n")


if __name__ == "__main__":
    main()
