#!/usr/bin/env python3
"""Print your recent messages to OpenCode, so one can be copied into a new chat.

The command is ~/bin/said, a three-line wrapper around this file, so the tool is backed up with
the project.

    said                 the last 5 in this project, not the helper chats
    said 20              the last 20
    said --md 10         markdown, ready to paste into a chat
    said --all           every project and every helper chat
    said --session abc   one conversation (id prefix)
    said --html ~/said.html   a page with a copy button per message

Reads the local OpenCode database read-only. Nothing is written there.
"""

import argparse
import html
import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
HELPER_PREFIXES = ("ses-sidechat",)     # the side chat is another agent, not DeepSeek1


def rows(limit, session=None, every=False, here=True):
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=2)
    con.row_factory = sqlite3.Row
    cwd = os.getcwd()
    conditions = ["m.type = 'user'"]
    args = []
    if session:
        conditions.append("m.session_id like ?")
        args.append(f"{session}%")
    elif not every:
        if here:
            conditions.append("s.directory = ?")
            args.append(cwd)
        # a subagent's prompt is not the operator's message
        conditions.append("s.parent_id is null")
        for prefix in HELPER_PREFIXES:
            conditions.append("m.session_id not like ?")
            args.append(f"{prefix}%")
    where = " and ".join(conditions)
    base = (
        "select m.session_id, m.time_created, m.data, s.title, s.directory "
        "from session_message m left join session_v2 s on s.id = m.session_id "
        f"where {where}"
    )
    # one message can be several rows (its parts); count distinct texts, not rows
    total = con.execute(
        "select count(distinct json_extract(data, '$.text')) from "
        f"(select m.data as data from session_message m left join session_v2 s "
        f"on s.id = m.session_id where {where})", args).fetchone()[0]
    sql = base + " order by m.time_created desc limit ?"
    out = []
    for row in con.execute(sql, args + [max(limit * 3, 30)]):
        try:
            text = sqlite3.connect(":memory:").execute(
                "select json_extract(?, '$.text')", (row["data"],)).fetchone()[0]
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
    return list(reversed(out)), total


def label(item):
    where = Path(item["directory"]).name if item["directory"] else ""
    return f"{item['at']} · {where or item['title'] or item['session'][:12]}"


def plain(items):
    return "\n\n".join(f"── {label(i)} ──\n{i['text']}" for i in items)


def markdown(items):
    chunks = []
    for item in items:
        body = item["text"]
        # a message that already carries Markdown is pasted as it is; a plain one is quoted
        if any(mark in body for mark in ("\n#", "\n- ", "\n1. ", "```", "|")):
            chunks.append(f"### {label(item)}\n\n{body}")
        else:
            chunks.append(f"### {label(item)}\n\n{body}\n")
    return "\n\n".join(chunks)


def page(items, out):
    cards = []
    for i, item in enumerate(items):
        cards.append(
            f'<article><header><span>{html.escape(label(item))}</span>'
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


def push(items, out):
    """Write the messages for the Astro route /said/, which reads this file per request."""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "format": "curve-lab.said/1",
        "note": "The operator's own messages, newest last. Written by scripts/said.py; "
                "personal, gitignored, never committed.",
        "count": len(items),
        "messages": items,
    }, ensure_ascii=False, indent=1) + "\n")
    return out


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("count", nargs="?", type=int, default=5)
    ap.add_argument("--session", default=None)
    ap.add_argument("--html", default=None)
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--push", action="store_true",
                    help="write data/said.json for the Astro page at /said/")
    ap.add_argument("--all", action="store_true", help="every project and helper chat")
    args = ap.parse_args()
    if not DB.exists():
        print(f"no OpenCode database at {DB}", file=sys.stderr)
        return 1
    items, total = rows(max(1, args.count), args.session, args.all)
    if args.push:
        target = Path(os.environ.get("CURVE_LAB_ROOT", os.getcwd())) / "data" / "said.json"
        if not Path(target).parent.exists():
            target = Path("/Users/thomaskelly/developer/curve-lab/data/said.json")
        push(items, target)
        print(f"{len(items)} messages -> {target}\nhttp://127.0.0.1:4321/said/")
        return 0
    if args.html:
        n = page(items, args.html)
        print(f"{n} messages -> {Path(args.html).expanduser()}")
        return 0
    print(markdown(items) if args.md else plain(items))
    print(f"\n(showing {len(items)}; 'said 30' for more, or http://127.0.0.1:4321/said/)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
