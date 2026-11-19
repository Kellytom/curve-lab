---
title: Run your own instance
---

The app is a lab for one person: one database, one owner, no accounts shared
between people. If you want to use it, run your own copy. That is not a
limitation to work around; it is what keeps the data model simple and the
backups honest.

## What you need

- **Node 24** (at least 22.23) and npm
- **Python 3.12** for the engine and the scripts
- **A C++ compiler** only if you want the compiled clothoid engine
- **git**

## The short version

```sh
git clone https://github.com/Kellytom/curve-lab.git
cd curve-lab
npm --prefix app install
cd app
npx prisma db push          # create the tables
node scripts/migrate.mjs    # fill them from workbench/curve-registry.json
node scripts/check-db.mjs   # expect 262 curves, 262 notes, 262 sets
npm run dev -- --host       # http://localhost:4321
```

Open `/illuminations` for the bordered gallery, `/names` for the naming desk,
`/finder` for the curve finder.

If you also want the engine's own commands:

```sh
bash scripts/build-native.sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Where your work lives

- **The database:** `app/prisma/dev.db`. It is created by the two commands
  above and it holds your names, ratings, turns and sets.
- **The seed:** `workbench/curve-registry.json`. The migration reads it once;
  your edits live in the database after that.
- **The exports:** `workbench/curve-notes.json` and the star files. They are
  written on save, committed by `scripts/sync-data.sh`, and they can rebuild the
  database if it is lost.
- **Snapshots:** `npm run backup` writes one to `state/backups/db/`; `npm run
  restore` puts it back. A snapshot is taken on every dev start.

## Do not put it on the open internet

There is **no login**. The Python server has a shared-token gate; the Astro app
has none. Safe options:

- keep it on `localhost`;
- reach it over Tailscale or another private network;
- put Cloudflare Access, or any proxy with authentication, in front of it.

A tunnel with no auth means anyone with the link can rename your curves and
empty your lists.

## A container, if you prefer

`deploy/self-host/` has a `Dockerfile` and a `compose.yaml` that build the repo
and keep the database on a named volume at `/data/dev.db`. The manual steps
above are the tested path; the container recipe is provided as a starting point
and has not been built on this machine.

```sh
cd deploy/self-host
docker compose up --build
```

## A playground that saves nothing

For showing the app to someone without giving them a database, run a hosted copy
whose saves stay in the browser. The sandbox and the desk already export JSON;
a visitor can draw, download a file, and leave. Nothing is written to the
server, and nothing is shared. Keep that deployment read-only and separate from
your own instance.

## Licence

MIT for this project; the vendored engine is BSD-2-Clause. See `LICENSE` and
`ATTRIBUTION.md`.
