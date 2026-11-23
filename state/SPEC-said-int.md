# SPEC — said (`/said/`)

The clean description. Faults would live in `state/PROBLEMS-said-int.md`; none yet.

**The page:** `app/src/pages/said.astro`
**The data:** `data/said.json`, written by `scripts/said.py --push` (personal, gitignored)
**The command:** `~/bin/said` (a wrapper over `scripts/said.py`)
**The check:** `app/scripts/check-pages.mjs` (one header, one main, no self-link)

## What it is

The operator: "often i have to search back in what i said to paste it into the new chat". The
page lists their own messages newest first, each with a copy button.

- **Source:** the local OpenCode database, read-only (`session_message`, type `user`).
- **Default scope:** this project's conversations, helper chats such as `ses-sidechat`
  excluded — the side chat is a different agent.
- **`said --md`** prints Markdown for pasting; **`said --push N`** writes the JSON the page
  reads and prints the URL.
- **The page is on the Astro server**, like every other page: no `file://` page and no second
  server. It reads the file per request, so a reload shows the newest list.

Rules with a check each:

- [x] The page has one header and one `<main id="main">`. Check: `check-pages.mjs /said`.
- [x] The JSON is gitignored: the history is personal and never committed. Check: `git check-ignore data/said.json`.
- [x] A copy button copies that message and says `copied`. Check: the module `app/src/scripts/said-copy.js`.
- [x] No message is invented: the list is exactly the database rows. Check: the command's count
      line matches the page's count.
