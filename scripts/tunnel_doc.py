"""Build docs/TUNNEL.html from docs/TUNNEL.md.

    .venv/bin/python scripts/tunnel_doc.py
    .venv/bin/python scripts/tunnel_doc.py --check

The Markdown is the source; the HTML twin carries the source SHA so the two
cannot drift. `--check` exits 1 when the twin is stale.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "docs" / "TUNNEL.md"
HTML = ROOT / "docs" / "TUNNEL.html"


def build(markdown_text: str) -> str:
    import markdown
    body = markdown.markdown(
        markdown_text, extensions=["tables", "toc", "fenced_code", "sane_lists"])
    sha = hashlib.sha1(markdown_text.encode("utf-8")).hexdigest()
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The tunnel | curve-lab</title>
<style>
:root{{--paper:#fffdf7;--ground:#f3eddf;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae;--gold:#c9a441;--blue:#1f5fa8}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);font:16px/1.6 Georgia,serif}}
main{{max-width:900px;margin:0 auto;padding:34px 22px 70px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:32px;line-height:1.15;margin:0 0 10px}}
h2{{font-size:21px;margin:28px 0 8px;padding-top:12px;border-top:1px solid var(--rule)}}
h3{{font-size:17px;margin:20px 0 6px}}
p{{margin:0 0 12px}}
a{{color:var(--blue)}}
strong{{color:var(--ink)}}
table{{border-collapse:collapse;width:100%;margin:10px 0 16px;font:13px/1.5 ui-monospace,Menlo,monospace}}
th,td{{border:1px solid var(--rule);padding:5px 8px;text-align:left;vertical-align:top}}
th{{color:var(--muted);font-weight:400}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
pre{{background:var(--paper);border:1px solid var(--rule);padding:12px 14px;overflow:auto}}
pre code{{background:none;padding:0}}
.footer{{margin-top:34px;padding-top:10px;border-top:1px solid var(--rule);font:11px/1.5 ui-monospace,Menlo,monospace;color:var(--muted)}}
</style></head><body><main>
<p class="eyebrow">curve-lab · the tunnel</p>
{body}
<p class="footer">Generated from <code>docs/TUNNEL.md</code> · source-sha: {sha} · do not edit this HTML by hand.</p>
</main></body></html>
"""


def main(argv: list[str]) -> int:
    source = MD.read_text(encoding="utf-8")
    import stamp_draft
    expected = stamp_draft.stamp_html(build(source))
    if "--check" in argv:
        if not HTML.exists():
            print(f"missing: {HTML.relative_to(ROOT)}")
            return 1
        if HTML.read_text(encoding="utf-8") != expected:
            print("stale: run .venv/bin/python scripts/tunnel_doc.py")
            return 1
        print("docs/TUNNEL.html is current")
        return 0
    HTML.write_text(expected, encoding="utf-8")
    print(f"wrote {HTML.relative_to(ROOT)} ({len(expected)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
