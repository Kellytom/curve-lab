# SC-HANDOFF-int — the sidechat's handoff (DeepSeek2)

Written 2026-11-26, after building the Inkscape quintic extension ("do all the
work"). **Identity: the sidechat = `deep2` = DeepSeek2 — one agent.** DeepSeek1
is the other. The `s` files and git for this agent's own work are mine; the `f`
family is not.

1. **The extension conforms to the shared contract.** `curve-lab.quintic/1` from
   `workbench/quintic.schema.json`: envelope, `spans[].points` y up, `frame` with
   forward tangents, `joins[]` with measured residuals, `closed` + `winding` for a
   loop. My own numbers live in `<guide>-report.json`, not the contract file.
   Commit `93bbcc5d`, contract consolidated in `6f8ff405`.
2. **The importer exists**: `quintic_sheet.py`/`.inx` reads the sheet by uid and
   places a curve with its six points marked (`q6-trefoil-10` at scale 3: 32 cubics,
   0.0021 px).
3. **Theorems that are now checked, not asserted:**
   - a **proved** error bound (de Casteljau + exact elevation + convex hull); the
     fit accepts only when the bound is inside the tolerance (bound ≈ 1.6–2.1× the
     measured miss);
   - **Blender** as an independent evaluator: `scripts/check_blender_quintic.py`,
     0.000016 px on the parabola arch, 0.000051 px on the wild cage, so "6 points +
     order_u 6 + endpoint = exact quintic" is measured, not claimed;
   - **PH** decided in exact polynomial arithmetic: 0 of the sheet's 200 curves are
     PH, so none has an exact offset; the offset export says `exact: false`.
4. **Quality knobs that survived measurement:** parameter-corrected least squares
   (1 span on the wild stroke: 46.1 → 21.8 px), C1 seam smoothing (7–88° → 0.0° with
   a measured residual), the no-overshoot clamp (provable by the convex hull), the
   degeneracy test (68 of 200 sheet curves are below degree 5 and draw as one cubic).
5. **Four knot schemes lost to uniform-in-`t`**, each recorded with numbers in
   `state/PROBLEMS-quintic-guide-int.md` §7, §8, §11, §12: arc length, curvature
   cuts, adaptive placement, an inflection station. The reason is the same every
   time — the clamped C2 solve divides by the interval lengths.
6. **Tests:** 48 in `tests/test_quintic_math.py`; `tests/js/quintic-data.test.ts`
   (the shared one) 8/8; `scripts/check_quintic_contract.py` passes `--strict` on my
   exports and fails the sheet on three extra keys.
7. **Not done:** no push; the dialog has not been driven in the Inkscape GUI; the
   Blender/GeoGebra files have not been pasted into either application.

## 1b. Where the work stood before this block


1. **The extension is built, installed and tested.** Commit `e588a98d`.
   `inkscape/quintic-guide.inx` (three tabs: Points / Display / Export),
   `inkscape/quintic_guide.py` (glue), `inkscape/quintic_math.py` (all maths,
   inkex-free), `tests/test_quintic_math.py` (**32 tests, green**),
   `docs/QUINTIC-GUIDE.md`, `state/PROBLEMS-quintic-guide-int.md`.
2. **Installed** in
   `~/Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions/`
   and run headless from `/tmp` (outside the repo) to prove the import path:
   exports written, no error. Menu: **Extensions → Curve Lab → Quintic from
   Guide**.
3. **The three layers are the design** (operator, 2026-11-26): the drawn curve,
   the six-point curve, the quintic display. Both joins are measured and
   printed: drawn→quintic (max, RMS) and quintic→chain (max).
4. **Measured**, `scripts/quintic_report.py`:

   - one span on a long stroke: 26.0 px (freehand-like) to 46.1 px (wild);
   - four spans: 0.67 px and 3.41 px; six spans: 0.21 px and 0.52 px;
   - the best-fit mode roughly halves the miss at equal span count;
   - the cubic chain reaches 0.0015 px at 8 cubics (250 px cage) and 0.0002 px
     at 32 (400 px cage);
   - interpolation overshoot: 774 px (six even points) and 480 px (least
     squares) on the 400 px guide; the clamp stops it by construction.

5. **Over DeepSeek1's sheet** (`workbench/quintic-guides.json`, 200 cages): my
   control points round-trip exactly through the sidecar (0 error), and fitting
   the chain to 0.001 grid units needs 2–32 segments (median 16); worst 0.00098.
   **Their recorded `worstApproximationError` is 0.1182** — not a contradiction
   unless the segment count matches, but the two numbers should be reconciled
   before either document quotes the other.
6. **Not done:** no push (no internet approval this session); the operator has
   not yet run the dialog in the Inkscape GUI (headless runs only).

## 2. The operator's open asks, in order

1. **"do all the work"** — done for the extension, the reducer, spans, the
   clamp, markers, tabs and the exports; commit `e588a98d`.
2. **A sheet of input curves with 6 points** — DeepSeek1 made it
   (`workbench/quintic-guides.json` + `.svg`, 200 cages). Used as a cross-check
   above; a full pass through the dialog per curve is the next action.
3. **Blender / GeoGebra round trip with real curves** — the exports are written
   and tested as text; neither has been pasted into the applications yet.
4. **coreaudiod ~30 %** — still waits on a reboot the operator has refused.
5. **Adobe paperwork** (112 receipts, 12 MB shared folder, `com.adobe.*`
   plists) — offered, not done.

## 3. Environment facts a fresh session must not rediscover

- **`node` is not on the default PATH.** Node 24 is `~/node24/bin`; export it
  before any `node --test`, `npm`, or page check.
- **inkex 1.4.4 API:** `Path` has `to_absolute`, `to_superpath`, `transform`,
  `proxy_iterator` — it does **not** have `point`, `length` or `ilength`.
  `PathElement` has `composed_transform`, `path`, `to_path_element`.
  `inkex.Boolean` and `inkex.EffectExtension` exist. `to_superpath()` gives
  `[in, point, out]` triples; a cubic is `(A.point, A.out, B.in, B.point)`.
- **inkex writes nothing when the document is unchanged** (`has_changed`
  compares serialisations). A repeat run under an identical `> file.svg`
  redirect gives a 0-byte file; that is not a crash.
- **zsh does not word-split an unquoted variable.** `$opts` holding two flags
  arrives as one argument, and argparse hands the whole string to the first
  option. This made five mode comparisons print identical numbers.
- **The .inx needs `needs-live-preview="true"`** on `<effect>`; a tabbed dialog
  is `<param type="notebook"><page name=… gui-text=…>`.
- **Blender clamps `order_u` to the point count silently** — 6 points, order 6
  and `use_endpoint_u` together are the only exact quintic span.
- **A guided step that minimises a sampled objective finds the sampling error**
  (see `state/PROBLEMS-quintic-guide-int.md` §5, the rejected optimiser).
- **Mailbox:** the main session rotated `archive/notes/side-to-deep.md` while
  this session worked (`af0ad387`); the moved entries are in
  `archive/notes/mailbox-history.md`, verified by grep, nothing lost.

## 4. The one next action

**Close the three envelope keys, with the curve-lab side's agreement.**
`workbench/quintic-guides.json` carries `note`, `order` (a list of point names where
the schema wants the integer 6) and `worstApproximationError` at the top level, and
the schema is `additionalProperties: false`:

```sh
.venv/bin/python scripts/check_quintic_contract.py workbench/quintic-guides.json --strict
# FAIL ... keys the schema does not allow: note, order, worstApproximationError
```

The file and its generator belong to the curve-lab side, so the choice — drop the
keys, or make `order` the integer and move the names to `labels` — is theirs. Ask in
the mailbox; do not edit the file or the generator.

`Proves:` the strict check passes on the sheet, `tests/js/quintic-data.test.ts`
still passes, and no reader had to change.

**Question for DeepSeek1, not to be guessed:** is the sheet's
`worstApproximationError` measured at 2–3 cubics per curve, and by max distance
or by a station sample? The two documents should not quote different numbers for
the same curves.
