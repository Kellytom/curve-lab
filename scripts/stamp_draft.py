"""Put the draft label on every outward-facing page.

    .venv/bin/python scripts/stamp_draft.py          # stamp the files
    .venv/bin/python scripts/stamp_draft.py --check  # exit 1 if one is missing

The label is one visible line, not a redesign:

- HTML: a small fixed badge in the corner, and the page title gains
  `: draft A`.
- Markdown: a blockquote line under the first heading.

The edit is idempotent. `scripts/build-pages.py` runs it at the end, and the
suite runs `--check`, so a regenerated page that dropped the label is a red
test rather than a quiet omission.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BADGE = (
    '<div class="draft-a" style="position:fixed;right:.75rem;bottom:.75rem;'
    'z-index:9999;background:#1b1b1b;color:#fff;font:12px/1.4 system-ui,'
    'sans-serif;padding:.35rem .6rem;border-radius:.25rem;opacity:.9">'
    'draft A</div>'
)
MD_LINE = "> **draft A** — a working draft, not a final text.\n"

# Outward-facing files only. Internal notes, tests, scripts and the private
# pointer files are deliberately absent.
def targets() -> list[Path]:
    files: list[Path] = []
    files += [p for p in sorted((ROOT / "workbench").glob("*.html"))
              if p.name != "tabs.html"]  # the local launcher, not an outward page
    files += sorted((ROOT / "book").glob("*.html"))
    files += sorted((ROOT / "app" / "src" / "pages").glob("*.astro"))
    files += sorted((ROOT / "curves").glob("*/notes.md"))
    for name in ("README.md", "SPEC.md", "goals.md"):
        path = ROOT / name
        if path.exists():
            files.append(path)
    return [p for p in files if p.is_file()]


def carries_label(text: str) -> bool:
    """A page that renders the shared header carries the label from there."""
    return 'class="draft-a"' in text or "<AppNav" in text or "<BaseLayout" in text


def stamp_html(text: str) -> str:
    if 'class="draft-a"' not in text:
        body = re.search(r"<body[^>]*>", text, re.IGNORECASE)
        if body:
            text = text[: body.end()] + "\n" + BADGE + text[body.end():]
    if "draft A</title>" not in text:
        text = re.sub(
            r"<title>(.*?)</title>",
            lambda m: f"<title>{m.group(1)}: draft A</title>"
            if "draft A" not in m.group(1)
            else m.group(0),
            text,
            count=1,
            flags=re.IGNORECASE | re.DOTALL,
        )
    return text


def stamp_md(text: str) -> str:
    if MD_LINE.strip() in text:
        return text
    heading = re.search(r"^# .*\n", text, re.MULTILINE)
    if not heading:
        return text
    at = heading.end()
    # keep one blank line after the heading
    if text[at: at + 1] == "\n":
        return text[:at + 1] + MD_LINE + text[at + 1:]
    return text[:at] + "\n" + MD_LINE + text[at:]


def stamp_file(path: str | Path) -> bool:
    """Stamp one file in place. Generators call this after writing a page, so a
    rebuild alone cannot drop the label."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    new = stamp_html(text) if path.suffix in (".html", ".astro") else stamp_md(text)
    if new == text:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def main(argv: list[str]) -> int:
    check = "--check" in argv
    missing = []
    changed = 0
    for path in targets():
        text = path.read_text(encoding="utf-8")
        new = stamp_html(text) if path.suffix in (".html", ".astro") else stamp_md(text)
        if new == text:
            continue
        if check and path.suffix in (".html", ".astro") and carries_label(text):
            continue
        if check:
            missing.append(path.relative_to(ROOT))
            continue
        path.write_text(new, encoding="utf-8")
        changed += 1
    if check:
        for name in missing:
            print(f"missing draft A: {name}")
        print(f"{len(missing)} of {len(targets())} pages lack the label")
        return 1 if missing else 0
    print(f"stamped {changed} of {len(targets())} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
