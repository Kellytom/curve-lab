```text
Read state/HANDOFF-int.md. Read docs/HANDOVER.md only for durable detail.
Fix the heart half's sample path: the upper and lower branches end at different
points on the tip — (1.105, 0.789) and (1.105, 0.28) — a 0.508 jump in a 3.63
arc, and that jump is the whole 11.7% error on Fig. 3/4. Find the tip properly,
where the two roots merge (the discriminant of the cubic in y vanishes), and
splice both branches through it. Then the Euler fit can finally be judged.
```

Source: state/HANDOFF-int.md · 2026-11-02 · written at commit 25e7087.
