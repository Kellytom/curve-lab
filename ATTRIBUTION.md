# Attribution

## Shipped in, and what their licences cost

**Clothoids**, by Marco Bertolazzi and Enrico Bertolazzi. The geometry engine:
clothoid evaluation, the G1 fitter, trimming, projection and intersection.
Licence GPL-3.0. This project is therefore GPL-3.0-or-later as a whole, and no
part of it can be relicensed or moved into a project that is not GPL.

**pyclothoids**, by Phillip Dix, 2020. The Python binding that carries the C++
engine, MIT licensed. It supplies the wheel this project installs, which is why
no C++ toolchain is needed to run the tool.

**Eigen**, by the Eigen authors, MPL-2.0. Header-only linear algebra, bundled
inside the pyclothoids build. Not used directly here.

## Used, never linked

**Inkscape**, GPL-2.0-or-later. The renderer and the node editor. This project
hands it a file and reads back a render; nothing is linked into it, and no
Inkscape code is vendored.

## Our part

Everything in `clothoid_lab/` that is not a call into the engine: the chain
model, the anchor and continuity rules, the cubic arm rule and its adaptive
subdivision, the error metric, the rails with their fold reporting, the SVG
writer and reader, the presets, and the command line.

The arm rule comes from Raph Levien's 2021 work on cleaner parallel curves with
Euler spirals, as recorded in the sibling project's `docs/clothoid-levien.md`.
The rule is used, not the code.
