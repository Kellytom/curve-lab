// The desk records carry a width on a span trace and name their traces with the
// layer baked in ("ink/a"). The constructor used to refuse that width ("a cubic
// span trace is a hairline"), so every saved desk piece was un-buildable; the
// builder also doubled the layer to "ink/ink/a".
//
// Python twin: tests/test_regressions.py :: SpanWidthTraceTest (register 90).

import { test } from "node:test";
import assert from "node:assert/strict";
import { buildPiece, buildRibbonPiece, toPiece } from "../../app/src/lib/piece.ts";

const span = { p0: [0, 0], c1: [1, 0], c2: [2, 0], p3: [3, 0] };

const deskPiece = () =>
  toPiece({
    name: "desk",
    stroke: 0.6,
    traces: [
      { name: "ink/a", spans: [span], width: 3, terminals: ["round", "point"] },
    ],
  });

test("a span trace may carry a width", () => {
  const { groups, info } = buildPiece(deskPiece());
  assert.equal(groups.length, 1);
  assert.equal(groups[0].role, "spine");
  assert.equal(info.fit_ok, true);
});

test("a trace name that already carries its layer is not doubled", () => {
  const { groups } = buildRibbonPiece(deskPiece());
  assert.ok(groups.every((group) => group.name.startsWith("ink/a")),
    groups.map((group) => group.name).join(", "));
  assert.ok(!groups.some((group) => group.name.includes("ink/ink/")));
});

test("the width builds the two rails and the two caps", () => {
  const { groups, info } = buildRibbonPiece(deskPiece());
  const roles = groups.map((group) => group.role);
  assert.equal(roles.filter((role) => role === "rail").length, 2, roles.join(", "));
  assert.equal(roles.filter((role) => role === "cap").length, 2, roles.join(", "));
  assert.equal(roles.filter((role) => role === "spine").length, 1, roles.join(", "));
  assert.equal(info.fit_ok, true);
});
