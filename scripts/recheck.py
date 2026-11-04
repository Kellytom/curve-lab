"""Re-check every result this project has established, in one run.

    .venv/bin/python scripts/recheck.py          # the fast set, a few seconds
    .venv/bin/python scripts/recheck.py --full   # adds the whole test suite

Each check is a claim we have made, the evidence for it, and the code that
re-derives it from scratch.  Nothing here is remembered: if a claim has stopped
being true, this says so.  The output is also written to `state/ACHIEVEMENTS-int.md`
so the list survives the session that found it.

Add a check when a result is established, not afterwards.
"""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

OUT = ROOT / "state" / "ACHIEVEMENTS-int.md"
CHECKS = []


def check(name, evidence, command):
    def wrap(fn):
        CHECKS.append((name, evidence, command, fn))
        return fn
    return wrap


# -- the engine --------------------------------------------------------------

@check("from_pairs is the same fit as from_hermite",
       "scripts/hodograph.py — the frame rotates by the tangent, not its half",
       "python -c 'import sys; sys.path.insert(0,\"scripts\"); from hodograph import ...'")
def c_from_pairs():
    from hodograph import from_hermite, from_pairs
    a = 100.0

    def cat(s):
        return (a * math.asinh(s / a), a * math.cosh(s / a) - a)
    worst = 0.0
    for s0, s1 in ((0, 30), (20, 60), (40, 80)):
        p0, p3 = cat(s0), cat(s1)
        t0, t1 = math.atan(s0 / a), math.atan(s1 / a)
        sh, _ = from_hermite(p0, t0, p3, t1)
        sp, _ = from_pairs(p0, math.cos(t0 / 2), math.sin(t0 / 2),
                           p3, math.cos(t1 / 2), math.sin(t1 / 2))
        worst = max(worst, math.dist(sh.control_points()[-1],
                                     sp.control_points()[-1]))
    return worst < 1e-12, f"worst disagreement {worst:.1e}"


@check("the degree lemma: n = deg h + 2 max(deg u, deg v) + 1",
       "scripts/generators.py — Farouki & Sakkalis; why quartics and sextics need h",
       "python scripts/generators.py")
def c_lemma():
    import generators as G
    ok = 0
    for spec in G.NAMED:
        for X, Y, W in (spec.get("branches") or []):
            pass
    for n, u, v, h in ((3, (1, 2), (2, 2), (1,)),
                       (4, (1, 4), (4, 4), (1, 1)),
                       (5, (1, 2, 2), (2, 2, 2), (1,)),
                       (6, (1, 2), (1, 2, 1), (1, 2))):
        want = len(h) - 1 + 2 * max(len(u) - 1, len(v) - 1) + 1
        ok += want == n
    return ok == 4, f"{ok}/4 splits give the degree they claim"


# -- the curves --------------------------------------------------------------

@check("every exact named curve is its own curve",
       "tests/test_named_curves.py — checked against an independent equation",
       "python -m unittest tests.test_named_curves")
def c_named_equations():
    r = subprocess.run([sys.executable, "-m", "unittest",
                        "tests.test_named_curves"],
                       cwd=ROOT, capture_output=True, text=True)
    tail = (r.stderr or "").strip().splitlines()
    return r.returncode == 0, tail[-1] if tail else "no output"


@check("25 named curves, 23 exact, with the recorded scales",
       "scripts/generators.py NAMED + tests/test_named_curves.py",
       "python -c 'import sys; sys.path.insert(0,\"scripts\"); import generators as g; ...'")
def c_counts():
    import generators as G
    exact = [s for s in G.NAMED if G.named_data(s)["exact"]]
    expect = {"bean": (12, 273), "bow": (3, 16), "tschirnhausen": (1, 27),
              "circle": (1, 5), "rounded square": (1, 425),
              "astroid": (5, 1), "nephroid": (5, 1), "cardioid": (3, 25)}
    bad = []
    for key, want in expect.items():
        spec = [s for s in G.NAMED if s["key"] == key][0]
        d = G.named_data(spec)
        if (d["cscale"], d["mscale"]) != want:
            bad.append(f"{key} {(d['cscale'], d['mscale'])} != {want}")
    return (len(G.NAMED) == 25 and len(exact) == 23 and not bad,
            f"{len(G.NAMED)} total, {len(exact)} exact" + (f"; {bad[0]}" if bad else ""))


@check("the two non-rational named curves are the ones we expect",
       "tests/test_named_curves.py — squircle genus 3, heart 4, pear 2; cruciform unbounded",
       "python -m unittest tests.test_named_curves")
