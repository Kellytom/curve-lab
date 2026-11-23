# SC-HANDOFF-int — the sidechat's handoff (read this first after a reset)

*Rewritten 2026-11-23 at the operator's `/shandoff`, before a model switch to GLM.
Everything below is committed (last `af090664`); the push is reported at the foot.*

## 1. Where the work stands

1. **The Inkscape round trip — CLOSED, proven on Inkscape 1.4.4.** `inkscape/`
   (send + receive `.inx`, actions, handles, variant), `docs/INKSCAPE-ROUNDTRIP.md`;
   guard `tests/test_ph_actions.py` (14), `test_ph_roundtrip.py` (7, through an
   Inkscape-serialised fixture), `test_ph_variant.py` (5).
2. **The broken heart is on `/candidates/`** — the strength sweep (lateral 1/10,
   9/50, 13/50 with reach 0.20 / 0.36 / 0.52, i.e. 2A), the straight seam as the
   reference, and the 9/50 rejoined. Commit `730c0fc3`; page
   `app/src/pages/candidates.astro`, five drawings in `app/public/deep2/`.
3. **The GLM session runbook** — `state/SC-GLM-SESSION-int.md` (`af090664`): the
   seven-step sequence, and the agent `~/.config/opencode/agents/glm-scan.md`,
   which writes its own report to `deep2/notes/ai-news-scan-glm-5.3.md`.
4. **The AI-news scan baseline** — `deep2/notes/ai-news-scan-deepseek-review.md`.
   It ran on `deepseek-v4.1-flash`, not GLM, because `opencode run` ignored the
   agent's `model:`; kept as the thing GLM is compared against.
5. **The s/f split and the junior role** — `state/SC-READING-int.md`,
   `state/SCmemory-int.md`, `state/SCToDo-int.md`, `next-shandoff-int.md`.
   DeepSeek1 is senior dev and designer; the `f` family is not read here.
6. **The queue of ten** — `state/SCToDo-int.md`, first table; rows 1–2 landed.
7. **The book-plate gap, measured not fixed** — 393 SVGs, 371 PNGs, 22 with no
   raster at all (`c-0398`–`c-0419`), and all 371 rasters older than their SVG.
   Counted this session; not yet written to a state file.

## 2. The operator's open asks, in order

1. **Run the GLM scan.** Their words: "lets do the glm run now". Then: "i am
   going to be on this side of the keyboard" — so it is interactive, GLM writes
   the md itself, nothing is pasted. Open first: `state/SC-GLM-SESSION-int.md`.
2. **The lens for everything next:** "getting the curves ready to move over to
   inkscape and then to the books". Open first: `book/print/`,
   `scripts/print_plates.mjs`, `book/README.md`.
3. **Consolidate the HTML pages.** Their words: "put the heart attempts into an
   existing html page. we need to consolidate our html pages." The heart landed
   on `/candidates/`; the consolidation itself is open and is a design call.
   Open first: `app/src/pages/candidates.astro`, `app/src/pages/hearts.astro`.
4. **A human figure at the centre.** Their words: "i need a human face or figure
   or statue … symbolizing human form in the center." DeepSeek1's ground; I
   measure if asked. Open first: `archive/notes/prior-art-human-figure.md`.
5. **Above the fold** (AGENTS.md, 2026-11-23): "what the reader sees before
   scrolling — a height in CSS pixels at the window they use". Open first:
   `state/FOLD-int.md`; re-measure with `node scripts/fold_report.mjs <width>`.

## 3. Environment facts a fresh session must not rediscover

- **Node 24 is at `~/node24/bin`**; the app is Astro on **4321** and its health
  line must read `node v24` and `astro 7`. Python 8003 only for the generated lab
  pages.
- **`opencode run` ignores an agent file's `model:`** — pass `--model`, and read
  the printed `> <agent> · <model>`. A run that says deepseek did not use GLM.
- **A headless run cannot answer a permission prompt**, so a write needs
  `--auto`; interactive is preferred because the prompt is the review.
- **The register takes ~44 s here**, not the "tenth of a second" the prompt
  claims. `check-db.mjs` prints the registry's 393, not the 262 in the `/fhandon`
  text.
- **`npm --prefix app run test:pages` runs every route when the tree is dirty**
  (~9 min). `/problems/` is red (no header, title, draft mark or `<main>`) and is
  DeepSeek1's, not ours.
- **`loading="lazy"` makes images blank in an element screenshot** and in a
  narrow-viewport shot; use `node scripts/shot.mjs <url> <out> <w> <h> viewport
  "<css selector>"` with the images eager.
- **`scripts/print_plates.mjs` has no pngquant step** (0 mentions); the binary is
  `.venv/bin/pngquant`. The PNG pass is separate and slow.
- Mailboxes are `archive/notes/`, heading `## YYYY-MM-DD HH:MM — subject`, 400
  lines max; DeepSeek1's is read-only for me.

## 4. The one next action

**Write the book-plate gap down and hand it over:** `state/SC-BOOK-GAP-int.md`
listing the 22 uids with no raster (`c-0398`–`c-0419`), the fact that all 371
existing PNGs are older than their SVG, and the command that counted them; then
ask DeepSeek1 to authorise the one raster run, because `print_plates.mjs` is
theirs and the tree currently carries their plate work. Do not edit that script
or start a raster pass without the word.
