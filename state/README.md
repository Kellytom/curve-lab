# state/

What is true **this week**, as opposed to what is true in general.

| file | what it holds |
|---|---|
| `HANDOFF-int.md` | current truth: local, remote, tests, git, risks, the next move. Written by `/fhandoff`; do not hand-edit the state lines |
| `BACKLOG-int.md` | execution detail for W01–W26, the work items on the board |
| `SESSIONS-int.md` | the proposed order for the next sessions |
| `WORK-int.md` | the P/W/D registers and the spine layer's promotion gate |
| `STATUS-int.md` | what works today, what is not wired |

These are superseded regularly and grow stale on purpose — that is the point of
keeping them apart from `docs/`, which holds the durable reference and the
design writing. They are not part of the published mkdocs book.

Start at `HANDOFF-int.md`. It is the second thing every session reads.


## The `-int` suffix

Every file here is internal: it carries working truth — paths, open defects,
sometimes addresses — and is not written for an audience outside the project.
A `-ext` twin of any of them can be produced later by taking the same content
and removing what should not travel; the internal one stays the source.

| file | what it is |
|---|---|
| `HANDOFF-int.md` | current truth, what is in flight, what is next |
| `ACHIEVEMENTS-int.md` | every result, with the command that re-derives it |
| `BACKLOG-int.md` | the W-label detail |
| `SESSIONS-int.md`, `STATUS-int.md`, `WORK-int.md` | order, state, breakdown |
