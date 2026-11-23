#!/usr/bin/env python3
"""Print your recent messages to OpenCode, so one can be copied into a new chat.

The command is ~/bin/said, a three-line wrapper around this file; the tool lives here so it is
backed up with the project.

    said                 the last 12

    said                 the last 12
    said 30              the last 30
    said --session abc   only that session (id prefix)
    said --html ~/said.html   write a page with a copy button per message

Reads the local OpenCode database read-only. Nothing is written there.
"""

import argparse
import html
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"


def rows(limit, session=None):
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=2)
    con.row_factory = sqlite3.Row
    sql = (
        "select m.session_id, m.time_created, m.data, s.title, s.directory "
        "from session_message m left join session_v2 s on s.id = m.session_id "
        "where m.type = 'user'"
    )
    args = []
    if session:
        sql += " and m.session_id like ?"
        args.append(f"{session}%")
    sql += " order by m.time_created desc limit ?"
    args.append(limit * 3)
    out = []
    for row in con.execute(sql, args):
        try:
            text = sqlite3.connect(":memory:").execute("select json_extract(?, '$.text')",
                                                       (row["data"],)).fetchone()[0]
        except sqlite3.Error:
            text = None
        if not text or not text.strip():
            continue
        text = text.strip()
        if out and out[-1]["text"] == text:
            continue
        out.append({
            "session": row["session_id"],
            "title": (row["title"] or "").strip(),
            "directory": (row["directory"] or "").strip(),
            "at": datetime.fromtimestamp(row["time_created"] / 1000).strftime("%Y-%m-%d %H:%M"),
            "text": text,
        })
        if len(out) >= limit:
            break
    con.close()
    return list(reversed(out))


def plain(items):
    chunks = []
    for item in items:
        where = Path(item["directory"]).name if item["directory"] else ""
        head = f"── {item['at']} · {where or item['title'] or item['session'][:12]} ──"
        chunks.append(f"{head}\n{item['text']}")
    return "\n\n".join(chunks)


def page(items, out):
    cards = []
    for i, item in enumerate(items):
        where = Path(item["directory"]).name if item["directory"] else ""
        cards.append(
            f'<article><header><span>{html.escape(item["at"])} · '
            f'{html.escape(where or item["title"])}</span>'
            f'<button data-i="{i}">copy</button></header>'
            f'<pre id="t{i}">{html.escape(item["text"])}</pre></article>'
        )
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>my recent messages</title>
<style>
body {{ margin:0; padding:20px; background:#faf6ec; color:#2b2620;
       font:15px/1.6 ui-sans-serif, system-ui, sans-serif; }}
h1 {{ font-size:18px; margin:0 0 4px; }}
p {{ margin:0 0 16px; color:#6b5d49; font-size:13px; }}
article {{ background:#fff; border:1px solid #e6dccb; margin:0 0 12px; padding:10px 12px; }}
header {{ display:flex; justify-content:space-between; align-items:center; gap:10px;
          font:11px/1.4 ui-monospace, Menlo, monospace; color:#7a5a1f; margin-bottom:6px; }}
pre {{ margin:0; white-space:pre-wrap; font:14px/1.6 ui-sans-serif, system-ui, sans-serif; }}
button {{ font:11px/1 ui-monospace, Menlo, monospace; padding:4px 8px; cursor:pointer;
          border:1px solid #d9c9a8; background:#fdf9f0; }}
button.ok {{ background:#e6f3e6; }}
</style></head><body>
<h1>my recent messages</h1>
<p>{len(items)} messages · regenerate with <code>said --html ~/said.html</code></p>
{"".join(cards)}
<script>
for (const b of document.querySelectorAll("button[data-i]")) {{
  b.addEventListener("click", async () => {{
    await navigator.clipboard.writeText(document.getElementById("t" + b.dataset.i).textContent);
    b.textContent = "copied"; b.classList.add("ok");
    setTimeout(() => {{ b.textContent = "copy"; b.classList.remove("ok"); }}, 1200);
  }});
}}
</script></body></html>"""
    Path(out).expanduser().write_text(doc)
    return len(items)


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("count", nargs="?", type=int, default=12)
    ap.add_argument("--session", default=None)
    ap.add_argument("--html", default=None)
    args = ap.parse_args()
    if not DB.exists():
        print(f"no OpenCode database at {DB}", file=sys.stderr)
        return 1
    items = rows(max(1, args.count), args.session)
    if args.html:
        print(f"{page(items, args.html)} messages -> {Path(args.html).expanduser()}")
    else:
        print(plain(items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
