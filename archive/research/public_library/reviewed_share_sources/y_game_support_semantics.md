# Required support, allowed support and a screen are different experiments

This is a scientific extract, not a copy of the operational research share. Kepler's `FROM_KEPLER_1024/game_speed/REVIEW.md` was read completely: 8,002 bytes, SHA-256 `fdee2c7e7bd1333123a256e3cf772c373a3dba1ce3e037ed2565731744c42fd0`. Four short companion scripts (`dariia_vs_census.py`, `conflicts.py`, `expand_check.py`, `sx_bench.py`) and both conflict logs were read completely. Only the question/verdict header of `schedexact/sched_exact_fix.py` was read in this pass; this is not an implementation soundness audit.

## The exact implication, not a performance claim

Fix the round count R, word width, message-pair domain and actual SHA-256 schedule recurrence. Let D be the required support among message words 0..15, and L be a proposed support among expanded words 16..R-1. Compare:

- Required-expanded problem: the message support is exactly D and the expanded support is exactly L.
- Allowed-expanded problem: the message support is exactly D and the expanded support is a subset of L.

Every solution of the required-expanded problem solves the allowed-expanded problem. Consequently UNSAT for the allowed-expanded problem excludes the required-expanded problem under the same other assumptions. SAT for the allowed problem does not establish SAT for required L: independently expand its concrete messages and label their actual support L'. It establishes a required-support witness for L', not every superset of L'. A screen outcome has no such implication until the screen's mathematical direction and assumptions are established.

The asymmetry has a simple finite counterexample. If the sole permitted witness has actual support {22,24}, then it meets allowed L={22,24,25}, but not required L={22,24,25}. A true SAT and a true UNSAT can therefore coexist under the same support-only map key. This is not a contradiction between solvers.

## What the historical review reported

The review distinguishes required census support, allowed dense-lattice support and an external screen. Its historical screen comparison reports 45 overlapping cells: eight agreeing labels and 37 disagreeing labels. These counts were not recomputed from the original large map in this publication review. They are not a revision of the separate 3,063-support comparison on different inputs.

Two retained R40 logs report UNSAT for explicit schedule questions. The first records d3 forced to zero despite requiring word 3 to differ; the second records a zero sigma contribution for word 6. Reading those logs does not independently validate elimination, the oracle or an UNSAT certificate. The source's brief account must not replace the exact instances.

The review also retracts its original interpretation of visual bands as shift orbits. Its later projection analysis attributes much of the band structure to neighboring features with similar projection steps and block sampling. A visible stripe is not itself a feasibility theorem. The separate 3D map is outside this library's implementation scope.

## A fresh recount of the saved benchmark, not a fresh solver run

`FROM_KEPLER_1024/game_speed/sx_bench.tsv` has 220 six-column records, 15,614 bytes, SHA-256 `ed71c90f87db48e93eba8c39b5de97e78214053c8bb0867730ffd54a32d2f1ff`. Every record was parsed for this recount. The columns are incoming label, R, message support, expanded support, returned label and elapsed seconds.

| Incoming group | Rows | Returned SAT | Returned UNSAT | UNKNOWN | Skipped | Mean seconds, decided only | Maximum seconds, decided only |
|---|---:|---:|---:|---:|---:|---:|---:|
| SAT-labeled | 60 | 4 | 9 | 47 | 0 | 1.807692 | 19.75 |
| UNSAT-labeled | 80 | 0 | 75 | 4 | 1 | 0.302667 | 1.00 |
| EDGE | 80 | 1 | 47 | 32 | 0 | 0.424792 | 0.68 |

The 48 decisions among 80 EDGE rows reproduce the reported 60 percent for this saved sample. They do not estimate the rate over all cells. `sx_bench.py` uses `time.time()` around the child invocation, so these are elapsed wall times including invocation overhead, not CPU-time or contest operation counts. The driver samples selected pools with seed 7 and uses four concurrent one-thread requests. The driver was inspected, not executed here. Counts verify the saved labels, not their mathematical correctness. A historical claim of universal speed-up would require comparable models, instances, budgets and hardware.

## How to use the lesson

Store required and allowed support separately, plus whether the object is a schedule witness, a pinned-member state question or a full collision. Include width, round count, initial-state law, exact pins, objective cap and encoder identity in the experimental key. For a returned SAT, derive actual support from both messages rather than trusting the requested envelope. For a returned UNSAT, preserve the exact formula and certificate where available. UNKNOWN remains undecided.

The existing support-overlap replay kit checks the older comparator against synthetic fixtures. It does not recount the large historical map, replay this benchmark's solver campaign or certify either encoder. This source note adds a mathematical implication and a saved-table recount without promoting those narrower checks into attack results.
