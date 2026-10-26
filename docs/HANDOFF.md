# clothoid-lab handoff

**Updated:** 2026-10-26  
**Use `/fhandon` to resume, `/fhandoff` to refresh this file.** The commands are
project-scoped: open OpenCode in this repository to use them. They are not
global and do not appear in `grid-8` or `ornaments`.

## Objective

Turn clothoid-lab into a usable design tool with exact clothoid geometry, a
200 × 250 mm sheet, +y up, and class I/II cap families. A local MVP and a public
remote MVP now exist.

## Current state

- **Local:** `http://127.0.0.1:8000/` — Python stdlib server plus the macOS
  `.dylib`. Start with `.venv/bin/python web/server.py`. HTTP 200 at
  2026-10-26 11:15 UTC. Auth is unset locally, so the loopback server stays
  open; the public deployment requires the token.
- **Remote:** `https://clothoid-web-ba5ahdu6bq-uc.a.run.app` — Cloud Run,
  project `clothoid-lab-1792967460`, region `us-central1`, service
  `clothoid-web`, revision `clothoid-web-00006-zrx`. HTTP **401 without the
  token, 200 with it** at 2026-10-26 11:13 UTC; a thin app deploy takes ~30 s.
- **Access:** HTTP Basic with a shared token; every route except `/health`.
  Token in Secret Manager `clothoid-token`, local copy
  `~/.config/clothoid-lab/token` (outside the repo). `/api/render` is limited to
  60/min, burst 20, per client address; excess is 429 with `Retry-After`.
- **Remote limits:** min `0`, max `1`, 1 vCPU, 512 MiB, concurrency `2`,
  60 s timeout. The Cloud Run IAM policy still allows unauthenticated ingress;
  the application token is the gate.
- **Build split (done):** engine base `clothoid-engine:2026-10-26` built in
  6m43s and pushed; the thin app deploy took 30 s (revision
  `clothoid-web-00004-nwx`, commit `eb67f4c`). App deploys now upload ~100
  files and skip the C++ compiler.
- **Budget:** `$1/month` alert (`clothoid-lab guardrail`) at 50/90/100%; alerts
  do not stop spend. Re-confirmed against billing account
  `015303-69BA52-95C035` at 2026-10-25 23:45 UTC (carried).
- **Parity:** carried — all seven comparisons passed at 2026-10-26 00:02 UTC
  (not re-run in the handoff).
- **Local tests:** 110 pass (re-run 2026-10-26 11:30 UTC, including auth,
  rate-limit and piece-model tests).
- **Git:** HEAD `c18af67` (W01 piece model); the handoff commit sits on top.
  Only `out/play-template.svg` is untracked.
- **Untracked user file:** `out/play-template.svg`; leave it alone.
- **Docs:** `docs/HANDOVER.md` is the durable reference;
  `docs/HANDOVER.html` is its browser mirror.

## What changed this session

- Added `web/` MVP: stdlib HTTP server, static page, JSON editor, SVG preview,
  report, presets/caps, SVG/JSON download.
- Added `Dockerfile` with Debian C++ build and `python:3.12-slim` runtime.
- Added `.dockerignore`, `.gcloudignore`, `tests/test_web.py`, `web/README.md`.
- Deployed the container to Cloud Run via Cloud Build.
- Set min 0 / max 1, concurrency 2, 1 vCPU / 512 MiB, 60 s timeout.
- Created the $1 budget alert.
- Added project-scoped, focused `/fhandoff` and `/fhandon` commands, modelled
  on the existing `handoff`/`handon` pattern in `grid-8` and `ornaments`.
- Added `scripts/check-parity.py`, which compares the local and remote served
  assets, presets/caps, SVG and report. It passes.
- Opened the local and remote apps in Chrome tabs as the shared starting base.
- Added a **global** `/focus` command (`~/.config/opencode/commands/focus.md`)
  that moves any session into this repo and surfaces `next-fhandoff.md` without
  starting work, so `/fhandon` is reachable after a restart from any directory.
  `/fhandon` and `/fhandoff` stay project-scoped on purpose: they are hard-wired
  to this repo and should not appear in `grid-8` or `ornaments`.
- Made `/fhandon` faster to follow: it now opens with one sentence naming the
  focused action, and it uses headless Chrome/CDP for browser checks instead of
  looking for the desktop Review pane or Safari.
- Hardened the phone layout in `web/static/style.css`: zero-minimum grid
  tracks, `min-width: 0` on selects/inputs/status, wrapping action buttons, and
  tighter 430px padding. Headless Chrome at 390 × 844 and 320 × 844 shows no
  overflow in any state (cap-14, `cap-pt-9`, all four presets, width error,
  report shown). The original clipping did **not** reproduce in Chromium, so
  the hardening targets intrinsic-width/Safari cases; confirm on a real phone.
- Deployed the CSS fix: revision `clothoid-web-00003-r4m`; remote measures
  390/390 at 390 × 844 with the same control geometry as local; parity passes.
- Phone check on the Samsung: right edge confirmed clean, 2026-10-26. The
  temporary tunnel was closed after the check.
- Split the image: added `engine/Dockerfile` (C++ build + runtime base),
  `cloudbuild.engine.yaml`, a thin app `Dockerfile` (FROM the engine base), and
  `.gcloudignore.engine`; app `.gcloudignore` now drops `vendor/`, `csrc/`, and
  `scripts/`. Engine base built in 6m43s; first thin deploy took 30 s
  (revision `clothoid-web-00004-nwx`); parity passed.
