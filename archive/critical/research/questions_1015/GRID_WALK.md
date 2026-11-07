# Question-grid walk, newly opened Pareto rounds (2026-10-15)

Sources read: RULES_WATCH.md (admission lists), HANDOFF.md tail, FILINGS.md tail, exec_r6mt/R6_PLAN.md, dossiers 41b32afc + 4086e210 ANALYSIS.md, live `benchmark show` for the 4 pareto lanes.
Live API fact (read today): currentBestScore = null on all four pareto lanes (nothing human-promoted); the benchmark JSON carries no per-round frontier rows and no rival list, so per-round rival rows are UNKNOWN from the API (rival PR pages for the new rounds not read; research/bigpicture/*rivals.md covers r2-r3 only).
Generic reference: blake3/sha3/sha256 generic normalises to ~125.0 at every round (B3 r4-r7 125.01-125.06, SHA3 r24 125.00008, SHA-256 r64 124.9915); Poseidon generic 127.009 (r56).
Tests run (3, nice 10, 1 core, <14 MB, WSL): questions_1015/t1..t3 -> dig cells GW1015-POS-CROSSOVER, GW1015-S256-PATH-EXTRAP, GW1015-SHA3-B3-NORMALISATION (each with peak_mem).

## Per-family table
| | BLAKE3 [3..7] | SHA3-256 [7..24] | SHA-256 [39..64] | Poseidon [3..56] |
|---|---|---|---|---|
| Our filed rows | r3 (review), r4 B3R4d 125.06, r5 125.00855+0.379, r6 125.038+0.641, r7 B3R7b 125.29 (B3R7 refuted F1/F2) | r7 LS1R7 124.286, r24 606bcba0 125.00008 (not_evaluable H_dp_count) | r39 368d1718 124.848+mem, r64 5790b7ac 124.9915 (not_evaluable H2 cut-count) | r3 POSR3H 30.08, r4 33.63, r5 34.74 (47.1 with memory), r56 POSGEN2 127.009 |
| Empty rows (ours) | none | r8..r23 (16) | r40..r63 (24) | r6 (run planned), r7..r55 (49) |
| Structured attack: where it stops | r2 automaton: no lever at r3 (dig, blake3_rivals.md); generic from r3 up | advantage over generic 2.33 (r6), 0.71 (r7), ~0.22 (r8, extrapolated at 0.306/round), <0.07 from r9 | r37 -64.0, r38 -38.5, r39 -0.143 bits vs generic; r40+ = generic | algebraic beats generic by 74.8 bits at r6, 69.4 at r7 (model); score reaches 127 near r22 but memory is 33 GB r6, 213 GB r7, 911 GB r8: hardware-limited at r7/r8 |
| Work/round grows slower than C(r)? | No: normalised slope +0.0011 bit/round r4-r7 | No (r24 125.00008) | No (r64 124.9915) | n/a: algebraic score grows ~4.4 bit/round, generic fixed |
| Rival rows | UNKNOWN (r3: we are the only entry) | UNKNOWN | UNKNOWN | UNKNOWN |

## Grid answers, one line each
Stage 1 Idea
- New path or re-pricing? Each new round is its own row (new path per row); same method re-rendered is a row filing. Evidence: submissionAdmission lists.
- Home run? Poseidon r6/r7 algebraic: ~53 / ~58 vs 127. Nothing comparable on the other three (all <= 0.7 bit).
- Missing lenses? UNKNOWN for the new rows (LENSES.md not walked here; lead 8).
- Transfer from another hash? SHA3 LS1 convention -> r7 done; LS1 at r8 untested (lead 6); SHA-256 path attack to r40 closed by GW1015-S256-PATH-EXTRAP.
- Dismissed by argument? B3 r2 automaton at r3 closed by dig, not re-tested on the r4-r7 band (UNKNOWN, lead 8).
- Boring details everyone copies? Round constants C(r): only Poseidon 216+21r is printed in the contract text we read; blake3 C(7)=1470 and sha3 C(24)=6504 appear in filings; recount per row (lead 7).
- Printed conditions hold on the witness? Kernels only: r64 0 diffs on 8,197 msgs, B3R7 0 diffs, r24 replay; no table audit on new rows.
- Mill tailings? The Lemma-2 rulings: one refuted bound (B3R7 F1/F2) sits in the shared text of 4 B3 rows + S256 r64 + SHA3 r24 (lead 1).
- Birthday/match lens? Generic rows are rho on the full digest; no cheaper match seen at Poseidon 127.009.
- Boring edges? 1 MiB program limit forces a rolled B3 r7; Orchard input = two 32-byte LE field encodings; runner digest(b"") bug: declare no experiments.
Stage 2 Measure
- Measured or copied? Poseidon r6 is extrapolated (no run); t1-t3 are arithmetic on filed numbers (COMPUTED).
- Preregistered/control? r3 validation reproduces six exec_r3f collision lines byte-identical (R6_PLAN s3); r6 not run.
- Unit right? Poseidon score = log2(time/C)+log2(MiB); B3/SHA rows charge bytes above 2^20: normalise before comparing rows.
- GPU? Poseidon r6 is RAM/FFT-bound (36.5 GB); generic rows are tiny-memory rho (GPU-able, not the bottleneck).
- Counted every case? Not yet: B3R7/S256R64/SHA3R24 success bounds used midpoint/Poisson/binomial shortcuts (12:35 rulings).
- Same quantity same way? FILINGS r6/r5 lines print +0.86686 (r7 template), cosmetic.
- Conventions? Register-file declarations (800/1856/2192/128), 1 MiB code limit, 2^20 memory allowance: all priced in the filings.
- Joint vs product? Poseidon plan chooser couples N, memory and the claim scope text (4086e210).
- Smaller count, costlier route? Poseidon plain-2^28 plan: -33% time, -4.3 GB but needs a kernel change; not net-free.
Stage 3 Build
- Exact count not bound? Open for the Lemma-2 v2 rewrite (proven Darboux/binomial bounds).
- Lean / checker? Lean; prefile_check, memgate, R21 PASS on filed packages.
- Credits? Deps same-challenge only, <= 20, id younger than ~5 min is "not found".
- Memory rule? Poseidon r6 claim 2^35.087 B; B3 r6 2^20.64; computed per filing.
Stage 4 File
- Lead or open a path? Every new round is open ground; first-at-max-round held on all 4 lanes but all four max-round filings are under rulings (B3R7 refuted, S256R64/SHA3R24 not_evaluable, POSGEN rejected then POSGEN2 filed).
- Retry worth it? Only after the ruling names the issue; refile per line.
- Backup / merge plan? Unchanged (MERGE_FILING_PLAN.md).
Stage 5 After
- Why did it fail? 41b32afc: judge-derived H4 (Lemma 2 conditioning; no fatal; H1-H3 plausible). 4086e210: claim.json scope N=3145728 vs proof 2^21 (template numbers for the wrong plan); text fix filed as POSR3H.
- How did it die, what do neighbours say? H4 and F1/F2 sit in the shared Lemma-2 block (one math fix serves 6 rows); the 4086e210 template bug could recur wherever a rows==2 plan is chosen; POSR4M/5M checked consistent.
- Who shaved us? UNKNOWN on the new rows (no rival data).
- Partners on the best job? Lemma-2 v2 math = pure-math ask for cloud; Poseidon r6 run = owner decision pending (cloud box).
- Handoff/credits? Not touched (rule).

## Top 8 leads (value / effort)
| # | Lead (question) | Why it matters | Cheapest test (<=10 min, 1 core) | Expected value |
|---|---|---|---|---|
| 1 | Does Lemma-2 v2 (upper Darboux MGF; K dominated by Binomial; DP count exactly binomial) clear every sibling? | One shared defect gates B3 r4-r7, S256 r64/r39, SHA3 r24 | Evaluate the v2 tail bound in exact/interval arithmetic with each family's parameters; confirm P >= 0.39 margin survives | 6 rows from refuted/not_evaluable to reviewable; ~0-0.1 bit cost |
| 2 | Does portkit render SHA3 r8..r23 / SHA-256 r40..r63 / Poseidon r7..r55 with 0 diffs vs the organizer digest? | 89 empty rows, each "first at row" at ~125.0 / 127.0 | Render SHA3 r8 and SHA-256 r40 kernels, diff vs organizer digest on 256 msgs | 0 bits, +89 rows once lead 1 clears (r24/r64/r56 are the same code) |
| 3 | Can Poseidon r7 be executed (213 GB live, a=31 <= 32 two-adicity) on a rented >=256 GB box? | Algebraic r7 ~57.6 vs 127 | Re-run t1 with the exact r6 formula at r7; price 256 GB x multi-day; check the 2^30 twiddle table fits | ~69 bits on the r7 row (price UNKNOWN) |
| 4 | Start Poseidon r6 as planned (52.9-53.9 vs 127) | Largest bit gain available today | None needed (plan ready, r3 validated); owner go | ~73 bits on r6, ~4-5 days |
| 5 | Streamed/chunked algebraic variant (4x less memory, ~2x time) for r7-r9? | Memory counts 1:1 with time; r8 needs 911 GB as built | Model score(mem cap) with time multiplier (M0/M)^e, e = 0.3..1 | up to ~60 bits on r8/r9; design risk high |
| 6 | SHA3 r8: does LS1-style still beat generic (extrapolated 0.22 bit)? | Only SHA3 band with structure left | Price the LS1R7 sheet at r8 (one more round) | ~0.2 bit on r8 (a structured path) |
| 7 | Do our C(r) constants equal the organizer's for every row? | Normalisation shifts a whole row | Recompute C(r) per admitted r from the cost-model text; compare with filings | up to +-1 bit/row (UNKNOWN until checked) |
| 8 | B3 r7 partial unroll (2 rounds per loop body) between rolled 125.29 and straight 125.054+0.867; also re-test r2 automaton at r4+ | Rolled body costs +0.236 bit | Size model: bytes per round x unroll vs 1,048,576 B | 0.1-0.2 bit on r7 |

## New questions (also appended to QUESTIONS.md)
1. Which C(r) does each family's cost model print, and do our filings use them (lead 7)?
2. Once per-round growth is ~5x, is memory not time the binding limit of an algebraic attack; what time/memory trade exists (lead 5)?
3. At which round does each filed structured line cross generic ~125.0, and how many bits remain at the last row (r39: 0.143; sha3 r8: ~0.22)?
4. Which rivals hold which per-round rows (API gives currentBestScore=null, no frontier list)?
