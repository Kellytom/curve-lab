"""The gate tiers: strict G3, source precision, and the near-G3 band.

    .venv/bin/python scripts/g3_gate.py
    open workbench/g3-gate.html

The strict G3 count is unchanged. This page shows what a relaxation buys and
what it does not: the near-G3 band admits the recovered LAC chains whose joins
have a small tangent/curvature gap, but those rows are **not** counted as G3.
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

TIERS = [
    ("exact", 1e-9, 1e-6,
     "floating-point noise for exact constructions"),
    ("source-precision", 1e-5, 1e-3,
     "integer-rounded source; still no visible corner"),
    ("near-G3", 5e-4, 0.2,
     "a declared small corner; convenient for a drawing, not G3"),
]


def _spans(fig):
    spans = []
    for sp in fig["spines"][0]["spans"]:
        spans.append([
            (sp["p0"][0], -sp["p0"][1]),
            (sp["c1"][0], -sp["c1"][1]),
            (sp["c2"][0], -sp["c2"][1]),
            (sp["p3"][0], -sp["p3"][1]),
        ])
    return spans


def _classify(spans):
    measured = {}
    for name, tol, angle, _why in TIERS:
        rows = S.gate(spans, tol=tol, angle_tol=angle)
        measured[name] = rows
    worst = {
        "angle": max(r["angle"] for r in measured["near-G3"]),
        "dk": max(r["dk"] for r in measured["near-G3"]),
        "dks": max(r["dks"] for r in measured["near-G3"]),
    }
    for name, _tol, _angle, _why in TIERS:
        if all(r["pass"] for r in measured[name]):
            return name, worst
    return "fail", worst


def _source_anchors():
    h = (ROOT / "workbench" / "showcase-notes.html").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(
            r'<section class="note" id="([^"]+)">(.*?)</section>', h, re.S):
        t = re.search(r"<h2>(.*?)</h2>", m.group(2), re.S)
        if not t:
            continue
        sm = re.search(r"(S\d+)\s*·", t.group(1))
        if sm:
            out.setdefault(sm.group(1), m.group(1))
    return out


def _g3_map():
    h = (ROOT / "workbench" / "g3-showcase.html").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(
            r'<h2 id="fig-(\d+)"><a href="g3-notes\.html#([^"]+)">'
            r'Fig\. \d+ · (.*?)</a>', h, re.S):
        out[html.unescape(m.group(3))] = (int(m.group(1)), m.group(2))
    return out


def _links(key, src, g3):
    parts = []
    sm = re.match(r"(S\d+)", key)
    if sm and sm.group(1) in src:
        parts.append(f'<a href="showcase-notes.html#{src[sm.group(1)]}">'
                     f'illustration</a>')
    if key in g3:
        parts.append(f'<a href="g3-showcase.html#fig-{g3[key][0]}">G3 figure</a>')
        parts.append(f'<a href="g3-notes.html#{g3[key][1]}">notes</a>')
    return " · ".join(parts) or "—"


def build():
    cat = json.loads((ROOT / "workbench" / "g3-catalogue.json").read_text())
    rows = cat["curves"]
    admitted = [r for r in rows if r.get("admitted")]
    exact = [r for r in admitted if not r.get("source_precision")]
    source = [r for r in admitted if r.get("source_precision")]

    lac = json.loads((ROOT / "workbench" / "spirals" / "lac.json").read_text())
    near, fail = [], []
    for fig in lac["figures"]:
        num = int(fig["figure"].split()[-1])
        key = f"S{38 + num} · {fig['figure']} · {fig['title']}"
        cls, worst = _classify(_spans(fig))
        row = {"key": key, "class": cls, **worst}
        if cls == "near-G3":
            near.append(row)
        elif cls == "fail":
            fail.append(row)

    tier_rows = "".join(
        f"<tr><td>{name}</td><td>{tol:.0e}</td><td>{angle:g}°</td>"
        f"<td>{why}</td></tr>" for name, tol, angle, why in TIERS)
    src = _source_anchors()
    g3 = _g3_map()
    near_rows = "".join(
        f"<tr><td>{r['key']}</td><td>{r['angle']:.3f}°</td>"
        f"<td>{r['dk']:.1e}</td><td>{r['dks']:.1e}</td>"
        f"<td>{_links(r['key'], src, g3)}</td></tr>" for r in near)
    source_rows = "".join(
        f"<tr><td>{r['key']}</td><td>{r['g3']:.1e}</td>"
        f"<td>{_links(r['key'], src, g3)}</td></tr>" for r in source)
    fail_rows = "".join(
        f"<tr><td>{r['key']}</td><td>{r['angle']:.3f}°</td>"
        f"<td>{r['dk']:.1e}</td><td>{r['dks']:.1e}</td>"
        f"<td>{_links(r['key'], src, g3)}</td></tr>" for r in fail)

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>G3 gate tiers · how far a relaxation goes</title>
<style>{S.CSS}
.lede{{max-width:920px;color:var(--muted)}}</style></head><body><main>
<p class="eyebrow">curve-lab · gate tiers</p>
<h1>G3 gate tiers · how far a relaxation goes</h1>
<p class="lede">The strict G3 count is unchanged: <strong>{len(admitted)}</strong>
admitted. This page shows the bands above and below that line. The
<strong>near-G3</strong> band adds {len(near)} recovered LAC chains whose joins
have a small tangent/curvature gap; they are <strong>not counted as G3</strong>.
The point is to see the trade, not to move the claim.</p>

<section class="panel">
<h2>The tiers</h2>
<table><tr><th>tier</th><th>|Δp|, |Δκ|, |Δ(dκ/ds)|</th><th>angle</th>
<th>meaning</th></tr>{tier_rows}</table>
<p class="small">The strict <strong>{len(exact)}</strong> rows are exact
(the solved joins are below 1e-9). <strong>{len(source)}</strong> admitted row is
source-precision (S44). <strong>{len(near)}</strong> LAC chains are near-G3;
<strong>{len(fail)}</strong> fail even the near band.</p>
</section>

<section class="panel">
<h2>Admitted by strict G3 · {len(admitted)}</h2>
<p class="small">Exact: {len(exact)} · source-precision: {len(source)}.
The latter is the recovered LAC Fig. 6:</p>
<table><tr><th>curve</th><th>worst Δ(dκ/ds)</th><th>where</th></tr>{source_rows}</table>
<p class="small">All 154 admitted curves are in the
<a href="g3-showcase.html#every-curve">showcase gallery</a> and the
<a href="g3-notes.html">notes</a>.</p>
</section>

<section class="panel">
<h2>Near-G3, not G3 · {len(near)}</h2>
<p class="small">These are cubic source spans; their joins have a tangent gap
of a few hundredths of a degree and a curvature gap up to 1.3e-4. The eye may
accept them in a drawing; the page does not call them G3. Accepting them would
take the catalogue from {len(admitted)} to {len(admitted) + len(near)}.</p>
<table><tr><th>curve</th><th>worst angle</th><th>worst |Δκ|</th>
<th>worst |Δ(dκ/ds)|</th><th>illustration</th></tr>{near_rows}</table>
</section>

<section class="panel">
<h2>Fail even near-G3 · {len(fail)}</h2>
<table><tr><th>curve</th><th>worst angle</th><th>worst |Δκ|</th>
<th>worst |Δ(dκ/ds)|</th><th>illustration</th></tr>{fail_rows}</table>
<p class="small">Back to the <a href="g3-showcase.html">showcase</a> ·
<a href="g3-notes.html">notes</a> ·
<a href="g3-cubic-native.html">cubic-native side list</a>.</p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "g3-gate.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    build()
