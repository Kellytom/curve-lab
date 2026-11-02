"""Promotion gate, step 1: a Pythagorean chain becomes a Piece/Trace.

The spine layer in `pythagorean-spiral/` is exact plan arithmetic: rational
anchors with rational headings, no trigonometry. This module is the one-way
bridge into the engine. It reads a chain's own cubic spans (the layer's
deliberate integration seam, `pythagorean_spiral.spans.spans`) and hands their
anchors and tangents to `interpolate.design_from_spans`, which fits one
clothoid per span. The result is an ordinary `Design`, so the rails, terminals,
clearance and SVG writer all keep working without a second geometry kind.

The import is lazy and uninstalled: `pythagorean-spiral/` is not a Python
package on `sys.path`, and the wheel does not ship it, so `load()` adds the
directory only when a chain is actually read.

    from curve_lab import spine
    package = spine.load()
    chain = package.design.lobe(package.thinnest(3125), steps=7)
    piece = spine.piece_from_chain(chain, width=1.0)
"""

from __future__ import annotations

import sys
from pathlib import Path

from . import interpolate
from .model import Design
from .piece import Piece, Trace

SPINE_ROOT = Path(__file__).resolve().parent.parent / "pythagorean-spiral"


def load():
    """Import the spine layer from the repository, unsupported and unwrapped.

    Kept as an explicit call rather than a module-level import: importing
    `curve_lab` must not depend on a sibling directory existing, and the
    spine layer must stay optional until the gate is fully passed.
    """
    if not (SPINE_ROOT / "pythagorean_spiral").is_dir():
        raise ImportError(
            f"the spine layer is not beside the package: {SPINE_ROOT}")
    if str(SPINE_ROOT) not in sys.path:
        sys.path.insert(0, str(SPINE_ROOT))
    import pythagorean_spiral

    return pythagorean_spiral


def chain_spans(chain, **options) -> list[dict]:
    """The chain's cubic spans, in the package's shared span format.

    `options` go straight to the spine layer's `spans()`: `max_turn`, `sharp`,
    `apsis`, `arms`. The defaults are the layer's own.

    A chain cusp is refused. `Spiral.cusp` records how many right angles it
    applied but not at which nodes, and `spans()` reads only the turn schedule,
    so a cusp's heading jump has nowhere to go in the span seam. Importing one
    would round a deliberate right angle without saying so; the caller must
    split the chain at the cusp instead.
    """
    cusps = getattr(chain, "cusps", [])
    if cusps:
        raise ValueError(
            f"this chain carries {len(cusps)} cusp(s); the span seam cannot "
            "locate a cusp's heading jump, so split the chain at the cusp "
            "before importing it")
    load()
    from pythagorean_spiral import spans as span_module

    return span_module.spans(chain, **options)


def anchors(chain) -> list[tuple[float, float, float]]:
    """Every node of the chain as `(x, y, heading)`, floats for the engine.

    These are the points a span endpoint must lie on. The layer keeps the
    exact `Fraction` and `Dir`; the engine needs floats, and the conversion is
    the only lossy step.
    """
    return [(float(x), float(y), heading.angle)
            for (x, y), heading in chain.knots()]


def design_from_chain(chain, name: str = "spine", **options) -> Design:
    """Fit one clothoid per span and return the chain as a `Design`.

    Every span endpoint is one of the chain's anchors, so the fitted chain
    turns on the anchors. A tangent jump between spans (the layer keeps one at
    a curvature reversal) is carried as a segment `corner`, not flattened.
    """
    spans = chain_spans(chain, **options)
    if not spans:
        raise interpolate.InterpolationError("the chain produced no spans")
    return interpolate.design_from_spans(spans, name=name)


def trace_from_chain(chain, name: str = "spine", width: float | None = None,
                     mirror: bool | None = None, layer: str = "ink",
                     terminals=("butt", "butt"), **options) -> Trace:
    """The chain as one named trace, optionally a ribbon of `width`."""
    return Trace(
        name=name,
        design=design_from_chain(chain, name=name, **options),
        width=width,
        mirror=mirror,
        layer=layer,
        terminals=terminals,
    )


def piece_from_chain(chain, name: str = "spine", width: float | None = None,
                     trace_name: str | None = None, layer: str = "ink",
                     terminals=("butt", "butt"), mirror: bool = False,
                     stroke: float = 1.0, contacts=None,
                     **options) -> Piece:
    """A one-trace piece from the chain: the gate's first object."""
    return Piece(
        name=name,
        traces=[trace_from_chain(
            chain, name=trace_name or name, width=width, layer=layer,
            terminals=terminals, **options,
        )],
        mirror=mirror,
        stroke=stroke,
        contacts=list(contacts or []),
    )
