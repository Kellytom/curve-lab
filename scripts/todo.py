"""Render TODO.md as a twin HTML page with checkboxes and a progress bar.

    .venv/bin/python scripts/todo.py
    open workbench/todo.html

TODO.md is the source of truth. The page is read-only: check items in the
Markdown, rerun this script, and the twin follows.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "TODO.md"
OUT = ROOT / "workbench" / "todo.html"

INK, MUTED, GOLD, LINE, PAPER = "#2e2413", "#7b6c4e", "#8c6a21", "#d8ccae", "#fffdf7"


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def parse(lines):
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        if not line.strip():
            i += 1
            continue
        if line.startswith("# "):
            blocks.append(("h1", line[2:].strip()))
            i += 1
        elif line.startswith("## "):
            blocks.append(("h2", line[3:].strip()))
            i += 1
        elif line.startswith("### "):
            blocks.append(("h3", line[4:].strip()))
            i += 1
        elif line.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ").strip())
                i += 1
            blocks.append(("note", " ".join(buf)))
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(row)
                i += 1
            if len(rows) >= 2 and all(set(c) <= set("-: ") for c in rows[1]):
                head, body = rows[0], rows[2:]
            else:
                head, body = None, rows
            blocks.append(("table", (head, body)))
        elif line.startswith("- ["):
            m = re.match(r"- \[([ xX])\]\s+(.*)", line)
            if m:
                done = m.group(1).lower() == "x"
                blocks.append(("task", (done, m.group(2))))
            i += 1
        elif line.startswith("- "):
            blocks.append(("li", line[2:]))
            i += 1
        else:
            buf = [line.strip()]
            i += 1
            while (i < len(lines) and lines[i].strip()
                   and not lines[i].startswith(("#", "|", "- [", "- ", ">"))):
                buf.append(lines[i].strip())
                i += 1
            blocks.append(("p", " ".join(buf)))
    return blocks


def render(blocks):
    done = sum(1 for kind, val in blocks if kind == "task" and val[0])
    total = sum(1 for kind, val in blocks if kind == "task")
    pct = (100.0 * done / total) if total else 0.0
    out = []
    table_index = 0
    for kind, val in blocks:
        if kind == "h1":
            out.append(f"<h1>{inline(val)}</h1>")
        elif kind == "h2":
            out.append(f"<h2>{inline(val)}</h2>")
        elif kind == "h3":
            out.append(f"<h3>{inline(val)}</h3>")
        elif kind == "note":
            out.append(f'<div class="note">{inline(val)}</div>')
        elif kind == "p":
            out.append(f"<p>{inline(val)}</p>")
        elif kind == "li":
            out.append(f"<li>{inline(val)}</li>")
        elif kind == "task":
            checked, text = val
            attr = " checked" if checked else ""
            out.append(f'<label class="task"><input type="checkbox"{attr} disabled>'
                       f"<span>{inline(text)}</span></label>")
        elif kind == "table":
            head, body = val
            table_index += 1
            h = ""
            if head:
                h = "<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead>"
            rows = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>"
                           for row in body)
            out.append(f'<div class="tablewrap"><table>{h}<tbody>{rows}</tbody></table></div>')
    return done, total, pct, "\n".join(out)


def main():
    blocks = parse(SRC.read_text(encoding="utf-8").splitlines())
    done, total, pct, body = render(blocks)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Todo — plant forms and grades</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1080px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
h2{{font:600 12px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.10em;
text-transform:uppercase;color:{MUTED};margin:30px 0 8px;border-top:1px solid {LINE};
padding-top:14px}}
h3{{font:600 15px/1.3 Georgia,serif;margin:20px 0 6px;color:{GOLD}}}
p{{margin:0 0 12px}}
.note{{background:{PAPER};border:1px solid {LINE};padding:12px 14px;margin:0 0 18px;
font:11px/1.5 ui-monospace,Menlo,monospace;color:{MUTED}}}
.task{{display:flex;gap:8px;align-items:flex-start;font:13px/1.45 ui-monospace,Menlo,monospace;
color:{INK};margin:0 0 7px}}
.task input{{margin-top:2px;accent-color:{GOLD}}}
.task input:checked + span{{color:#5f6f2f;text-decoration:line-through}}
li{{margin:0 0 6px}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f2ead8;padding:1px 4px}}
a{{color:{GOLD}}}
.progress{{background:{PAPER};border:1px solid {LINE};padding:14px 16px;margin:0 0 22px}}
.bar{{height:12px;background:#efe7d3;border:1px solid {LINE};margin:0 0 8px}}
.fill{{height:100%;background:{GOLD};width:{pct:.1f}%}}
.count{{font:11px ui-monospace,Menlo,monospace;color:{MUTED}}}
.tablewrap{{overflow-x:auto;margin:0 0 18px}}
table{{border-collapse:collapse;width:100%;font:11px/1.45 ui-monospace,Menlo,monospace}}
th,td{{border-bottom:1px solid {LINE};padding:6px 8px;text-align:left;vertical-align:top}}
th{{color:{MUTED};font:600 10px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.08em;text-transform:uppercase}}
tr:nth-child(even) td{{background:#fcf8ee}}
</style></head><body><main>
<h1>Todo</h1>
<div class="progress">
<div class="bar"><div class="fill"></div></div>
<div class="count">{done} / {total} done · {pct:.0f}% · read-only twin of
<a href="../TODO.md">TODO.md</a> · regenerate with <code>scripts/todo.py</code></div>
</div>
{body}
</main></body></html>
"""
    OUT.write_text(page, encoding="utf-8")
    # the draft label, the hub bar and the lattice pass, so a rebuild does not
    # drop them
    import stamp_draft
    stamp_draft.stamp_file(OUT)
    import hub
    hub.decorate_file(OUT.name)
    print(OUT)
    print(f"  {done}/{total} done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
