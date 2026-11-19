---
title: If something goes wrong
---

Short version: the database is the record, the snapshots are the undo, and the
JSON files are the readable fallback. Below is what to do for each failure.

## Detect it

```sh
cd app
sqlite3 prisma/dev.db "PRAGMA integrity_check;"   # "ok" or a list of faults
node scripts/check-db.mjs                        # counts against the registry
npm run backup                                   # take a snapshot before you touch anything
```

## The database is damaged

1. Stop the app (no writes while repairing).
2. `sqlite3 prisma/dev.db "PRAGMA integrity_check;"` — if it is not `ok`, do not
   try to edit the file.
3. `npm run restore` — the newest snapshot, with the damaged file copied aside
   as `dev.db.before-restore-*`.
4. `node scripts/check-db.mjs` — 262 curves, 262 notes, 262 sets.
5. If the newest snapshot is also damaged, restore an older one by name from
   `state/backups/db/` (the last 20 are kept).

If every snapshot is gone, the readable fallback is `workbench/curve-registry.json`
(rows, lists, default names) plus `workbench/curve-notes.json` (names, ratings,
turns, pieces). `node scripts/migrate.mjs` rebuilds the database from them.

## A JSON file is damaged

The registry and the notes mirror are **derived**. Do not repair them by hand:
`node scripts/migrate.mjs` regenerates the database, and the export is written
again on the next save. The star export is rewritten by `scripts/operator_list.py`
and `/api/finder-stars`.

## The disk is lost, or the machine will not start

GitHub is the off-site copy, and it is kept current automatically: a LaunchAgent
runs `scripts/sync-data.sh` every five minutes, committing and pushing the data
exports (`curve-registry.json`, `curve-notes.json`, `finder-stars.json`,
`starred.json`, `operator-list.json`).

On a new machine: clone the repository, `npm --prefix app install`,
`npx prisma db push`, `node scripts/migrate.mjs`, `node scripts/check-db.mjs`.
You lose at most the last five minutes of edits, and only if the machine died
between two syncs.

The exception is the **user directory**: it lives only in `app/data/users.json`
(gitignored) and in the database. It is deliberately not on GitHub because the
repository is public. Back that file up somewhere private, or accept losing it.

## Something is hacked

1. **Close the door first.** Stop the tunnel (`scripts/tunnel.sh stop`), stop the
   Astro app, and stop the Python server.
2. **Rotate every secret that was reachable.** The shared token in Secret
   Manager (`CLOTHOID_TOKEN`), the ownership key in `ppoi.json`, any Cloudflare
   tunnel credentials, and `gh auth` if the GitHub account was reachable.
3. **Check GitHub** for commits, deploy keys and tokens you did not create.
4. **Restore** the newest snapshot from before the intrusion, and compare
   `node scripts/check-db.mjs`.
5. **Read the changes.** The database has no audit table yet; the JSON notes
   mirror shows the current values, not who changed them. That is a known gap.

The Astro app has **no login**. It is safe on localhost and unsafe on a public
hostname. The Python server has a shared-token gate; the app does not. Do not
expose the app without putting auth in front of it.

## A rename or a rating is wrong

Every save replaces one row; the previous database is in the snapshot taken on
the last start, and `curve-notes.backup.json` holds the previous notes export.
Restore the snapshot, or set the value again in `/names`.

## Drill

A backup that has never been restored is a hope. Twice a year: copy the newest
snapshot to a scratch folder, open it, run `check-db` against it, and delete the
scratch copy. That proves the file, not just the script.
