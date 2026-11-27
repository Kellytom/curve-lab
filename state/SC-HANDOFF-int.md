# SC-HANDOFF-int — the sidechat's handoff (DeepSeek2)

Written 2026-11-26 at the operator's handoff request, before a context reset.
**Identity (operator, 2026-11-24): the sidechat = `deep2` = DeepSeek2 — one agent.** DeepSeek1
is the other. The `s` files and git for this agent's own work are mine; the `f` family
(`next-fhandoff-int.md`, `state/HANDOFF-int.md`, `state/PLAN-int.md`, `state/SPRINT-int.md`) is not.

This session did **no repository work**. It was machine cleanup plus Blender/quintic tooling. The
tree was clean at `841c40b9` throughout; the only repo change is this handoff and its pointer.

## 1. Where the work stands

1. **No code change this session.** `git status --short` is empty at `841c40b9` on `main`.
2. **The 2026-11-25 workstreams still stand** — TypeScript register (`tests/test_regressions.ts`),
   `/shandon`, the gothic desk, the glue quintic, the TS ports, the Tschirnhausen pieces, the
   recent-work appendix. Proof: `git log --oneline -20` and the rows in the previous handoff.
   None of them was touched or verified again today.
3. **Disk: 27.1 GB → 113 GB free.** Proof: `df -h /System/Volumes/Data`. Ten cache rows, Chrome
   caches, the Mylio library (21 GB), `~/Local Sites LOM` (8 GB) and two Wine stacks removed.
4. **Audio driver fault fixed, then it partially came back.** The orphaned
   `MSTeamsAudioDevice.driver` was moved to `/Library/Audio/Plug-Ins/HAL-Disabled/`; `coreaudiod`
   fell 55.7% → 0.4%, then climbed to ~30% after the audio settings were reloaded at 22:12.
   Proof: `ls /Library/Audio/Plug-Ins/HAL/` (empty), `ps -o pcpu= -p $(pgrep -x coreaudiod)`.
5. **Adobe removed by hand, not with Adobe's uninstaller** (that is a GUI app). 0 Adobe processes;
   the apps, `/Library/Application Support/Adobe` and all launch agents/daemons are gone.
   Proof: `pgrep -f -i adobe` is empty. Left behind: 112 receipts in `/var/db/receipts`,
   `/Users/Shared/Adobe` (12 MB), ~15 `com.adobe.*` plists. **Uncommitted, and offered, not done.**
6. **Blender 4.2.23 LTS (Intel) installed** at `/Applications/Blender.app`. Proof: headless launch
   exits 0 and prints `4.2.23 LTS`; a Workbench render writes a PNG. EEVEE headless hangs.
7. **The quintic kit** at `~/developer/quintics/` — `quintic-kit.blend` (four six-point quintics
   with cages), `tools/curve_to_svg.py` (sampled SVG + dashed control polygon),
   `tools/quintic_kit.py` (regenerates the blend), `tools/refit.py` (the invertibility test),
   `curve.svg`. **Outside the repo by design, so not committed.**
8. **PDF default changed** to PDF Expert (`com.readdle.PDFExpert-Mac`), was Acrobat.
   Proof: `LSSetDefaultRoleHandlerForContentType` returned 0 and reads back the new bundle id.

## 2. The operator's open asks, in order

1. **"lets get back to the choice of blender, geogebra or inkscape to draw the outer control
   curve, which renders the inner quintic bezier"** — open. First file:
   `~/developer/quintics/quintic-kit.blend`, then §3 below.
2. **"how do i draw a few quick curves in blender to get a feel for the quintics?"** — answered;
   the kit exists, the keystrokes were given: `Tab`, `Alt+A`, click one end point, `E`, click.
   Not yet exercised by the operator.
3. **"get rid of adobe but not the data"** — done except the paperwork listed in §1.5; first file:
   nothing to read, one admin command.
4. **"no reboot for now"** — the `coreaudiod` regression is open and waits on a reboot or a
   device check. First file: this handoff, §1.4.
5. **"keep caffinate"** — no action, `com.local.caffeinate` left running.

## 3. Environment facts a fresh session must not rediscover

- **Blender's order is clamped silently to the point count.** `Add → Curve → Path` gives 5 points;
  `order_u = 6` then means degree 4. Six points plus `order_u = 6` plus `use_endpoint_u` is an
  exact degree-5 Bézier — proved to 0.0001 against de Casteljau in `tools/refit.py`.
- **Blender cannot export SVG.** The bundled `io_curve_svg` is import-only ("Import SVG as
  curves"). The extension "Export Curve as SVG" needs `blender_version_min = 5.0.0`, and Blender
  5.0 ships **no Intel macOS build** — unusable here.
- **SVG has no quintic primitive** (`M L H V C S Q T A` only). Any export samples or refits.
  Sampling **is** invertible with uniform `t` (0.0001 control-point error); with chord-length `t`
  it is wrong by 1.82. Degree is lost forever in a cubic refit.
- **`.blend` stores control points as float32** (`0.1` → `0.10000000149011612`) and does not
  expose a knot vector (`spline.knots_u` raises `AttributeError`); clamped ends are a flag.
- **The Metal warning is benign.** Iris 550 reports Metal API 1.2; Workbench works, EEVEE is the
  fragile path. Use `Z → Solid`.
- **Inkscape 1.4.4** is cubic-only; **GeoGebra is not installed**; **FreeCAD is not installed**
  (the only realistic STEP/3DM hub).
- **TCC:** the shell is spawned by `~/.opencode/bin/opencode` whose parent is `launchd`, so Full
  Disk Access granted to kitty does nothing. `~/Downloads`, `~/Desktop`, `~/Documents`,
  `~/.Trash` and the Photos library stay unreadable; `mdfind`/`mdls` still return sizes from the
  Spotlight index.
- **The gate command changed today:** `node --test tests/test_regressions.ts` (36 tests, ~5 s).
  The Python twin is gone.
- **`coreaudiod` is at ~30% again** — do not read that as the driver returning; the HAL folder is
  empty and no Teams device is listed.
- **Pushes:** this handoff is committed and pushed at the operator's explicit word. Do not assume
  internet is open for anything else.

## 4. The one next action

**Add the exact control points to the exporter, then use it once by hand.**
In `~/developer/quintics/tools/curve_to_svg.py`, write each spline's six `(x, y)` control points
into its `<path>` as `data-control="0,0 1,3 3,4 6,3 8,0 9,-2"` alongside the sampled `d`, and
write the degree and knot mode as `data-degree="5" data-endpoint="true"`. Then drag the six points
of `S_curve` in `quintic-kit.blend`, re-export, and confirm the file is both picture and record.

`Proves:` a fresh `curve.svg` parses back to the same six control points that
`spline.points[i].co` reports, and the export log still prints `control=6`.

**Question for DeepSeek1, not to be guessed:** is a Blender-side exporter project work, or is it
the operator's own tooling outside the repo? It lives in `~/developer/quintics/` until they say
otherwise.
