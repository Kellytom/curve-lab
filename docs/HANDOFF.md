# clothoid-lab handoff

**Updated:** 2026-10-25  
**Use `/fhandon` to resume, `/fhandoff` to refresh this file.** The commands are
project-scoped: open OpenCode in this repository to use them. They are not
global and do not appear in `grid-8` or `ornaments`.

## Objective

Turn clothoid-lab into a usable design tool with exact clothoid geometry, a
200 × 250 mm sheet, +y up, and class I/II cap families. A local MVP and a public
remote MVP now exist.

## Current state

- **Local:** `http://127.0.0.1:8000/` — Python stdlib server plus the macOS
  `.dylib`. Start with `.venv/bin/python web/server.py`. Verified HTTP 200 at
  2026-10-25 23:45 UTC.
- **Remote:** `https://clothoid-web-ba5ahdu6bq-uc.a.run.app` — Cloud Run,
  project `clothoid-lab-1792967460`, region `us-central1`, service
  `clothoid-web`, revision `clothoid-web-00002-wsp` (unchanged). HTTP 200 in
  0.3 s at 2026-10-25 23:45 UTC.
- **Remote limits:** min `0`, max `1`, 1 vCPU, 512 MiB, concurrency `2`,
  60 s timeout, public/unauthenticated.
- **Budget:** `$1/month` alert (`clothoid-lab guardrail`) at 50/90/100%; alerts
  do not stop spend. Re-confirmed against billing account
  `015303-69BA52-95C035` at 2026-10-25 23:45 UTC.
- **Parity:** local and remote static assets, preset/cap lists, and a real cap-14
  render are byte-identical. `scripts/check-parity.py` passed on 2026-10-25
  23:32 UTC (local and remote both HTTP 200).
- **Local tests:** 96 pass (re-run 2026-10-25 23:44 UTC).
- **Git:** HEAD `922a9c8`; the handoff commit sits on top of it. Only
  `out/play-template.svg` is untracked.
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
- Started the phone review. At 390 CSS px the single-column layout still
  overflows horizontally: the Cap select, the ribbon-width field, the SVG/JSON
  buttons and the status line are clipped past the right edge. The cause is not
  yet diagnosed and **no CSS fix has been applied**.

## Risks / open decisions

1. **No auth or rate limiting — deferred by operator decision.** The public URL
   can consume the free allowance, so keep it private for now. Do not increase
   max instances until this is addressed.
2. **Cold starts** at min 0 are roughly 1–3 s. Do not pay for min 1 unless a
   demo needs it; set it back to 0.
3. **Free-tier usage.** Stay within the monthly Cloud Run/Cloud Build/Artifact
   Registry allowances; the budget alert is only a warning.
4. **Large deploys.** The vendored C++ tree makes Cloud Build uploads slow. The
   current Debian build is deliberate because the Ubuntu 24.04 Linux artifact
   needs glibc 2.38 and will not run on Debian bookworm.
5. **Caps are baked in.** New `out/caps/*.json` files require a rebuild.
6. **No persistence/accounts.** Designs live in the browser and are not saved.

## Next move

Fix the horizontal overflow at phone width in `web/static/style.css`, then
re-check local and remote at 390 × 844. Auth/rate limiting is deferred. Keep the
URL private until it is added.

## Tooling notes

- `--headless=new` hangs Chrome on this machine; `--headless=old` captures
  screenshots fine. Prefer DevTools Protocol over CLI flags for emulation and
  measurement.

## Important paths and commands

| Path | Purpose |
|---|---|
| `web/server.py` | stdlib server and `/api/render` |
| `web/static/` | MVP page, JS, CSS |
| `Dockerfile` | Linux build + runtime image |
| `.gcloudignore` | small Cloud Build upload |
| `scripts/check-parity.py` | local/remote parity smoke test |
| `tests/test_web.py` | web tests |
| `docs/HANDOVER.md` | durable handover |
| `docs/HANDOVER.html` | HTML mirror |
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
gcloud run deploy clothoid-web --source . --region us-central1 \
  --allow-unauthenticated --memory 512Mi --cpu 1 --concurrency 2 \
  --min-instances 0 --max-instances 1 --timeout 60 --port 8080 \
  --set-env-vars HOST=0.0.0.0 --quiet
```
