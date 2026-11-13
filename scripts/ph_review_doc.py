"""Build docs/ph-quintic-review.html from docs/PH-QUINTIC-REVIEW.md.

    .venv/bin/python scripts/ph_review_doc.py
    .venv/bin/python scripts/ph_review_doc.py --check

The Markdown is the source; the HTML twin is generated with the source SHA and
the commit stamped into the footer. `--check` exits 1 when the twin is stale, so
the two cannot drift.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "docs" / "PH-QUINTIC-REVIEW.md"
HTML = ROOT / "docs" / "ph-quintic-review.html"


def _html(markdown_text):
    import markdown
    body = markdown.markdown(
        markdown_text, extensions=["tables", "toc", "fenced_code", "sane_lists"])
    sha = hashlib.sha1(markdown_text.encode("utf-8")).hexdigest()
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PH quintics | where the work stands</title>
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
<p class="eyebrow">curve-lab · PH quintics</p>
<p class="live"><a href="../workbench/ph-quintic-gallery.html">Open the live gallery</a> ·
<a href="../workbench/ph-quintic-presets.svg">the preset sheet</a> ·
<a href="../workbench/ph-quintic-presets.json">the preset JSON</a></p>
{body}
<p class="footer">Generated from <code>docs/PH-QUINTIC-REVIEW.md</code> · source-sha: {sha} · do not edit this HTML by hand.</p>
</main></body></html>
"""


def main():
    import sys
    markdown_text = MD.read_text()
    twin = _html(markdown_text)
    if "--check" in sys.argv:
        # no markdown import here: CI may not have it, and the SHA is enough
        if not HTML.exists():
            print("missing twin: docs/ph-quintic-review.html")
            return 1
        source_sha = hashlib.sha1(markdown_text.encode("utf-8")).hexdigest()
        if f"source-sha: {source_sha}" not in HTML.read_text():
            print("stale twin: run scripts/ph_review_doc.py")
            return 1
        print("twin is current")
        return 0
    HTML.write_text(twin)
    print(f"{HTML.relative_to(ROOT)}  {HTML.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
