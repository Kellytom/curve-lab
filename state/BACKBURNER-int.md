# Backburner

## B01 — Bounding parabolas for cubic/cubic intersection

**Status:** deferred 2026-11-03. Not part of the offset/ornament path.

**What it is:** a y-monotonic cubic is replaced by a sideways parabola
`x = ay² + by + c`, bracketed by two hybrid quadratics; the strip is used to
prove disjointness or drive subdivision for curve/curve intersection. It is a
boolean-path-ops primitive, not an offset construction.

**Artifact:** `workbench/bounding-parabola.html` — interactive ends, handles,
fitted parabola, hybrid quadratics, strip, and readout.

**Sources:**
- Levien, *Parallel curves of cubic Béziers*, cusp-finding aside.
- `raphlinus/raphlinus.github.io#79` — full design and cubic-scaling claim.
- `linebender/kurbo#258` — draft prototype, `examples/cubic_fun.rs`.
- `linebender/kurbo#277` / `#274` — boolean path ops and intersection traits.

**Why parked:**
- solves curve/curve intersection, not offset rails, endings or integer hits;
- prototype is draft/unmerged and needs y-monotonic preprocessing, cusp
  handling, Fréchet fallbacks and robust root solving;
- current curve-lab work does not need a new boolean/intersection subsystem.

**Revisit when:** we need robust boolean path operations, curve/curve crossing
classification, or a cusp-bracketing primitive that cannot be handled by the
existing clearance/intersection code.

## B02 — Euler spiral to cubic Bézier via endpoint parabolas

**Status:** candidate fitted option, 2026-11-03; not implemented.

**What it is:** for an Euler spiral segment, place a sideways parabola at each
endpoint of the chord. With the chord normalized to `(0,0)–(1,0)`, the left
parabola is `x = 1/3 - (3/4)y²`; the right is `x = 2/3 + (3/4)y²`. The cubic
control points are the intersections of those parabolas with the endpoint
tangent rays. The vertex is 1/3 along the chord and the endpoint arms open to
±2/3 orthogonally.

**Why it matters:** this is a **cubic Bézier fit to an Euler spiral segment**,
not an Euler spiral made of parabolas, and not the bounding/intersection
parabola. It is simple, fast, matches the symmetric circular-arc cubic, and
scales as `O(n^5)` — better than Hermite `O(n^4)`, below the optimal `O(n^6)`.
It is a plausible fitted option for the cubic seam; the p-triple polygon and
rational rails remain the exact route.

**Source:** Raph Levien, *Cleaner parallel curves with Euler spirals*,
2021-02-19, section “Euler spirals to cubic Béziers”:
https://raphlinus.github.io/curves/2021/02/19/parallel-curves.html

## B03 — machine refresh: swap growth forces a reboot

**Status:** parked 2026-11-04. Machine work, not curve work. It does not block
the n=2 chain.

**Symptom:** swap climbs toward 6 GB with nothing in Activity Monitor, so the
working rhythm becomes `/fhandoff` → quit → reboot → `/focus` → `/fhandon`.
Compaction does not help, because compaction is model context, not memory.

**Measure before blaming swap** (one call):

```sh
sysctl vm.swapusage
memory_pressure | tail -3
ps -Ao pid,rss,comm | sort -k2 -nr | head -15
```

**What the numbers mean:**
- `used` high while `ps` shows no live owner → the dynamic pager is holding
  already-allocated files in `/private/var/vm/swapfile*`. Those are released
  **only at boot**; there is no supported runtime shrink.
- `free percentage` high but `Pageouts` climbing → swap was written earlier by
  something that has since exited; this is residue, not live pressure.
- `Pageouts` low and `used` still high → the owner is still resident; find it in
  `ps` and kill that PID, not the machine.

**What actually feeds it here:** long-lived `opencode` sessions (node), Google
Chrome renderer processes, `mkdocs serve` autoreloading over `node_modules`,
and per-screenshot Chromium launches. On 2026-11-04 the footprint was two
opencode processes (~700 MB RSS) and ~10 Chrome renderers (~1.5 GB); there were
**no** orphaned Playwright browsers, because `scripts/shot.mjs` launches and
closes one per shot.

**Measured baseline, 2026-11-04 (the machine is 8 GB, not 16):**

| reading | value |
|---|---|
| `PhysMem` | 8148M used, **43M unused** |
| wired | 1654M |
| compressor | 734,197 pages = **3.0 GB occupied**, 7.6 GB of logical pages stored |
| swap | 1587M used of 3072M |
| pressure level | **2 (warning)** |
| disk | 92% full, 38 GiB free |

At that reading the machine was genuinely full, not sticky. Two corrections that
matter when reading Activity Monitor: the **"1.5 GB" is Swap Used**, not memory
used — they are the same number to one decimal and are routinely confused — and
**compressed memory is live**, held by processes still running, so it does not
drain when the browser closes. On 8 GB, one browser session plus two opencode
processes plus mkdocs is more than the machine has.

**What to do:** quit the session at a handoff seam (the tree is committed and
`next-fhandoff-int.md` carries the finish line, so nothing is lost); stop
`mkdocs serve` between checks; do not keep a browser open "for screenshots".
Reboot only when `vm.swapusage used` is large *and* `ps` has no owner.

**What not to do:** do not disable SIP or unload `com.apple.dynamic_pager` to
force a shrink, and do not read swap as a leak — it is allocation history.
`sudo purge` clears file cache and does nothing for swap.

**Revisit when:** a second consecutive reboot shows the same 6 GB with the same
`ps` output — that is a leak worth bisecting by process, not a pager artefact.
