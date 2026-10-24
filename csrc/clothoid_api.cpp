// csrc/clothoid_api.cpp — the C surface over Bertolazzi's Clothoids.
//
// The Python side holds no C++ types and no compiler knowledge: it loads the
// dylib this file is linked into and speaks these twenty functions. Everything
// here is either a call straight through to G2lib or a bounds and error check
// so a C++ exception cannot cross the boundary.
//
// Functions return 0 on success and a nonzero code on failure. An opaque handle
// is a ClothoidList, which is one chain, not one curve.

#include <Clothoids.hh>

#include <new>

using G2lib::ClothoidList;

namespace {
struct Handle {
  // ClothoidList's only usable constructor takes a name; there is no default.
  Handle() : list("clothoid-lab") {}
  ClothoidList list;
};
}  // namespace

extern "C" {

const char *cl_version() { return "clothoids-bertolazzi"; }

Handle *cl_new() {
  try {
    return new Handle();
  } catch (...) {
    return nullptr;
  }
}

void cl_free(Handle *h) { delete h; }

// Continue the chain from where it ended, at a stated curvature and rate.
int cl_push(Handle *h, double k0, double dk, double L) {
  if (h == nullptr || L <= 0) return 1;
  try {
    h->list.push_back(k0, dk, L);
    return 0;
  } catch (...) {
    return 2;
  }
}

// Place a segment at an absolute start point, direction and curvature.
int cl_push_at(Handle *h, double x0, double y0, double t0, double k0, double dk,
               double L) {
  if (h == nullptr || L <= 0) return 1;
  try {
    h->list.push_back(x0, y0, t0, k0, dk, L);
    return 0;
  } catch (...) {
    return 2;
  }
}

// Fit one clothoid from the current end to a point and a direction.
int cl_push_G1(Handle *h, double x1, double y1, double t1) {
  if (h == nullptr) return 1;
  if (h->list.num_segments() == 0) return 3;
  try {
    h->list.push_back_G1(x1, y1, t1);
    return 0;
  } catch (...) {
    return 2;
  }
}

double cl_length(const Handle *h) {
  return h == nullptr ? 0.0 : h->list.length();
}

int cl_nseg(const Handle *h) {
  return h == nullptr ? 0 : static_cast<int>(h->list.num_segments());
}

// out[0..3] = x, y, theta, kappa
int cl_eval(const Handle *h, double s, double *out) {
  if (h == nullptr || out == nullptr) return 1;
  if (s < 0.0 || s > h->list.length()) return 4;
  try {
    out[0] = h->list.X(s);
    out[1] = h->list.Y(s);
    out[2] = h->list.theta(s);
    out[3] = h->list.kappa(s);
    return 0;
  } catch (...) {
    return 2;
  }
}

// The exact parallel curve at a signed lateral distance, out[0..1].
int cl_eval_offset(const Handle *h, double s, double d, double *out) {
  if (h == nullptr || out == nullptr) return 1;
  if (s < 0.0 || s > h->list.length()) return 4;
  try {
    out[0] = h->list.X_ISO(s, d);
    out[1] = h->list.Y_ISO(s, d);
    return 0;
  } catch (...) {
    return 2;
  }
}

// out[0..3] = xmin, ymin, xmax, ymax
int cl_bbox(const Handle *h, double *out) {
  if (h == nullptr || out == nullptr) return 1;
  try {
    h->list.bbox(out[0], out[1], out[2], out[3]);
    return 0;
  } catch (...) {
    return 2;
  }
}

}  // extern "C"
