# Sol Cloud 19 local reproducibility check (D623)

Source: the owner-provided scripts inside
`SOL6Cloud/SOLCLOUD_19/SOLCLOUD_19_RESULTS.zip`.  Commands were run from the
archive root in a temporary extraction; no package or submission files were
changed.

`python solcloud19/exact_checks.py` returned:

```text
simultaneous_fibre_checks = 4096
E1_invariant_checks       = 4096
seed_E1_key               = 0dd0a280 e75b8c63 9636de7b 800dd0a2
seed_E3_key               = 27c07ad2 9bc61055 0680389c 8aa4dd7c
seed_gate_passes          = False
seed_gate_left            = 9bc61055
seed_gate_right           = 9c068038
```

`python solcloud19/neutral_bound.py` returned `unsat` for minimum dimensions
19, 16, 12, and **8** (15-second solver limits), and `sat` for lower queries.
The companion exact-bound script returned a dimension-7 witness, consistent
with the report.  These are finite script-level reproductions of the archive
claims; they do not prove a general impossibility or upstream reachability.
