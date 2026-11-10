"""The side list: curves whose Bézier representation is cubic.

    .venv/bin/python scripts/g3_cubic_native.py
    open workbench/g3-cubic-native.html

A quintic span is an exact elevation of a cubic when both the fourth and
fifth differences vanish:

    d4 = P0 - 4P1 + 6P2 - 4P3 + P4   (and the shifted P1...P5)
    d5 = P0 - 5P1 + 10P2 - 10P3 + 5P4 - P5

The catalogue's `native` field applies this test to every span of the fitted
representation. A four-point source span (the recovered LAC and the showcase
cubic lead) is cubic by construction. The page lists both, and separately the
rejected LAC source chains that are cubic but do not pass G3.
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import g3_showcase as S  # noqa: E402


def figure_map():
    """key -> (showcase figure number, notes anchor) from the generated page."""
    page = (ROOT / "workbench" / "g3-showcase.html").read_text(encoding="utf-8")
    out = {}
    pat = re.compile(
        r'<h2 id="fig-(\d+)"><a href="g3-notes\.html#([^"]+)">'
        r'Fig\. \d+ · (.*?)</a>', re.S)
    for m in pat.finditer(page):
        out[html.unescape(m.group(3))] = (int(m.group(1)), m.group(2))
    return out


def links(key, figs):
    fig = figs.get(key)
    if fig is None:
        return f'<a href="g3-notes.html#{S.note_id(key)}">notes</a>'
    return (f'<a href="g3-showcase.html#fig-{fig[0]}">Fig. {fig[0]}</a> · '
            f'<a href="g3-notes.html#{fig[1]}">notes</a>')


def build():
    data = json.loads((ROOT / "workbench" / "g3-catalogue.json").read_text())
    rows = data["curves"]
    figs = figure_map()

    exact = [r for r in rows if r.get("native") == "cubic-native"
             and r.get("source") != "lac"]
    lac_ok = [r for r in rows if r.get("native") == "cubic-native"
              and r.get("source") == "lac"]
    lac_bad = [r for r in rows if r.get("source_precision")
               and not r.get("admitted")]

    lead = []
    for p in S.PANELS:
        key = p["title"]
        if key in figs:
            lead.append((key, figs[key]))

    def rows_html(items, qc=False):
        body = []
        for r in items:
            q = (f'{r.get("quintic_content", 0):.1e}' if qc else "—")
            body.append(
                f'<tr><td>{r["key"]}</td><td class="num">{q}</td>'
                f'<td>{r.get("source")}</td><td>{links(r["key"], figs)}</td></tr>')
        return ("<table><tr><th>curve</th><th>d4/d5 residual</th><th>source</th>"
                "<th>where</th></tr>" + "".join(body) + "</table>")

    lead_html = "".join(
        f'<tr><td>{k}</td><td>{v[0]}</td>'
        f'<td><a href="g3-showcase.html#fig-{v[0]}">showcase</a> · '
        f'<a href="g3-notes.html#{v[1]}">notes</a></td></tr>'
        for k, v in lead)
    bad_html = "".join(
        f'<tr><td>{r["key"]}</td><td>{r.get("reason", "")}</td></tr>'
        for r in lac_bad)

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>G3 cubic-native · curves that collapse to cubics</title>
<style>{S.CSS}
.side-lede{{max-width:900px;color:var(--muted)}}
.num{{text-align:right}}</style></head><body><main>
<p class="eyebrow">curve-lab · G3 cubic-native</p>
<h1>Curves that collapse to cubics</h1>
<p class="side-lede">A quintic span is an exact elevation of a cubic when both
the fourth and fifth finite differences of its control polygon vanish:
<code>d4 = P0 − 4P1 + 6P2 − 4P3 + P4</code> (and the shifted one), and
<code>d5 = P0 − 5P1 + 10P2 − 10P3 + 5P4 − P5</code>. The residual is
<code>max(|d4|, |d5|) / chord</code>; a four-point source span is cubic by
construction. The <a href="g3-showcase.html">showcase</a> and the
<a href="g3-notes.html">notes</a> are the primary pages.</p>
<p class="small"><strong>{len(exact) + len(lac_ok) + len([k for k, _ in lead if not k.startswith("integer cubic")])}
distinct curves qualify</strong>: {len(exact)} exact quintic→cubic
elevations, the S44 LAC, and the four non-integer showcase cubic panels.
The two integer lead panels repeat integer rows already counted.</p>

<section class="panel">
<h2>Exact quintic→cubic elevations · {len(exact)}</h2>
<p class="small">These are the integer cubics. Their quintic spans are degree
elevations of cubics; the residual is float noise. {len(exact)} rows.</p>
{rows_html(exact, qc=True)}
</section>

<section class="panel">
<h2>Cubic by construction · {len(lac_ok) + len(lead)}</h2>
<p class="small">The recovered LAC Fig. 6 (S44) is four-point cubic source
spans. The showcase cubic lead is four-point by construction; the two integer
lead panels are the same curves as the integer rows above.</p>
<h3>S44 · the recovered LAC</h3>
{rows_html(lac_ok)}
<h3>The showcase cubic lead · {len(lead)}</h3>
<table><tr><th>panel</th><th>Fig.</th><th>where</th></tr>{lead_html}</table>
</section>

<section class="panel">
<h2>Cubic source, not G3-qualified · {len(lac_bad)}</h2>
<p class="small">These recovered LAC chains are four-point cubic source spans,
but their joins are only G1 (angle/curvature gaps); they are rejected by the
G3 gate and are not counted as qualified. They are listed so the source is not
confused with the representation.</p>
<table><tr><th>curve</th><th>reason</th></tr>{bad_html}</table>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "g3-cubic-native.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    build()
