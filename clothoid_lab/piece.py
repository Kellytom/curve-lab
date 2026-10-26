"""A piece: several named traces, a mirror, and one SVG.

The engine's `Design` is one chain. An ornament is usually more than one: a
half-stroke, a band, two parallel edges, and the mirror of the ink. `Piece`
holds those traces in one object and hands the SVG writer a single set of
groups, so the page, frame and y-flip are decided once.

This is the W01 model. Terminals and the fleur grammar build on it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from . import bezier, engine, svg
from .model import Design
from .offsets import build_rails


@dataclass
class Trace:
    """One named chain in a piece, optionally with a ribbon width."""

    name: str
    design: Design
    width: float | None = None
    # None follows the piece; True/False overrides it. A centred band usually
    # sets False so the mirror does not draw it twice.
    mirror: bool | None = None
    layer: str = "ink"

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("a trace needs a name")
        if self.width is not None and self.width <= 0:
            raise ValueError("trace width must be positive")
        if not self.layer.strip():
            raise ValueError("a trace needs a layer")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "layer": self.layer,
            "width": self.width,
            "mirror": self.mirror,
            "design": self.design.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Trace":
        return cls(
            name=str(data["name"]),
            design=Design.from_dict(data["design"]),
            width=None if data.get("width") is None else float(data["width"]),
            mirror=data.get("mirror"),
            layer=str(data.get("layer", "ink")),
        )


@dataclass
class Piece:
    """A named set of traces, mirrored as one drawing."""

    name: str
    traces: list[Trace]
    mirror: bool = False
    stroke: float = 1.0

    def __post_init__(self):
        if not self.traces:
            raise ValueError("a piece needs at least one trace")
        if self.stroke <= 0:
            raise ValueError("stroke width must be positive")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "mirror": self.mirror,
            "stroke": self.stroke,
            "traces": [trace.to_dict() for trace in self.traces],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict) -> "Piece":
        return cls(
            name=str(data.get("name", "untitled")),
            mirror=bool(data.get("mirror", False)),
            stroke=float(data.get("stroke", 1.0)),
            traces=[Trace.from_dict(t) for t in data.get("traces", [])],
        )


def _mirror_spans(spans: list[dict]) -> list[dict]:
    """Mirror every control point across x = 0, preserving the span order."""
    mirrored = []
    for span in spans:
        copy = dict(span)
        for key in ("p0", "c1", "c2", "p3"):
            x, y = span[key]
            copy[key] = (-x, y)
        mirrored.append(copy)
    return mirrored


def render_piece(piece: Piece, tol: float = 0.02, prec: int = 4,
                 margin: float = 5.0, max_spans: int = 64, split: int = 2,
                 backend: str | None = None,
                 page: tuple[float, float] | None = None,
                 frame: tuple[float, float] | None = None,
                 view: str | None = None) -> tuple[str, dict]:
    """Build every trace, mirror where asked, and write one SVG."""
    groups: list[tuple[str, list[dict], float | None]] = []
    report = []

    for trace in piece.traces:
        chain = engine.build(trace.design, backend=backend)
        spine, fit = bezier.fit_chain(
            chain, tol=tol, max_spans_per_segment=max_spans, split=split,
        )
        distances = list(trace.design.offsets)
        if trace.width is not None:
            distances.extend([trace.width / 2.0, -trace.width / 2.0])
        rails = build_rails(
            chain, distances, tol=tol,
            max_spans_per_segment=max_spans, split=split,
        )

        base = f"{trace.layer}/{trace.name}"
        groups.append((base, spine, None))
        for rail in rails:
            groups.append(
                (f"{base} rail {svg.num(rail['distance'], 3)}",
                 rail["spans"], rail["distance"])
            )

        entry = {
            "name": trace.name,
            "layer": trace.layer,
            "fit_error": fit["error_max"],
            "rails": len(rails),
            "mirrored": piece.mirror if trace.mirror is None else bool(trace.mirror),
        }
        report.append(entry)

        if entry["mirrored"]:
            groups.append((f"{base} mirrored", _mirror_spans(spine), None))
            for rail in rails:
                groups.append(
                    (f"{base} mirrored rail {svg.num(rail['distance'], 3)}",
                     _mirror_spans(rail["spans"]), rail["distance"])
                )

    text = svg.document(
        piece, groups=groups, prec=prec, margin=margin,
        page=page, frame=frame, view=view,
    )
    info = {
        "piece": piece.name,
        "traces": report,
        "fit_ok": all(t["fit_error"] <= tol for t in report),
        "mirror": piece.mirror,
    }
    return text, info
