# PNG-COMPRESSION-int — how small the plate set can get

Measured 2026-11-20 on the 397 plates in `app/public/plates-web/` (1600 px
grey). Nothing in the set was replaced: every output below lives in a scratch
folder, and the set itself is untouched until the operator picks a quality.

**Headline: `pngquant --quality 70-95 --speed 1` takes the set from 17.8 MB to
6.0 MB (66.6% smaller) in 113 s, and the lossless tools cannot get near it.**

## The tools that were available

- **zopflipng** — installed from a pip wheel (`pip install zopflipng`, Python
  binding; note the call returns `(png_bytes, status)`, not bytes).
- **pngquant 3.0.3** — installed from a pip wheel that ships the binary
  (`pip install pngquant-cli`; the binary lands in `.venv/bin/pngquant`).
- **oxipng, optipng — not obtainable on this machine, so not measured.** Homebrew
  is banned (see `AGENTS.md` §Guardrails: this Xcode is too old for bottles, so
  brew started a 30–60 minute LLVM + rust build for oxipng and delivered
  nothing). The GitHub release tarball for oxipng 10.2.1 was refused three times
  (`Connection reset by peer`). If the operator wants them later, they are one
  download away on a network that permits it.

## The whole set (the number the decision is about)

| set | bytes | time |
|---|---|---|
| original, 397 plates | 18,715,781 (17.8 MB, median 46 KB) | — |
| after `pngquant --quality 70-95 --speed 1` | 6,250,514 (6.0 MB) | **112.7 s** wall, ~0.28 s/plate |

The brief said ~19 MB; the measured set is 17.8 MB (the desk added plates since
the number was written).

## Ten representative plates, every method

Chosen to span the set: the biggest (`c-0014`, 161 KB), the smallest (`c-0021`,
12 KB), and one each of the wave, lace, hybrid, path and polyline kinds
(`c-0088` is a polyline record). Fidelity is measured pixel-by-pixel against
the original with Pillow (grey levels 0–255):

| plate | original | zopfli (lossless) | zopfli time | pngquant | pngquant max diff | changed pixels |
|---|---|---|---|---|---|---|
| c-0001 | 116,728 | 88,499 (−24.2%) | 119.0 s | 41,854 (−64.1%) | 14 | 3.17% |
| c-0002 | 66,649 | 47,872 (−28.2%) | 59.7 s | 24,745 (−62.9%) | 12 | 3.51% |
| c-0005 | 71,224 | 52,209 (−26.7%) | — | 27,127 (−61.9%) | 10 | 2.68% |
| c-0007 | 29,081 | 20,268 (−30.3%) | — | 11,136 (−61.7%) | 11 | 6.87% |
| c-0009 | 41,579 | 29,850 (−28.2%) | 27.7 s | 16,202 (−61.0%) | 13 | 4.52% |
| c-0013 | 82,750 | 61,080 (−26.2%) | — | 30,529 (−63.1%) | 12 | 3.35% |
| c-0014 | 161,100 | 113,778 (−29.4%) | — | 55,684 (−65.4%) | 16 | 4.23% |
| c-0021 | 12,218 | 7,370 (−39.7%) | 6.8 s | 5,358 (−56.1%) | 11 | 2.80% |
| c-0028 | 40,005 | 30,818 (−22.9%) | 24.0 s | 14,438 (−63.9%) | 10 | 3.75% |
| c-0088 | 16,481 | 4,504 (−72.7%) | 51.3 s | 1,159 (−93.0%) | 78* | 0.00% |
| **ten totals** | **637,815** | **456,248 (−28.5%)** | ~49 s avg | **228,232 (−64.2%)** | | |

zopfli is lossless — max diff **0** on every plate, as it must be — and its cost
is time: 6–152 s a plate, ~5.4 h for the set, for less than half the saving.

\* c-0088 is an almost-empty polyline plate: one stray pixel moved 78 levels
(mean diff 0.001). Invisible at page scale, but it is the one plate to eyeball
before committing to a setting.

## What the pngquant error is

The art is two greys, black and white, antialiased — the palette ends up at
**17–22 grey levels out of the original 211**, so most of the 64% is palette
economy, not dirt. The changed pixels are the antialiased edges (Floyd–Steinberg
dithering): never more than 7% of the plate, never more than 16 grey steps of
255 (6%). Two stricter windows, measured on the worst two plates:

| setting | c-0001 | c-0014 | note |
|---|---|---|---|
| `--quality 70-95` | 41,854 · max 14 | 55,684 · max 16 | the default candidate |
| `--quality 90-99` | 54,566 (−53%) · max 6 | 72,615 (−55%) · max 8 | keeps edges to a 3% step |
| `70-95 --nofs` | 39,868 · max 11 | 53,559 · max 12 | dithering is not the driver; the palette is |

## Recommendation

**`pngquant --quality 70-95 --speed 1` for the whole set: 6.0 MB, 113 s, done.**
If the operator wants the edges even quieter, `--quality 90-99` still halves the
set (~8.5 MB estimated from the two plates) with every moved pixel within a 3%
grey step. The visual call is the operator's: original and compressed copies of
every studied plate are side by side under
`/private/var/folders/ck/y5_gyx710jv6tr1z02xxpp1w0000gn/T/opencode/png-study/`
(`orig/` vs `pngquant/`), and the scratch folder also holds `pngquant-all/` —
a full compressed copy of the set, ready to swap in on a yes.

## The commands, so the numbers can be re-derived

```sh
# zopflipng (pip wheel zopflipng; the call returns (bytes, status))
python -c "import zopflipng; open('out.png','wb').write(
  zopflipng.png_optimize(open('in.png','rb').read(), use_zopfli=True,
  num_iterations=15, num_iterations_large=20)[0])"

# pngquant (pip wheel pngquant-cli ships the binary)
.venv/bin/pngquant --quality 70-95 --speed 1 --force --output out.png in.png

# the whole set, as measured
python - <<'PY'
import subprocess, time
from pathlib import Path
src = Path('app/public/plates-web'); out = Path('/tmp/pngquant-all'); out.mkdir(exist_ok=True)
pq = str(Path.home()/'developer/curve-lab/.venv/bin/pngquant')
t0 = time.perf_counter(); a = b = 0
for png in sorted(src.glob('*.png')):
    d = png.read_bytes()
    subprocess.run([pq, '--quality','70-95','--speed','1','--force','--output', str(out/png.name), str(png)], check=True)
    a += len(d); b += (out/png.name).stat().st_size
print(a, b, round(100*(1-b/a),1), round(time.perf_counter()-t0,1))
PY
```

## Status

Report only. The set is untouched; the compressed copies are in the scratch
folder and die with the session unless the operator says swap them in.