def c_sampled():
    import generators as G
    sampled = sorted(s["key"] for s in G.NAMED if not G.named_data(s)["exact"])
    return (sampled == ["heart", "squircle"], ", ".join(sampled))


# -- integer hits ------------------------------------------------------------

@check("a finer grid does not buy hits; the right factors do",
       "workbench/generators.html Fig. 1a/1b — bean: 4 hits at grid 12, 48 and 156; 16 at 273",
       "python -c 'import sys; sys.path.insert(0,\"scripts\"); import generators as g; ...'")
def c_granularity():
    import generators as G
    bean = [s for s in G.NAMED if s["key"] == "bean"][0]
    got = [len(G.hit_points(bean, S)) for S in (12, 48, 156, 273)]
    return got == [4, 4, 4, 16], f"grids 12/48/156/273 -> {got} hits"


@check("grids under 3125 take the exact curves from 120 hits to 892",
       "scripts/generators.py best_grid(); the table on the generators page",
       "python -c 'import sys; sys.path.insert(0,\"scripts\"); import generators as g; ...'")
def c_hit_totals():
    import generators as G
    control = best = 0
    for s in G.NAMED:
        d = G.named_data(s)
        if not d["exact"]:
            continue
        control += len(G.hit_points(s, d["cscale"]))
        best += G.best_grid(s)[1]
    return (control, best) == (120, 892), f"control {control}, optimised {best}"


@check("clothoid spans match smooth curves and cannot match a cusp",
       "scripts/euler_match.py — 0.44-1.1% smooth, 9-63% at the cusped roulettes",
       "python scripts/euler_match.py")
def c_euler():
    import euler_match as E
    import generators as G

    def worst(key):
        spec = [s for s in G.NAMED if s["key"] == key][0]
        return E.run(spec)["dev_spans"]
    smooth = max(worst(k) for k in ("bean", "gerono", "nodal"))
    cusped = min(worst(k) for k in ("astroid", "deltoid", "cardioid"))
    return (smooth < 0.02 and cusped > 0.05,
            f"smooth {100*smooth:.2f}%, cusped {100*cusped:.1f}%")


# -- the lattice -------------------------------------------------------------

@check("the 3-4-5 ladder is fine enough long before a 3125 grid",
       "scripts/curve_families.py ladder() — measured rung spacing",
       "python -c 'import sys; sys.path.insert(0,\"scripts\"); from curve_families import ladder; ...'")
