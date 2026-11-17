"""Read or set a PNG's physical resolution, with no dependency.

A Chrome screenshot carries 96 dpi. A plate is exported at 300 dpi so a
3000-pixel-long-side image inserts in LibreOffice at 10 inches (254 mm) instead
of 31 inches. The PNG stores this in a `pHYs` chunk: pixels per metre, unit 1.

    from png_dpi import set_dpi, read_dpi
    set_dpi(path, 300)

The chunk is rebuilt with the right CRC; every other byte of the file is kept.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunks(data: bytes):
    if not data.startswith(SIGNATURE):
        raise ValueError("not a PNG")
    offset = len(SIGNATURE)
    while offset < len(data):
        (length,) = struct.unpack(">I", data[offset:offset + 4])
        kind = data[offset + 4:offset + 8]
        body = data[offset + 8:offset + 8 + length]
        crc = data[offset + 8 + length:offset + 12 + length]
        yield kind, body, crc
        offset += 12 + length


def _pack(kind: bytes, body: bytes) -> bytes:
    return (struct.pack(">I", len(body)) + kind + body
            + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF))


def read_dpi(path) -> int:
    for kind, body, _crc in _chunks(Path(path).read_bytes()):
        if kind == b"pHYs":
            x, _y, unit = struct.unpack(">IIB", body)
            if unit != 1:
                return 0
            return round(x * 0.0254)
    return 96


def set_dpi(path, dpi: int = 300) -> int:
    """Replace or add `pHYs`; returns the dpi written."""
    path = Path(path)
    data = path.read_bytes()
    metres = round(dpi / 0.0254)
    body = struct.pack(">IIB", metres, metres, 1)
    out = [SIGNATURE]
    inserted = False
    for kind, chunk_body, _crc in _chunks(data):
        if kind == b"pHYs":
            continue
        if kind == b"IDAT" and not inserted:
            out.append(_pack(b"pHYs", body))
            inserted = True
        out.append(_pack(kind, chunk_body))
    if not inserted:
        raise ValueError("no IDAT chunk: not a usable PNG")
    path.write_bytes(b"".join(out))
    return dpi
