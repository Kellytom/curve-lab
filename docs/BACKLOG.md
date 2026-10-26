# Backlog — the next few hours

One item at a time. Each item is one change, one verify, one commit. Do not
bundle. Finish an item, mark it `[x]`, update `docs/HANDOFF.md`, commit, and
stop unless the operator says to continue down the list.

**Markers:** `[ ]` next, `[>]` in progress, `[x]` done, `[~]` blocked on the
operator. A `[~]` is never picked.

**Rules**

- Keep the public URL private; auth/rate limiting stays deferred.
- Never touch `out/play-template.svg`.
- Do not change `vendor/` or the cap JSON; caps are baked in.
- If an item needs a taste or product decision, write the question under the
  item and stop instead of guessing.
- If a verify fails twice for the same reason, stop and write the reason.
- Deploy only at the milestones marked **deploy**; the URL is public.
- Tests must stay green: `.venv/bin/python -m unittest discover tests` (96 now).

**Commands**

```sh
.venv/bin/python -m unittest discover tests
.venv/bin/python web/server.py          # local, port 8000
.venv/bin/python scripts/check-parity.py
node scripts/check-web.mjs              # layout/UI gate, added in M1
```

---

## [>] M0 — Finish the image split

The engine base `clothoid-engine:2026-10-26` is built and pushed. The thin app
`Dockerfile`, `engine/Dockerfile`, `cloudbuild.engine.yaml`, and both
`.gcloudignore` files are in the working tree, uncommitted.

1. Deploy the thin app with the normal command and time it.
2. Confirm the remote page and `/api/render` still work; run parity.
3. Commit the split; update `docs/HANDOFF.md` with the deploy time and revision.
4. Success: a second app-only deploy (one CSS byte) finishes in under a minute.

**Deploy:** yes. **Verify:** parity + remote HTTP 200 + timed deploy.
**Commit:** `build: split the engine base from the thin app image`

---

## [ ] M1 — One headless layout gate

The phone overflow escaped 96 tests because none of them looked at layout. Add
a repeatable gate.

- `scripts/check-web.mjs`: Node 22 built-ins only (fetch + WebSocket), launch
  Chrome `--headless=old` with a temp profile and CDP, measure at 320/360/390.
- Fail if `document.documentElement.scrollWidth > innerWidth + 1`, or if a
  control's right edge passes the viewport.
- Check the page after load, after selecting `cap-pt-9`, and after a width error.
- Optional `--url` for the remote and `--shot` for a PNG.

**Verify:** `node scripts/check-web.mjs` on the local server.
**Commit:** `test(web): add a headless layout gate`

---

## [ ] M2 — Preset parameters in the API

The presets are already parametric functions; the web layer throws the
parameters away.

- `clothoid_lab/presets.py`: add a `PARAMS` schema per preset with `min`, `max`,
  `step`, `default`, `label`, `unit` for `length`, `degrees`, `straight`,
  `arc_share` as each applies.
- `get(name, **params)` validates against the schema and regenerates.
- `/api/presets` returns names plus the schema; `/api/preset` accepts query
  parameters and rejects out-of-range values with 400.
- Keep the old response shape working for the current page until M3.
- Add tests: defaults unchanged, a parameter changes the segment count/length,
  out-of-range is rejected.

**Verify:** tests; `curl` a parameterised preset.
**Commit:** `feat(web): expose preset parameters`

---

## [ ] M3 — Sliders for one family at a time

- `web/static/app.js`: when a preset is selected, render one range input per
  schema parameter under the Preset/Cap row, with a live value readout.
- Debounce 150 ms, fetch `/api/preset?name=…&…`, update the JSON editor and
  re-render. A Reset button restores defaults. Hide the panel for caps.
- `index.html`/`style.css`: a compact panel that fits 360 px.
- Do not add sliders to raw `segments[]`; only the family parameters.
- Extend `check-web.mjs` to assert the panel appears and that moving a slider
  changes the rendered SVG.

**Deploy:** yes. **Verify:** `node scripts/check-web.mjs` + tests + screenshot.
**Commit:** `feat(web): add preset sliders`

---

## [ ] M4 — Remember and share a design

- Save `{design, width, page}` to `localStorage` after each successful render;
  restore it on boot instead of cap-14.
- Add **Copy link**: base64url JSON in `#d=…`; on load, decode, validate, and
  render. Keep it under ~8 KB; fall back to download for larger designs.
- A **Reset** clears storage and returns to the default cap.
- The JSON editor stays the source of truth; persistence is a wrapper.

**Verify:** extend `check-web.mjs` to reload and confirm the design survived,
and to open a `#d=` link and confirm the same status.
**Commit:** `feat(web): remember and share designs`

---

## [ ] M5 — Phone ergonomics pass

- 16 px inputs on phone widths so focus does not zoom.
- 44 px minimum tap targets; sliders with a visible value.
- Put `design.json` behind a `<details>` on phones; keep it open on desktop.
- Preview before the report; report collapsed by default on phones.
- Safe-area padding at the bottom; no horizontal overflow at 320/360/390.

**Deploy:** yes. **Verify:** `node scripts/check-web.mjs --width 320,360,390`
and a real Samsung look.
**Commit:** `feat(web): tune the phone editor`

---

## [ ] M6 — Join and fit status in the page

The report is engine-speak; surface the verdict.

- Use `info.chain` / `info.fit` to show badges: segments, cubics, G1/G2, corner
  count, worst fit against tolerance.
- Keep the raw report below; link the two.
- No new geometry; read what `cli.render` already returns.

**Verify:** tests + `check-web.mjs` asserts the badge text for cap-14 and a
deliberate corner design.
**Commit:** `feat(web): show join and fit status`

---

## [ ] M7 — Sync the durable docs and deploy the milestone

- `docs/HANDOVER.md` (+ HTML mirror): the image split, sliders, persistence,
  the layout gate, and the new deploy loop.
- `docs/HANDOFF.md`: current truth and the next move.
- Deploy, run parity, and record the revision and the app-deploy time.

**Deploy:** yes. **Verify:** tests + parity + `check-web.mjs` local and remote.
**Commit:** `docs: sync the handover after the editor pass`

---

## [~] Auth and rate limiting

Deferred by operator decision. Do not start. Keep the URL private until this
is lifted.

## [~] Parametric caps

Class I/II caps are fixed JSON. Slider parameters for caps need a product
decision about which family is worth parameterising; do not invent one.
