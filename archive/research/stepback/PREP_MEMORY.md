# Preprocessing-phase memory: measured peak RSS (2026-10-13, WSL Ubuntu, nice 10, 1 thread each, `/usr/bin/time -v`, 600 s cap)
| package | phase / instance | solver | max RSS bytes | log2 | wall | result |
|---|---|---|---:|---:|---|---|
| r38 | pair search, file a (dense_chi38_e16_new.cnf, 110,437 v / 383,938 c) | kissat | 118,464,512 | 26.82 | 10:00.08 | UNKNOWN (cap) |
| r38 | same | cadical | 149,368,832 | 27.15 | 10:00.05 | no result (cap) |
| r38 | pair search, file b (dense_chi38_elist_new.cnf, 110,469 v / 385,435 c) | kissat | 121,495,552 | 26.86 | 10:00.07 | UNKNOWN (cap) |
| r38 | same | cadical | 139,743,232 | 27.06 | 8:28.98 | SAT |
| r38 max over measured phases | | cadical, file a | 149,368,832 | 27.15 | | |
| r37 | no stand-in instance exists in the package or under research/ | - | not measured | - | - | proof states the SAT solve and char search were not rerun (allowances A_S, A_C only) |
Notes: r38 CNFs are in research/grok/work/job115_r38_pair/ (counts match Appendix C: 110,437 v; clauses 383,913 base, +25/+1,522 for the file-specific pins/selection). Raw logs: research/stepback/prepmem/*.err.
Not measured: Appendix C's 39-step characteristic derivation (CryptoMiniSat 12 threads, STP-to-CNF; the CNF is not in research/; no CMS peak RSS), the Step-1 solve, development runs, the 35-step predecessor re-run. Those peaks are likely larger than 150 MB (CMS at 12 threads) but are unmeasured.

## Added 2026-10-13 (R38M5): characteristic-derivation instance, single thread
CNF = /root/llw24/work/ex39_search_90.cnf (ex39_search.py 90; 132,265 v / 771,857 cl; the file CMS solved in 772.58 s on 12 threads, cms.err). MEASURED, `nice 10 /usr/bin/time -v`, 900 s cap, side by side:
| solver | max RSS bytes | log2 | wall | result |
|---|---:|---:|---|---|
| cadical 2.1.3 | 198,053,888 | 27.56 | 1:52.11 | SAT |
| kissat 4.0.3 | 188,432,384 | 27.49 | 7:33.76 | SAT |
Logs: stepback/prepmem/dv_*.err. Largest preprocessing peak now 2^27.56; bound chosen 2^28. Step-1 solve and development remain unmeasured (assumed no larger).
