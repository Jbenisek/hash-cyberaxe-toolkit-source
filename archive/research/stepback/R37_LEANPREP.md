# R37 lean preprocessing peak (2026-10-13)
Instance (COMPUTED): research/grok/work/job112_dense_finish/dense_full.cnf, 107,359 vars / 370,173 clauses (5 unit, 118,528 binary, 251,640 ternary; 991,981 literals). Same instance for every row. Single thread, `nice 10 /usr/bin/time -v`, 600 s cap, WSL Ubuntu (kissat 4.0.x, cadical, minisat, cryptominisat5 from distro). Raw logs and run.sh: research/stepback/leanprep/. No row reached SAT/UNSAT in 600 s (the instance is hard); peaks are at the cap, i.e. after learning has run 10 minutes.
| setting | max RSS bytes | log2 | result |
|---|---:|---:|---|
| kissat default (--time=600) | 161,722,368 | 27.27 | UNKNOWN |
| kissat --plain | 181,173,248 | 27.43 | UNKNOWN |
| cadical --plain | 292,995,072 | 28.13 | cap |
| cryptominisat5 1 thread, occsimp/sls/bva/intree off | 269,574,144 | 28.01 | INDETERMINATE |
| minisat -no-pre | 342,400,000 | 28.35 | cap |
| kissat --basic (no reduce) | 2,946,197,000 | 31.46 | UNKNOWN (learnt clauses never deleted) |
Lowest measured: kissat default, 2^27.27. Lighter solvers and "plain" modes are NOT lighter (reduction/inprocessing keeps the learnt database small). Server measurements (S006) gave kissat 95-114 MB on the same family, so 2^26.5-2^26.8 is also observed; local number is the conservative one.
## Theoretical floor (COMPUTED from the CNF)
Clause database alone: 4 B/literal = 3,967,924 B; +4 B header/clause = 5,448,616 B (2^22.38); with 8 B header 6.93 MB (2^22.72); with solver watch lists about 9.9 MB (2^23.2); per-variable state about 10.7 MB. So floor ~ 2^22.4 to 2^23.3. A solver cannot get under 2^20 on this instance (needs >= 2^22.4), so the preprocessing penalty cannot be removed, only shrunk to >= 2.4 bits.
## Score formula (exact)
score = time_log2 + max(0, log2(PEAK) - 20), PEAK over ALL phases (preprocessing, characteristic derivation, Step-1 solve, development, online). time_log2 = 60.99099 is the claimed time and stays. The online 2^19.21 is below 2^20 and contributes 0 already, so there is NO "-0.21": the peak REPLACES 2^19.21 and the term is log2(PEAK)-20.
- peak 2^27.27 (lowest measured, this instance): 68.26
- peak 2^28 (bound already chosen for r38 derivation, 2^27.56 measured): 68.99
- peak 2^22.4 (theoretical floor, unreachable in practice): 63.4
- break-even against best other entry (Th0rgal 73.94225): log2(PEAK) = 20 + 12.95 = 32.95, i.e. PEAK <= ~8.3 GB.
Implication (INFERRED): r37 stays a WIN over 73.94 with any honest preprocessing peak up to ~2^32.9 B; the cost of declaring memory is 6-8 bits, not a loss. The rulings fail the entry for OMITTING preprocessing memory, so the fix is to declare it (bound 2^28 covers all measured r37/r38 phases: 2^27.56 derivation, 2^27.27 dense solve), not to shrink it. Shrinking from 2^28 to 2^27.27 buys 0.7 bit; splitting into smaller sequential sub-instances could cut toward the 2^23 floor (up to ~5 bits) but is untested and would add time.
## Not measured
Candidate 39-step characteristic derivation with CMS 12-thread, Step-1 solve, development runs of the real r37 pipeline (no r37 stand-in CNF exists besides dense_*); splitting experiment; picosat/glucose (not installed).
