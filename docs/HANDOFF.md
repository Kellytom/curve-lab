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
  `.dylib`. Start with `.venv/bin/python web/server.py`.
- **Remote:** `https://clothoid-web-ba5ahdu6bq-uc.a.run.app` — Cloud Run,
  project `clothoid-lab-1792967460`, region `us-central1`, service
  `clothoid-web`, revision `clothoid-web-00002-wsp`.
- **Remote limits:** min `0`, max `1`, 1 vCPU, 512 MiB, concurrency `2`,
  60 s timeout, public/unauthenticated.
- **Budget:** `$1/month` alert (`clothoid-lab guardrail`) at 50/90/100%; alerts
  do not stop spend.
- **Local tests:** 96 pass.
- **Git:** run `git log -1`; the last pre-command commit was `59ead35`.
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

## Risks / open decisions

1. **No auth or rate limiting.** The public URL can consume the free allowance.
   This is the main blocker to sharing it broadly.
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

Confirm the remote MVP on the phone and check the responsive layout. The
focused handoff currently points at adding a lightweight auth/rate-limit layer
before publicizing the URL. Do not increase max instances until that exists.

## Important paths and commands

| Path | Purpose |
|---|---|
| `web/server.py` | stdlib server and `/api/render` |
| `web/static/` | MVP page, JS, CSS |
| `Dockerfile` | Linux build + runtime image |
| `.gcloudignore` | small Cloud Build upload |
| `tests/test_web.py` | web tests |
| `docs/HANDOVER.md` | durable handover |
| `docs/HANDOVER.html` | HTML mirror |
| `next-fhandoff.md` | two-line focused pointer |
| `.opencode/commands/fhandoff.md` | write the focused handoff |
| `.opencode/commands/fhandon.md` | resume from it |

```sh
cd /Users/thomaskelly/developer/clothoid-lab
.venv/bin/python -m unittest discover tests
.venv/bin/python web/server.py
```

```sh
gcloud run deploy clothoid-web --source . --region us-central1 \
  --allow-unauthenticated --memory 512Mi --cpu 1 --concurrency 2 \
  --min-instances 0 --max-instances 1 --timeout 60 --port 8080 \
  --set-env-vars HOST=0.0.0.0 --quiet
```