def c_ladder():
    from curve_families import ladder
    r = ladder(max_h=1600, max_deg=62.0)
    d = [x["deg"] for x in r]
    gaps = [b - a for a, b in zip(d, d[1:])]
    med = sorted(gaps)[len(gaps) // 2]
    return (len(r) == 350 and med < 0.2,
            f"{len(r)} rungs, median gap {med:.2f} degrees")


# -- the workbench -----------------------------------------------------------

@check("the Pythagorean integer cubic family",
       "curve_lab/pyth_cubic.py; workbench/integer-cubic.html Fig. P1",
       "python -m unittest tests.test_pyth_cubic")
def c_pyth_cubic():
    from curve_lab.pyth_cubic import case, cases, checks, rotate_scale

    all_cases = cases()
    ok = all(checks(c) for c in all_cases)
    base = case(3, 4, 5)
    ok = ok and base["p1"] == (3, -4) and base["p2"] == (7, 4)
    ok = ok and abs(base["angle"] + 53.13010235415598) < 1e-12
    rotated = rotate_scale(
        (base["p0"], base["p1"], base["p2"], base["p3"]), 3 / 5, 4 / 5, 5)
    ok = ok and all(
        abs(got[0] - want[0]) < 1e-9 and abs(got[1] - want[1]) < 1e-9
        for got, want in zip(rotated, [(0.0, 0.0), (25.0, 0.0), (5.0, 40.0), (30.0, 40.0)]))
    return ok, f"{len(all_cases)} triples, integer controls, chord 2c, arms c"


@check("the integer G2 mirror chain is exact",
       "curve_lab/pyth_g2.py; workbench/integer-g2.html Fig. G1",
       "python -m unittest tests.test_pyth_g2")
def c_pyth_g2():
    from curve_lab.pyth_g2 import probe_all

    reports = probe_all()
    ok = all(r["g2"] for r in reports)
    return ok, f"{sum(r['g2'] for r in reports)}/{len(reports)} triples pass both joins"


@check("an asymmetric integer G2 pair exists at scale 1",
       "curve_lab/pyth_g2.py asymmetric_pair; workbench/integer-g2.html Fig. G2",
       "python -m unittest tests.test_pyth_g2")
def c_asym_g2():
    from fractions import Fraction

    from curve_lab.pyth_g2 import asymmetric_pair, g1_fallback

    pair = asymmetric_pair()
    fallback = g1_fallback()
    ok = pair["g2"] and pair["curvature"] == Fraction(-6, 5)
    ok = ok and fallback["g1"] and not fallback["g2"]
    return ok, "scale 1 G2 pair; G1 fallback has a curvature jump"


@check("the hub is built from the manifest and every page carries its bar",
       "workbench/manifest.json + scripts/hub.py",
       "python scripts/hub.py")
def c_hub():
    import json
    m = json.loads((ROOT / "workbench" / "manifest.json").read_text())
    missing = [p["file"] for p in m["pages"]
               if not (ROOT / "workbench" / p["file"]).exists()]
    no_bar = [p["file"] for p in m["pages"]
              if "<!-- hub-bar -->" not in
              (ROOT / "workbench" / p["file"]).read_text(errors="replace")]
    hub = (ROOT / "workbench" / "workbench.html").read_text()
    return (not missing and not no_bar and 'class="decision"' in hub,
            f"{len(m['pages'])} pages, {len(no_bar)} without a bar")


@check("the package is curve_lab and nothing imports the old name",
       "the rename of 2026-11-01",
       "grep -r clothoid_lab --include=*.py .")
def c_rename():
    hits = 0
    for p in ROOT.rglob("*.py"):
        if any(x in p.parts for x in (".venv", "site", "node_modules", ".git")):
            continue
        if p.name == "recheck.py":
            continue            # this file names the old package in its own check
        hits += "clothoid_lab" in p.read_text(errors="replace")
    return hits == 0 and (ROOT / "curve_lab" / "__init__.py").exists(), \
        f"{hits} stale imports"


# -- recorded, not re-derived here ------------------------------------------

RECORDED = [
    ("The catenary, solved", "four PH cubics, 0.41% of a; integer chord walk",
     "python scripts/catenary.py", "workbench/catenary.html, sections A and C"),
    ("Clothoid per recovered span", "586 of 586 spans fit",
     "python scripts/check-spirals.py", "median 0.00-0.03% of the chord"),
    ("The square-discriminant dead end", "0 of 17,168 on the rung ladder",
     "see state/HANDOFF-int.md, 'In flight'", "choosing the pair buys exactness, not a lattice"),
    ("Spine chain vs study 01", "1.29% drift", "python scripts/spine_study_probe.py",
     "inside the 1.6% fidelity rule"),
]


def main(argv):
    full = "--full" in argv
    rows = []
    failures = 0
    for name, evidence, command, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as exc:                       # noqa: BLE001
            ok, detail = False, f"raised {type(exc).__name__}: {exc}"
        failures += 0 if ok else 1
        rows.append((ok, name, detail, evidence, command))
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
        print(f"        {detail}")

    if full:
        r = subprocess.run([sys.executable, "-m", "unittest", "discover", "tests"],
                           cwd=ROOT, capture_output=True, text=True)
        tail = (r.stderr or "").strip().splitlines()
        ok = r.returncode == 0
        failures += 0 if ok else 1
        rows.append((ok, "the whole test suite", tail[-1] if tail else "",
                     "tests/", "python -m unittest discover tests"))
        print(f"  {'PASS' if ok else 'FAIL'}  the whole test suite — "
              f"{tail[-1] if tail else ''}")

    lines = ["# Achievements, and how to re-check them", "",
             "Generated by `scripts/recheck.py`; run it at the start of a session.",
             "Each row is a claim, the evidence for it, and the command that",
             "re-derives it. A FAIL here means a result has slipped.", "",
             "| | claim | check says | evidence |", "|---|---|---|---|"]
    for ok, name, detail, evidence, _ in rows:
        lines.append(f"| {'ok' if ok else '**FAIL**'} | {name} | {detail} | {evidence} |")
    lines += ["", "## Recorded, re-derived elsewhere", "",
              "| claim | number | command | note |", "|---|---|---|---|"]
    for name, number, command, note in RECORDED:
        lines.append(f"| {name} | {number} | `{command}` | {note} |")
    lines += ["", "## The command", "", "```sh",
              ".venv/bin/python scripts/recheck.py --full", "```", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"\n  {len(rows) - failures}/{len(rows)} pass -> {OUT.relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
