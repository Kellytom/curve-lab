# PROTOCOL — notifying DeepSeek1 that a reduced curve is ready

The rule: **DeepSeek2 never writes the registry directly.** A reduced curve is
announced in the mailbox; DeepSeek1 reviews and adds it through the standard
path (`add-registry-curves.mjs` / the registry rows + the database). When a
whole batch is ready, the records travel as one file and DeepSeek1 adds them in
one pass.

## 1 · The announcement format

The mailbox subject line always starts with the fixed marker, so DeepSeek1 can
grep the mailbox for every announcement ever made:

    ## NURBS Project status: <one-line summary>

Body, in this order (one block per curve; append only, never edit a sent
block):

```
NURBS Project status: <name> is ready
    variant uid      c-<n>            (assigned by DeepSeek1 on add)
    variant name     <parent-name>-r11
    variantOf        <exact uid>      (<exact name>)
    reducedDegree    11
    maxMiss          0.04 % of size   (dial 0.05 % — under)
    rails            rail+ deg 11, miss 0.03 % · rail- deg 11, miss 0.05 %
    rail source      the exact offset of <exact uid> (formula X = x·w2 − d·y′)
    total miss       0.06 % (curve + rail, worst of the two axes)
    records file     reduction/out/<name>.json   (registry-row format)
```

Every number is measured, never estimated; the dial compliance is stated per
line. A record over the dial is announced as **NOT READY** with the miss shown —
DeepSeek1 does not add it.

## 2 · The two modes

**Single.** One block per ready curve, as above. DeepSeek1 reviews, adds the
record, and reports the assigned uid back in the mailbox. The variant name is a
proposal: `<parent-name>-r11`; if it collides, DeepSeek1 serialises it
(`<parent-name>-r11-2`) and says so.

**Batch.** When the pipeline has a completed batch (the first one is planned as
the 29 good knots), DeepSeek2 writes all records to one handoff file:

    reduction/out/batch-001.json

in the standard registry-row format (the same shape `add-registry-curves.mjs`
reads), one variant row per curve, each carrying `params.variantOf`,
`reducedFrom`, `reducedDegree`, `maxMiss`, `maxMissRail`. The announcement is
one block:

    NURBS Project status: batch ready — 29 records at reduction/out/batch-001.json
    dial              0.05 % of size
    worst record      <name>, miss 0.04 % — all under the dial
    parent uids       <list>
    over the dial     none (or named)

DeepSeek1 reviews the file, adds the batch to the curve repository in one pass,
and reports the assigned uid range. While the batch waits, DeepSeek2 keeps
working on the next batch; the mailbox carries the status, not the blocking.

## 3 · What makes a curve ready (the checklist, all four or NOT READY)

1. the curve is reduced to degree ≤ 11 (exact at the chosen knots);
2. `maxMiss` is under the dial;
3. every rail is fitted to degree ≤ 11 **against the exact offset**, with
   `maxMissRail` under the dial;
4. the delivered-set audit passes for this record (position degree ≤ 11,
   delivered rail degree ≤ 11, total miss stated).

## 4 · Where the files live

- `reduction/out/<name>.json` — one record per curve (single mode).
- `reduction/out/batch-<n>.json` — the batch handoff (batch mode).
- The out folder is the handoff point: DeepSeek1 reads it, DeepSeek2 never
  writes past it. The branch stays local until the task is complete, per the
  operator's separation rule.

## 5 · The acknowledgement loop

DeepSeek1 answers in the mailbox with the same marker:

    ## NURBS Project status: added <name> as <uid> (or: rejected — reason)

Rejected records come back with the reason (name collision, dial breach,
audit failure) and are either fixed and re-announced or parked in
`reduction/out/rejected/` with the reason file.
