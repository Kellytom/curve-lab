"""Build docs/G3-showcase-docs.html from docs/G3-showcase-docs.md.

    .venv/bin/python scripts/g3_showcase_doc.py
    .venv/bin/python scripts/g3_showcase_doc.py --check

The Markdown is the source. This script:

- fills the counts block from the catalogue JSON and the showcase page;
- stamps the updated line with the date and commit;
- writes the HTML twin and embeds the Markdown SHA.

`--check` exits 1 when the twin or the counts are stale, so the document
cannot silently drift from the showcase.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import g3_showcase as S  # noqa: E402

MD = ROOT / "docs" / "G3-showcase-docs.md"
HTML = ROOT / "docs" / "G3-showcase-docs.html"


def _git(*args):
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True,
            stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _counts():
    cat = json.loads((ROOT / "workbench" / "g3-catalogue.json").read_text())
    rows = cat["curves"]
    hand = json.loads((ROOT / "workbench" / "g3-handover.json").read_text())
    page = (ROOT / "workbench" / "g3-showcase.html").read_text()
    figures = len(re.findall(r"<h[23]>Fig\.\s*\d+", page))
    complete = hand["counts"]["complete"]
    try:
        cusp_part = page.split('id="cusp-family"')[1]
        cusp_part = cusp_part.split('id="deviation"')[0]
        cusp = len(re.findall(r"<h3>Fig\.", cusp_part))
        dev_part = page.split('id="deviation"')[1]
        dev = len(re.findall(r"<h3>Fig\.", dev_part))
    except Exception:
        cusp = dev = "—"
    return {
        "candidates": len(rows),
        "admitted": sum(1 for r in rows if r.get("admitted")),
        "complete": complete,
        "smooth": hand["counts"]["smooth"],
        "declared": hand["counts"]["declared"],
        "cubic_native": sum(1 for r in rows
                            if r.get("native") == "cubic-native"),
        "figures": figures,
        "lead": figures - complete,
        "gallery": complete,
        "quintic": len(S.QUINTIC_KEYS),
        "cusp": cusp,
        "dev": dev,
    }


def _counts_table(c):
    rows = [
        ("candidates attempted", c["candidates"]),
        ("admitted", c["admitted"]),
        ("G3-complete", c["complete"]),
        ("smooth handover", c["smooth"]),
        ("complete with a declared feature", c["declared"]),
        ("cubic-native rows", c["cubic_native"]),
        ("figures on the showcase", c["figures"]),
        ("lead figures (cubic + quintic + cusp + deviation)", c["lead"]),
        ("gallery figures", c["gallery"]),
        ("quintic-required lead", c["quintic"]),
        ("cusp cards", c["cusp"]),
        ("deviation cards", c["dev"]),
    ]
    body = "\n".join(f"| {a} | {b} |" for a, b in rows)
    return "| | |\n|---|---|\n" + body


def _replace(md, name, body):
    pattern = re.compile(
        rf"<!-- {name}:start -->.*?<!-- {name}:end -->", re.S)
    return pattern.sub(
        f"<!-- {name}:start -->\n{body}\n<!-- {name}:end -->", md)


def _html(md):
    import markdown
    body = markdown.markdown(
        md, extensions=["tables", "toc", "fenced_code", "sane_lists"])
    sha = hashlib.sha1(md.encode("utf-8")).hexdigest()
    commit = _git("rev-parse", "--short", "HEAD")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>G3 showcase · how it is built</title>
<style>
:root{{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae;--gold:#c9a441;--blue:#1f5fa8}}
*{{box-sizing:border-box}}
body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.6 Georgia,serif}}
main{{max-width:980px;margin:0 auto;padding:34px 22px 70px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:34px;line-height:1.12;margin:0 0 10px}}
h2{{font-size:21px;margin:28px 0 8px;padding-top:12px;border-top:1px solid var(--rule)}}
h3{{font-size:17px;margin:20px 0 6px}}
p{{margin:0 0 12px}}
a{{color:var(--blue)}}
blockquote{{margin:0 0 16px;padding:10px 16px;border-left:4px solid var(--gold);background:#fffdf7;color:var(--muted)}}
table{{border-collapse:collapse;width:100%;margin:10px 0 16px;font:13px/1.5 ui-monospace,Menlo,monospace}}
th,td{{border:1px solid var(--rule);padding:5px 8px;text-align:left;vertical-align:top}}
th{{color:var(--muted);font-weight:400}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
pre{{background:#fffdf7;border:1px solid var(--rule);padding:12px 14px;overflow:auto}}
pre code{{background:none;padding:0}}
.live{{margin:0 0 18px;padding:10px 14px;background:#fffdf7;border-left:4px solid var(--gold);font:13px/1.6 ui-monospace,Menlo,monospace}}
.footer{{margin-top:34px;padding-top:10px;border-top:1px solid var(--rule);font:11px/1.5 ui-monospace,Menlo,monospace;color:var(--muted)}}
</style></head><body><main>
<p class="eyebrow">curve-lab · G3 showcase</p>
<p class="live"><a href="../workbench/g3-showcase.html">Open the live showcase</a> ·
<a href="../workbench/g3-notes.html">G3 notes</a> ·
<a href="../workbench/g3-handover.html">G3 handover</a> ·
<a href="../workbench/g3-diagnostics.html">tightest-span diagnostics</a></p>
{body}
<p class="footer">Generated from <code>docs/G3-showcase-docs.md</code> · source-sha: {sha} · commit: {commit or '—'} · {date.today().isoformat()} · do not edit this HTML by hand.</p>
</main></body></html>
"""


def _check():
    md = MD.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")
    sha = hashlib.sha1(md.encode("utf-8")).hexdigest()
    if f"source-sha: {sha}" not in html:
        print("stale: docs/G3-showcase-docs.html does not match the Markdown.\n"
              "Run .venv/bin/python scripts/g3_showcase_doc.py")
        return 1
    expected = _counts_table(_counts())
    if expected not in md:
        print("stale: the counts block does not match the catalogue/showcase.\n"
              "Run .venv/bin/python scripts/g3_showcase_doc.py")
        return 1
    return 0


def build():
    md = MD.read_text(encoding="utf-8")
    counts = _counts()
    updated = (f"Updated {date.today().isoformat()} · commit "
               f"`{_git('rev-parse', '--short', 'HEAD') or '—'}`")
    md = _replace(md, "updated", updated)
    md = _replace(md, "counts", _counts_table(counts))
    MD.write_text(md, encoding="utf-8")
    HTML.write_text(_html(md), encoding="utf-8")
    print(MD)
    print(HTML)
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(_check())
    sys.exit(build())
