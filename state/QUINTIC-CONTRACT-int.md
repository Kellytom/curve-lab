# QUINTIC-CONTRACT-int — the extension's side of the shared record

The authority is **`workbench/quintic.schema.json`** (`curve-lab.quintic/1`), written
and owned by the curve-lab side, and `state/RESPONSIBILITIES-int.md` §7 says who owns
what. This file is only what the **extension** does with it, so neither side has to
read the other's code to find out.

## 1. The split, in one line each

| area | owner |
|---|---|
| `scripts/quintic-guides.ts`, `workbench/quintic-guides*.json/.svg` | DeepSeek1 — the only writer of the data file |
| `workbench/quintic.schema.json`, `tests/js/quintic-data.test.ts` | shared — a meaning change is a format bump |
| `inkscape/quintic_*.py`, `inkscape/*.inx` | DeepSeek2 (me) — reads the record, never writes the data file |
| `scripts/quintic_contract.py` | me — the reader-side check, Python, no Node needed |

## 2. What the extension writes

`<guide>-quintic.json`, exactly the schema's shape:
`format`, `degree: 5`, `createdBy`, `axes {x, y, units, extent}`, `count`, `curves[]`.
A curve has `uid, group, family, name, closed, winding, fitError, selfCrossings,
spans[], joins[]`. A span has `uid, kind: "quintic", points[6], weights: null, frame`.
`frame.start.tangent = P1 − P0` and `frame.end.tangent = P5 − P4`, both forward.

**`fitError` means the drawn→quintic miss** for a curve taken off a stroke, and `0`
when the six points came from the sheet and are therefore exact.

`joins` is populated only when the seams were smoothed: continuity `G1` with a
measured `residual {position, tangentDegrees, kappa, rate}`. An unsmoothed seam is
C0 and the schema has no word for it, so it emits **no join** rather than a false
`G1`.

`<guide>-report.json` carries my own numbers — the proved bound, PH, cusps, true
degree, overshoot, segment counts — and is deliberately **not** in the contract
shape. The checker skips it by name.

## 3. What the extension reads

`inkscape/quintic_sheet.py` (`Extensions → Curve Lab → Quintic sheet: place a curve`)
reads `workbench/quintic-guides.json`, finds one curve by uid, and draws its spans
plus the six points as marks on every span. That is the whole input path: the
extension never invents a curve, it draws one the other side made.

## 4. The one flip

The record is **y up**; an Inkscape document is **y down**. `quintic_sheet.to_svg`
is the only flip on the reading side, and `quintic_math.to_y_up` is the only flip on
the writing side. Each is called exactly once. A y flipped twice is the classic
fault in this area, and both files say so at the function.

## 5. The check

```sh
.venv/bin/python scripts/quintic_contract.py workbench/quintic-guides.json --extent-must-follow
.venv/bin/python scripts/quintic_contract.py /tmp/export/*-quintic.json --extent-must-follow
node --test tests/js/quintic-data.test.ts
```

The first two are the reader-side check (types, required keys, no extra keys, forward
tangents present, a join's residual present and non-negative, `axes.extent` covering
the points). The third is the shared test the other side wrote.

## 6. Two known differences, stated rather than hidden

1. **`workbench/quintic-guides.json` has three top-level keys the schema forbids**:
   `note`, `order` (a list of point names, where the schema wants the integer 6) and
   `worstApproximationError`. My checker reports them; their JS test passes because it
   checks the curve and span shape, not the envelope. Either the schema gains the keys
   or the generator drops them — a change of meaning is a format bump, so this is a
   decision for the curve-lab side, not an edit I make.
2. **A fitted record is not on the integer grid.** The sheet's points are integers
   because they are generated; six points fitted to a drawn stroke are floats, and
   the schema allows `number`. `fitError` is the field that says how far the fit is
   from the stroke, and the report file carries the rest.

## 7. On a format bump

`curve-lab.quintic/2` means: schema, generator, `tests/js/quintic-data.test.ts`, this
extension and `scripts/quintic_contract.py` change in **one** commit, and only one of
us makes that commit. Until then, a new field is additive and the other side is told
in the mailbox in one line.
