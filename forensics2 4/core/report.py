"""
ReportBuilder — генерирует JSON и HTML-отчёты из ForensicsReport.
"""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from core.models import ForensicsReport


class ReportBuilder:
    def __init__(self, report: ForensicsReport):
        self.report = report

    # ── JSON ─────────────────────────────────────────────────
    def save_json(self, path: Path) -> None:
        data = {
            "generated": self.report.generated,
            "history":   [asdict(e) for e in self.report.history],
            "cookies":   [asdict(e) for e in self.report.cookies],
            "bookmarks": [asdict(e) for e in self.report.bookmarks],
            "autofill":  [asdict(e) for e in self.report.autofill],
        }
        # Переименовываем поля под формат виджета
        for h in data["history"]:
            pass  # уже совпадает
        for c in data["cookies"]:
            c["httpOnly"] = c.pop("http_only")

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── HTML ─────────────────────────────────────────────────
    def save_html(self, path: Path) -> None:
        r = self.report

        def table(items, keys, labels=None):
            labels = labels or keys
            head = "".join(f"<th>{l}</th>" for l in labels)
            body = ""
            for item in items:
                d = asdict(item)
                body += "<tr>" + "".join(f"<td>{d.get(k, '')}</td>" for k in keys) + "</tr>"
            return f"<table><tr>{head}</tr>{body}</table>"

        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Browser Forensics Report</title>
<style>
  :root{{--bg:#0d1117;--bg2:#161b22;--bg3:#21262d;--border:#30363d;--text:#c9d1d9;--muted:#8b949e;--accent:#58a6ff}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:system-ui,sans-serif;padding:40px 32px}}
  h1{{color:var(--accent);font-size:22px;margin-bottom:4px}}
  h2{{color:var(--accent);font-size:14px;font-weight:500;margin:2rem 0 .5rem;text-transform:uppercase;letter-spacing:.05em}}
  .meta{{color:var(--muted);font-size:13px;margin-bottom:2rem}}
  .stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:2.5rem}}
  .stat{{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:16px}}
  .stat-n{{font-size:30px;font-weight:600;color:var(--accent)}}
  .stat-l{{font-size:12px;color:var(--muted);margin-top:4px}}
  table{{width:100%;border-collapse:collapse;background:var(--bg2);margin-bottom:.5rem;font-size:12px}}
  th{{background:var(--bg3);color:var(--accent);padding:8px 10px;border:1px solid var(--border);text-align:left;font-weight:500}}
  td{{padding:7px 10px;border:1px solid var(--border);color:var(--muted);max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  tr:hover td{{color:var(--text)}}
  .badge{{display:inline-block;padding:1px 8px;border-radius:20px;font-size:11px}}
  .chrome{{background:#1a3a5c;color:#58a6ff}}
  .firefox{{background:#1a3a1a;color:#7ee787}}
  .edge{{background:#2d1a5c;color:#a5a0e6}}
</style>
</head>
<body>

<h1>Browser Forensics Report</h1>
<p class="meta">Generated: {r.generated} · For educational and audit purposes only</p>

<div class="stats">
  <div class="stat"><div class="stat-n">{len(r.history)}</div><div class="stat-l">History entries</div></div>
  <div class="stat"><div class="stat-n">{len(r.cookies)}</div><div class="stat-l">Cookies</div></div>
  <div class="stat"><div class="stat-n">{len(r.bookmarks)}</div><div class="stat-l">Bookmarks</div></div>
  <div class="stat"><div class="stat-n">{len(r.autofill)}</div><div class="stat-l">Autofill entries</div></div>
</div>

<h2>History — last {min(len(r.history), 200)} entries</h2>
{table(r.history[:200], ['browser','time','title','url','visits'])}

<h2>Cookies metadata — {len(r.cookies)} entries</h2>
{table(r.cookies, ['browser','domain','name','http_only','secure','expires'],
       ['Browser','Domain','Name','HttpOnly','Secure','Expires'])}

<h2>Bookmarks — {len(r.bookmarks)} entries</h2>
{table(r.bookmarks, ['browser','folder','title','url','added'])}

<h2>Autofill — {len(r.autofill)} entries</h2>
{table(r.autofill, ['browser','field','value','uses','last'])}

</body></html>"""
        path.write_text(html, encoding="utf-8")
