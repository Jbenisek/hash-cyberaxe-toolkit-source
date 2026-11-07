# SHA-256 seam-tool positive control and model differences

Original filename: `FINDINGS_2026-10-28_SEAM_AUDIT.md`.
Original SHA-256: `8d1c549a8c66eb3051851c560990d74063c182418ca2a98947737ce28b7d7e1e`.
Original author label Kepler; complete archival review 2026-10-29. No solver was run in this publication pass.

The 2026-10-28 audit describes a known 38-step witness pinned into a separately generated seam cell by carrying variable names across the two maps. The 1,536 unit clauses fix two 512-bit message blocks and the two 256-bit starting states. The audited model uses a free common chaining value, signed differences, a nontriviality condition and no symmetry breaker. The pinned cell was reported SAT in 0.41 seconds, decoding to the same pair; words 7, 8, 9, 10, 11 and 15 differ, outputs agree, and the independent verifier reported success. The same witness met all rows of both tested fast-grid seam descriptions with zero mismatches. This is a positive control for that free-CV model, not a standard-IV collision claim.

Three differences between the two encoders explain why apparently identical cell labels can disagree:

1. One seam generator's gap G frees G+1 rows; the fast generator frees G rows. Thus a hybrid seam starting at 17 with label g5 frees rows 17 through 22, while the fast g5 seam frees rows 17 through 21. The same-sized fast seam is g6. A witness may happen to satisfy both, but the formulas are not identical.
2. The hybrid model leaves message words free in its last four rows while requiring zero state differences there. The fast model imports the second characteristic's final A/E/W conditions. It is stricter and can add UNSAT cells without refuting the looser construction.
3. The two nontriviality settings differ, but the pinned characteristic already contains differences in the relevant W8/W9 positions; the audit found this discrepancy harmless for this positive control.

The source reports five repeat fast-grid UNSAT decisions, ranging from 1.6 to 8.6 seconds, and says seven marked cells were all at gap widths at most two. These are recorded solver verdicts for those exact constrained models; this publication pass did not check proof certificates. Repeating the same CNF and seed is principally a reproducibility check. An undecided larger-budget run would remain UNKNOWN, not establish an edge or a theorem. The audit reports no discovered soundness defect in those particular fast cells, which pinned no concrete values.

Operational paths, queue changes and process instructions from the original have been excluded.
