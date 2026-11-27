# PROBLEMS — photo reduction

Every fault this project has had: the operator's words, what was actually wrong, the fix, the guard.
The clean description lives in `state/SPEC-photo-reduction-int.md`; nothing here is a plan.

## 1. The service daemon outlives quitting the app (2026-11-27)

**Symptom.** A permission was granted to OpenCode, the sessions were quit and reopened, and the
library was still `Operation not permitted`.

**Cause.** The tool calls run as children of `opencode serve --service`, pid 872, whose parent is
`launchd`. Quitting the app closes windows and leaves that process alive; macOS binds a permission to
a process when it starts, so the grant never reached it.

**Fix.** The run did not need the permission: AppleScript into Photos works and is the route used.

**Guard for next time.** Read `ps -o lstart= -p <daemon>` before blaming the grant. If the daemon is
older than the grant, restart it (`kill`), or choose a door that does not need it.

## 2. A "reduction" produced a file 19× larger (2026-11-27)

**Symptom.** `0.49 MB -> 9.74 MB (1969 %) over-target` in one line of a run.

**Cause.** `sips` with no size cap re-encoded a small source into a much larger file; nothing checked
the result against the input.

**Fix.** After every reduction, compare bytes: if the output is not smaller, delete it, copy the
original, and record `skipped-larger`.

**Guard.** The comparison is in `handle()` in `scripts/photo-reduce.ts`, before the manifest row is
written. A row can no longer claim a saving that is not there.

## 3. Exporting one asset per Apple event was 10× slower (2026-11-27)

**Symptom.** ~10.8 s per asset on an album whose export itself takes 0.32 s.

**Cause.** Every `osascript` call resolves `album "X"` by name across 272 albums before it touches the
item.

**Fix.** Export in chunks (`--chunk`, default 20) and map the returned ids to the exported filenames.

**Guard.** Measured, not assumed: 5 assets in 5.6 s chunked against 54 s per-item.

## 4. The resize reaches a quarter on its own (2026-11-27)

**Symptom.** The operator asked for 1/4 to 1/2 the size; the run produced about 1/8 per file, then
23 % across 29 files.

**Cause.** The 3000 px long-side cap, not the JPEG quality, is what removes the bytes. Quality 90
changed little.

**Guard.** `--max-long-side` is a flag; raising it to 4032 is the measured lever, and it is named in
the spec rather than buried in the code.

## 5. The copies were owner-only, so other programs could not read them (2026-11-27)

**Symptom.** The operator, 2026-11-27: "obviously the photos should be available to the finder, and
any other program." Files existed but opened as `-rw-------`.

**Cause.** Photos' AppleScript export writes each file `0600`, and `cp` and `sips` do not widen it. The
tree was therefore readable only by the account that made it — private to the point of looking broken.

**Fix.** `chmod 0644` on every file written and `0755` on every album directory, in `handle()` in
`scripts/photo-reduce.ts`; the existing tree was widened in one pass.

**Proved.** `ls -l` shows `-rw-r--r--`; `qlmanage -t` produced a thumbnail of a reduced file, so
Quick Look and Finder can preview it; `mdls` reports `kMDItemKind = "JPEG image"`, so Spotlight reads
it. A file no other program can open is not an archive.

## 6. Album-by-album export would have missed half the library (2026-11-27)

**Symptom.** None yet — caught before it cost a run. The operator, 2026-11-27: "no guarantee that all
photos are categorized in albums, maybe a hash is necessary."

**Cause.** Photos' AppleScript `every album` returned 272 albums; the database holds 8,557 and
**56,341 of 118,612 assets belong to no album at all**. An album-driven export silently omits them.

**Fix.** Read `database/Photos.sqlite`: every asset, its album if it has one, and `_by-year/YYYY`
when it does not. `scripts/photo-db.ts` writes the plan; the reducer consumes it.

**Guard.** The plan prints its counts and the number in no album, so a future run cannot quietly
shrink. If the unalbumed figure ever comes back as zero, the query is wrong, not the library.

## 7. AppleScript times out on a library this size (2026-11-27)

**Symptom.** `count of albums` and `every media item` both failed after 120 s; raising the AppleEvent
timeout to 600 s produced `Connection is invalid (-609)` at 179 s. `get name` answered in 0.1 s.

**Cause.** Enumerating a 118k-item library exceeds AppleScript's event limit, and Photos does not
survive the larger timeout.

**Fix.** Do not enumerate through Photos. Read the database copy with `sqlite3`.

**Guard.** The database route never asks Photos a question, so the failure cannot recur. Keep
AppleScript only for operations that take an item index, which is what it is good at.
