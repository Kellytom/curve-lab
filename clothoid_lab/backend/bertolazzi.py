"""The compiled Clothoids library through ctypes.

The dylib is built by `scripts/build-native.sh` from `vendor/Clothoids`. This
module is the only place that knows the C names, the argument types, or the
error codes, and it converts every call into either a value or a Python
exception. Nothing above it sees ctypes.

Positions, angles and curvature come from the library itself, so this backend
can offer the exact parallel curve (`X_ISO`, `Y_ISO`) rather than offsetting a
sample by a rotated tangent.
"""

from __future__ import annotations

import ctypes
import os
from pathlib import Path

import math

NAME = "bertolazzi"
_ROOT = Path(__file__).resolve().parents[2]
LIB_PATH = Path(os.environ.get("CLOTHOID_LIB", _ROOT / "build" / "libclothoidlab.dylib"))

_lib = None


class BackendError(RuntimeError):
    pass


def _bind():
    """Load the library and declare every signature once."""
    global _lib
    if _lib is not None:
        return _lib
    if not LIB_PATH.exists():
        raise BackendError(
            f"{LIB_PATH} is missing; run scripts/build-native.sh, or set "
            "CLOTHOID_BACKEND=pyclothoids to use the wheel"
        )
    lib = ctypes.CDLL(str(LIB_PATH))

    lib.cl_version.restype = ctypes.c_char_p
    lib.cl_new.restype = ctypes.c_void_p
    lib.cl_free.argtypes = [ctypes.c_void_p]

    lib.cl_push.argtypes = [ctypes.c_void_p] + [ctypes.c_double] * 3
    lib.cl_push.restype = ctypes.c_int
    lib.cl_push_at.argtypes = [ctypes.c_void_p] + [ctypes.c_double] * 6
    lib.cl_push_at.restype = ctypes.c_int
    lib.cl_push_G1.argtypes = [ctypes.c_void_p] + [ctypes.c_double] * 3
    lib.cl_push_G1.restype = ctypes.c_int

    lib.cl_length.argtypes = [ctypes.c_void_p]
    lib.cl_length.restype = ctypes.c_double
    lib.cl_nseg.argtypes = [ctypes.c_void_p]
    lib.cl_nseg.restype = ctypes.c_int

    lib.cl_eval.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.POINTER(ctypes.c_double)]
    lib.cl_eval.restype = ctypes.c_int
    lib.cl_eval_offset.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double,
                                   ctypes.POINTER(ctypes.c_double)]
    lib.cl_eval_offset.restype = ctypes.c_int
    lib.cl_bbox.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_double)]
    lib.cl_bbox.restype = ctypes.c_int

    _lib = lib
    return lib


def probe() -> str:
    """Whether this backend can load, as a short sentence either way."""
    try:
        lib = _bind()
        return f"ok: {lib.cl_version().decode()}"
    except Exception as exc:
        return str(exc)


def load():
    return _bind()


_FOUR = ctypes.c_double * 4


class Curve:
    """One chain, held as a ClothoidList, addressed by arc length."""

    __slots__ = ("_h", "_len", "segments")

    def __init__(self, segments, anchor):
        lib = _bind()
        handle = lib.cl_new()
        if not handle:
            raise BackendError("the library could not allocate a chain")
        self._h = handle
        self.segments = segments
        x = float(anchor.get("x", 0.0))
        y = float(anchor.get("y", 0.0))
        t = float(anchor.get("angle", 0.0))
        try:
            for i, seg in enumerate(segments):
                if i == 0:
                    rc = lib.cl_push_at(handle, x, y, t, seg["k0"], seg["kd"], seg["length"])
                else:
                    rc = lib.cl_push(handle, seg["k0"], seg["kd"], seg["length"])
                if rc != 0:
                    raise BackendError(f"the library refused segment {i} (code {rc})")
            self._len = float(lib.cl_length(handle))
        except Exception:
            lib.cl_free(handle)
            self._h = None
            raise

    def close(self):
        if getattr(self, "_h", None):
            _bind().cl_free(self._h)
            self._h = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    @property
    def length(self):
        return self._len

    def _eval(self, s):
        out = _FOUR()
        rc = _bind().cl_eval(self._h, float(s), out)
        if rc != 0:
            raise BackendError(f"eval failed at s={s} (code {rc})")
        return out[0], out[1], out[2], out[3]

    def point(self, s):
        x, y, _, _ = self._eval(s)
        return (x, y)

    def tangent(self, s):
        return self._eval(s)[2]

    def kappa(self, s):
        return self._eval(s)[3]

    def offset_point(self, s, distance):
        out = (ctypes.c_double * 2)()
        rc = _bind().cl_eval_offset(self._h, float(s), float(distance), out)
        if rc != 0:
            raise BackendError(f"offset eval failed at s={s} (code {rc})")
        return (out[0], out[1])

    def bounds(self):
        out = _FOUR()
        rc = _bind().cl_bbox(self._h, out)
        if rc != 0:
            raise BackendError(f"bounds failed (code {rc})")
        return (out[0], out[1], out[2], out[3])


def build_curve(segments, anchor):
    return Curve(segments, anchor)


def describe() -> str:
    return f"{NAME} ({LIB_PATH.name})"
