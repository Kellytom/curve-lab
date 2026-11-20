#!/usr/bin/env python3
"""Render a page spec as an HTML twin, served by the app.

    .venv/bin/python scripts/spec_page.py                     # the grid page spec
    .venv/bin/python scripts/spec_page.py state/SPEC-prime-mover-int.md
    .venv/bin/python scripts/spec_page.py --all

The spec is the source. This writes the readable twin into `app/public/spec/`, so
it opens at `http://127.0.0.1:4321/spec/<name>.html` and uses the app's own
theme. Regenerate after any spec change; never edit the twin by hand.

The same pattern as `scripts/g3_showcase_doc.py`: markdown is the record, the
HTML is generated from it.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import hashlib
import markdown

ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "state"
OUT_DIR = ROOT / "app" / "public" / "spec"

TEMPLATE = """<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="spec-source-hash" content="{source_hash}">
<title>{title}</title>
<link rel="stylesheet" href="/vendor/pico.min.css">
<link rel="stylesheet" href="/vendor/curve-lab-theme.css">
<link rel="stylesheet" href="/vendor/app-shell.css">
<style>
  body {{ background: #fffdf7; color: #3b2d1c; }}
  main {{ max-width: 78ch; margin: 0 auto; padding: 28px 20px 80px; }}
  h1 {{ font-size: 1.5rem; margin-bottom: 4px; }}
  h2 {{ font-size: 1.1rem; margin-top: 30px; border-bottom: 1px solid #e6dcc6; padding-bottom: 4px; }}
  p, li {{ line-height: 1.6; }}
  code {{ font: 12.5px/1.5 ui-monospace, Menlo, monospace; background: #f7f1e3; padding: 1px 5px; border-radius: 2px; }}
  table {{ font: 12.5px/1.5 ui-monospace, Menlo, monospace; border-collapse: collapse; width: 100%; }}
  th, td {{ border-bottom: 1px solid #efe4c9; padding: 5px 8px; text-align: left; vertical-align: top; }}
  th {{ color: #8c6a21; font-weight: 400; }}
  blockquote {{ border-left: 3px solid #c9a441; margin-left: 0; padding-left: 14px; color: #5a4a32; }}
  .note {{ margin-top: 34px; padding-top: 12px; border-top: 1px solid #efe4c9; font-size: 12px; color: #8a7a5e; }}
  li input[type="checkbox"] {{ margin-right: 0.5rem; }}
  li:has(> input[type="checkbox"]) {{ list-style: none; }}
</style>
</head>
<body>
<main>
{body}
<p class="note">Generated from <code>{source}</code> by <code>scripts/spec_page.py</code>. Edit the markdown, not this page.</p>
</main>
</body>
</html>
"""


def slug(path: Path) -> str:
    """SPEC-prime-mover-int -> prime-mover; PROBLEMS-prime-mover-int -> prime-mover-problems."""
    name = path.stem
    problems = name.startswith("PROBLEMS-")
    name = re.sub(r"^(SPEC|PROBLEMS|NOTES)-", "", name)
    name = re.sub(r"-int$", "", name)
    return f"{name}-problems" if problems else name


def render(path: Path) -> Path:
    text = path.read_text(encoding="utf-8")
    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists", "toc"],
        output_format="html5",
    )
    # GitHub-style task items: `- [ ]` and `- [x]` become disabled checkboxes, so the
    # spec's status is visible on the page, not only in the markdown.
    body = re.sub(r"<li>\[ \] ", '<li><input type="checkbox" disabled> ', body)
    body = re.sub(r"<li>\[[xX]\] ", '<li><input type="checkbox" disabled checked> ', body)
    source_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    first_heading = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = re.sub(r"[`*]", "", first_heading.group(1)).strip() if first_heading else slug(path)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{slug(path)}.html"
    out.write_text(
        TEMPLATE.format(title=title, body=body, source=str(path.relative_to(ROOT)),
                        source_hash=source_hash),
        encoding="utf-8",
    )
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", nargs="?", default="state/SPEC-prime-mover-int.md")
    parser.add_argument("--all", action="store_true", help="every state/SPEC-*.md")
    args = parser.parse_args(argv)

    if args.all:
        paths = (sorted(SPEC_DIR.glob("SPEC-*.md"))
                 + sorted(SPEC_DIR.glob("PROBLEMS-*.md"))
                 + sorted(SPEC_DIR.glob("NOTES-*.md")))
    else:
        paths = [Path(args.spec)]
    for path in paths:
        full = path if path.is_absolute() else ROOT / path
        if not full.exists():
            raise SystemExit(f"no such spec: {path}")
        out = render(full)
        print(f"{full.relative_to(ROOT)} → {out.relative_to(ROOT)}  (http://127.0.0.1:4321/spec/{out.stem}.html)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