- Added shared-token access and quotas: HTTP Basic on every route except
  `/health`, token in Secret Manager `clothoid-token`, and a per-address
  render limit (60/min, burst 20). Deployed as revision
  `clothoid-web-00006-zrx`; 401 without the token, 200 with it. Added
  `tests/test_auth.py`.
- **W01 done:** added `clothoid_lab/piece.py` (`Piece`, `Trace`,
  `render_piece`), extended `svg.document(..., groups=...)` for several named
  traces, and added `tests/test_piece.py`. The visual proof is
  `docs/piece-model.html`, generated by `scripts/piece_sandbox.py`: one ribbon
  half, its two rails, its mirror, and an unmirrored guide.
- Added `docs/ornament-board.html`: **85 plates** (45 catalogue ornaments
  P21–P65, 27 class I caps P66–P92, 9 class II leaves P93–P101, 4 presets
  P102–P105), **26 work items** W01–W26 and **11 decisions** D01–D11. The
  twenty fleur studies (P01–P20) are the subpage `docs/fleur-studies.html`,
  defaulted to “Needs work”. The board has a beginner glossary, plain-language
  briefs, editable text per card, DeepSeek-pick sorting, priority/stage,
  drag/↑↓, notes, localStorage and JSON/order export.

## Risks / open decisions

1. **Accounts and roles are still absent.** The shared token (W11) and the
   per-address render limit (W12) protect the URL, but there are no named users,
   saved designs or audit trail. Rotate the Secret Manager version if the token
   leaks.
2. **Cold starts** at min 0 are roughly 1–3 s. Do not pay for min 1 unless a
   demo needs it; set it back to 0.
3. **Free-tier usage.** Stay within the monthly Cloud Run/Cloud Build/Artifact
   Registry allowances; the budget alert is only a warning.
4. **Large deploys (fixed).** App deploys are thin and skip the C++ compiler;
   the engine base must be rebuilt only when `vendor/`, `csrc/`, or
   `scripts/build-native.sh` changes. The base tag is pinned to `2026-10-26`.
   The Debian build is deliberate: the Ubuntu 24.04 artifact needs glibc 2.38
   and will not run on Debian bookworm.
5. **Caps are baked in.** New `out/caps/*.json` files need an app deploy (thin),
   not an engine rebuild.
6. **No persistence/accounts.** Designs live in the browser and are not saved.

## Next move

**W02 — terminals.** Add a small vocabulary for how an open trace ends:
`butt` (current), `point` (corner), `arc` (small radius), `round` (half-width)
and `taper`. Apply it per trace end in `Piece`/`render_piece`, report the
terminal like a join, keep `butt` as the baseline, and extend the visual
sandbox with a terminal strip. Then W03 the fleur grammar, W04 the twenty sets.

## Tooling notes

- `--headless=new` hangs Chrome on this machine; `--headless=old` captures
  screenshots fine. Prefer DevTools Protocol over CLI flags for emulation and
  measurement.

## Important paths and commands

| Path | Purpose |
|---|---|
| `web/server.py` | stdlib server and `/api/render` |
| `web/static/` | MVP page, JS, CSS |
| `clothoid_lab/piece.py` | `Piece`/`Trace` multi-trace model and renderer |
| `tests/test_piece.py` | piece model, mirror, round-trip tests |
| `scripts/piece_sandbox.py` | builds `docs/piece-model.html` |
| `docs/piece-model.html` | W01 visual proof: traces, rails, mirror |
| `Dockerfile` | thin app image; starts FROM the engine base |
| `engine/Dockerfile` | engine base: C++ build + Python runtime + `.so` |
| `cloudbuild.engine.yaml` | build and push the engine base |
| `.gcloudignore` | small app-only Cloud Build upload |
| `.gcloudignore.engine` | engine-base build context |
| `scripts/check-parity.py` | local/remote parity smoke test |
| `tests/test_web.py` | web API tests |
| `tests/test_auth.py` | token auth and rate-limit tests |
| `docs/HANDOVER.md` | durable handover |
| `docs/HANDOVER.html` | HTML mirror |
| `docs/BACKLOG.md` | execution detail for W01–W26 |
| `docs/ornament-board.html` | visual board: 85 plates, 26 work, 11 decisions |
| `docs/fleur-studies.html` | subpage: the twenty fleur studies, P01–P20 |
| `scripts/board/` | board generator, template, extractors and README |
| `next-fhandoff.md` | two-line focused pointer |
| `.opencode/commands/fhandoff.md` | write the focused handoff |
| `.opencode/commands/fhandon.md` | resume from it |
| `~/.config/opencode/commands/focus.md` | global: move session here, show focus |

```sh
cd /Users/thomaskelly/developer/clothoid-lab
.venv/bin/python -m unittest discover tests
.venv/bin/python web/server.py
# with the local server up and the remote reachable:
.venv/bin/python scripts/check-parity.py
```

```sh
# engine base: only when vendor/, csrc/, or scripts/build-native.sh changes
gcloud builds submit --config cloudbuild.engine.yaml \
  --ignore-file=.gcloudignore.engine .

# app: every UI/Python change (thin upload, no C++ compile)
gcloud run deploy clothoid-web --source . --region us-central1 \
  --allow-unauthenticated --memory 512Mi --cpu 1 --concurrency 2 \
  --min-instances 0 --max-instances 1 --timeout 60 --port 8080 \
  --set-env-vars HOST=0.0.0.0 --quiet
```
