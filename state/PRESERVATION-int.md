# PRESERVATION — the work outlives the account

The aim, in the operator's words: *this should survive past my death, and that means no
monthly charges, even for GitHub.*

So the rules below are about **free, plain, and copyable**, not about polish. A thing that
needs a subscription or a running service is not preserved; it is rented.

## What must survive

1. **The records** — `workbench/curve-registry.json` (397 curves), `state/DATA-int.md`, and the
   `data/` export of the database. Text, small, and enough to rebuild everything else.
2. **The generators** — `scripts/` and the app: the code that turns a record into a figure, a
   plate, a page. Without it the records are a list of numbers.
3. **The pictures** — `book/print/` (397 plates, PNG + SVG) and `app/public/figures/`.
4. **The words** — the docs under `app/src/content/docs/`, the specs and handoffs in `state/`,
   the README.

## The rules

- **No paid dependency on the critical path.** No LFS (its free quota is 1 GB and a lapse makes
  the files unreadable), no hosted database, no CDN, no build service. SQLite is the runtime
  store; the JSON export is the durable copy; both are in the repository.
- **Plain formats only.** JSON, Markdown, Python, JavaScript, SVG, PNG. Nothing that needs a
  particular application to open, and no format that has to be licensed.
- **Under the free limits, by a wide margin.** GitHub's guidance is a repository under 1 GB,
  and a file under 100 MB. Today: `.git` is 228 MB and the largest plate is 100 KB. Committing a
  re-rendered plate set is therefore fine **once per change of set**, not per tweak.
- **The repository is the master; GitHub is a copy.** Everything needed to rebuild is
  committed, so a lost host costs the account, not the work.
- **More than one copy, in more than one place.** GitHub alone is one company's decision away
  from gone. At least one mirror, and one archive that does not depend on git.

## What to do, in order

| step | cost | why |
|---|---|---|
| **Make the repository public** | free | a public repository can be cloned, forked and archived by others; a private one dies with the account. `app/data/users.json` and the database are already excluded |
| **Mirror to a second host** (Codeberg, GitLab) | free | one push target is one point of failure |
| **Submit to Software Heritage** | free | it archives public repositories permanently and mints a `swh:1:` identifier |
| **Deposit the plate set** (Zenodo or the Internet Archive) | free | a citable snapshot of the pictures that does not depend on git at all |
| **Keep a local copy** | free | a clone plus `data/` on a disk that is not the working machine |
| **A succession note in the README** | free | who may take the repository over, and that it is meant to be kept |

## What not to do

- **Do not put the big binaries in LFS.** It reads as the tidy answer and is the one that
  breaks: past the free quota, clones fail until someone pays.
- **Do not rely on the running app.** The deployed instance is a convenience; the repository is
  the work.
- **Do not let one host be the only copy** — including this one.

## The decision that is still open

**Public or private.** Public is the single largest lever: it is what makes forking, mirroring
and permanent archiving possible at no cost. It also publishes the plates, the text and the
code — which is what a book project wants — while the user store and the database stay out of
the tree. The operator has kept it private so far; this note records why it matters.
