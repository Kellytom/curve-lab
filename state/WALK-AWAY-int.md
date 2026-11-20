# WALK-AWAY-int — the project must outlive the person running it

The operator's top-level requirement (2026-11-19):

> "I want to be able to walk away from this project at any time, knowing someone
> else can understand and use it easily. I don't want to pay money, primarily
> because if I die, my debit cards will only last a year and then everything
> quietly goes away that is paid for. Also, make generous use of archive.org to
> store individual pages forever."

This is a constraint on every session, beside the register and the design notes.
Read it before choosing a tool, a host or a dependency.

## 1. Someone else must be able to pick it up

- **The repository is the whole project.** A clone, Python 3, Node 24 and the
  vendored C++ must be enough. No private service is required to build, run or
  understand it.
- **The state files are the handover.** `state/HANDOFF-int.md` (tail),
  `LTMemory-int.md`, `state/DESIGN-int.md`, `state/REGRESSIONS-int.md`,
  `state/READING-int.md` and `README.md` are written for a stranger, not for us.
- **Runbooks over memory.** Every routine has a command: the gate
  (`scripts/test.py`), the register, `recheck`, `recover`, `check-db`, the build.
  If a step is only in someone's head, it is not done.
- **No single-person knowledge.** A name, a number or a convention lives in the
  repo (a table, a test, a note), never only in a chat.

## 2. Nothing paid, nothing that needs a card

- **No paid hosting is required.** The app runs locally (`npm --prefix app run
  dev`) and can be built to static files. Cloud Run is an *optional* convenience
  and must never be the only way to see the work.
- **No paid API, storage or database.** SQLite is a file; the exports are in git;
  GitHub is the off-site copy. A tunnel is a convenience, not a dependency.
- **No trial that expires into silence.** If a thing stops when a card expires,
  it is not part of the project.
- **Costs are stated** when a session proposes anything that could bill: name the
  service, say what it costs and what happens when it stops.

## 3. archive.org is the permanent copy of the pages

The web pages are the public face; the repository is the source. A page that
matters is archived, not merely published:

- `scripts/archive_pages.py` submits a URL to the Wayback Machine ("Save Page
  Now") and appends the resulting snapshot to `state/ARCHIVE-int.md`.
- Archive **individual pages**, not only the repository: the README, the book
  docs, a gallery page, a plate's page. One URL per row, with the date.
- Do it when a page is worth reading by a stranger, and again when it changes
  substantially — a snapshot is cheap, and an unarchived page is one outage away
  from gone.
- The script waits between requests (the service rate-limits) and never claims a
  snapshot exists until the service returns its URL.

## 4. What this rules out

- A paid image host, a paid form service, a paid auth provider.
- A build that needs a global toolchain installed by hand and unrecorded.
- A page that exists only in a screenshot or only on someone's laptop.
- A dependency pinned to a version that can only be fetched from a private
  registry.
