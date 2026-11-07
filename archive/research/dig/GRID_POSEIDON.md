# GRID_POSEIDON - Poseidon Pareto row dig (generic part and algebraic part)

Created 2026-10-17. Before this file the dig held Poseidon only as the exploratory rows r1/r2 (hash poseidon-r1, poseidon-r2: round x lane x layer x Q1..Q4, universe group PO in coverage.py) and a few door cells for r3/r4/r5. The Pareto rows r3..r56 had no grid. Each Pareto row is its own dig site: a row r is a Poseidon with r partial rounds (Orchard P128Pow5T3: 3 lanes, x^5 S-box, 8 full rounds); the generic collision line and the algebraic line are two different attacks on the same row and are dug separately here.

Status letters follow SCHEMA.md (B BEDROCK, C COMPUTED, L LOCAL_ONLY, O OPEN). Evidence is by path. Rival rows are read as data from the board snapshot only.

## Part 0 - the two attack structures (what a row is made of)

| item | generic line (rho / route2c, route2d2) | algebraic line (line restriction) |
|---|---|---|
| idea | birthday-type collision search over the partial-round state form with two free rounds spent on making lanes 1,2 offset-free; distinguished points, table in 2^20 bytes | restrict the input to a line, the digest becomes a polynomial of degree m=(5^(6+r)-1)/2 in the line parameter; find collisions via S^((p-1)/2) mod g (Euler-exponent powering), then half-gcd for roots |
| unit of cost | field ADD+MUL ops in the step; step = 140 + 12r ops (partial round 12 = 3 + 4M + 5A; four full-round layers 6M+6A+3; entry 12 / exit 7 of the partial form; hidden-basis cut saves 4) | stages A..I in ledger.py: NTT (2^a or 3*2^a), Barrett squarings, half-gcd; K trials charged |
| score shape | S*(N+3.75), S = 1.393*2^127; about 126.2-126.8 for rows 7..56 (route2d2 staged ~126.23-126.30; filed route2 126.71-126.81) | r3 38.6, r4 42.9, r5 47.1, r6 52.8, r7 58.07, r8 62.36 (ledger K=1/K=2); modelled r9..r21 up to ~124; cross-over with generic at r21/r22 |
| memory | 2^20 bytes table + code (memory term 0) | tens of GB to 2^70 B: memory term max(0, mem_log2 - 20) dominates from r5 |
| binding risk | premise H1 (average over rho0), finite preprocessing statement (H2), 10-bit walk statement | per-trial success bound (plane genus bound r<=7; complete-intersection bound of Grok 134 for 8..11), coin draws vs probability space, lane_experiments evidence |
| sources | research/levers_1016/dig_posgen, research/rows_1016/factory/posgen_route* | research/poseidon/algebraic_paper/ledger.py, levers_1016/pos_alg_rows, r7alg_refile, posledger, pos_memcut, pos_far_rows |


## Part 1 - generic Poseidon rows (route2c / route2d2)


Generated 2026-10-17 by `research/dig/new/gen_new_cells.py` + `gen_grid_md.py` (cells in `research/dig/new/poseidon-generic.jsonl`, merged into CELLS.jsonl 2026-10-17). Poseidon generic collision rows r3..r56 (rho route2c/2d2 template, factory research/rows_1016/factory/posgen_route*). Orchard P128Pow5T3, r = number of partial rounds; 8 full rounds (0..3 and 60..63 in the filed numbering) around r partial rounds.

Each row is its own dig site with the same needs as the older sites: ledger, memory, packing, success slack, premise, preprocessing, rival, levers, judge findings, neighbour transfer, structure. Fourteen questions per row (Q1..Q12 shared by all families, Q13/Q14 family specific). Cell ids are `PR-poseidon-generic-r<R>-<Qn>`; hash field is `poseidon-r<R>`.

### The question template

| Q | name | question (R = round count) |
|---|---|---|
| Q1 | cost ledger | Cost ledger of the row poseidon-generic rR: where does every op go, term by term (per step / per trial / per batch, plus recovery, setup, preprocessing), and what is the exact total of the filed or best program? Give shares in percent and bit value of one op. |
| Q2 | dispatch and control charge | Which control ops does rR charge (loop counter, branch, DP/filter test, handlers, dispatch, loads/stores, register moves) and is each charged at best-case exact count, per the organizer cost model as written? |
| Q3 | memory peak and drain | What is the peak-memory phase of rR (which stage, which buffers live), what is the measured or modelled peak in bytes, and do drain / stream / alias / free-early options lower the peak that binds (peak = max over stages, so all binding stages must drop)? |
| Q4 | table / entry packing | How is the table, entry or code packed on rR (bits per entry, entries, bytes per instruction, code bytes versus table slots), and what does a different packing change in the ledger? |
| Q5 | success-bound slack | How far is the proven success probability of rR above the required premise, and what time bit does the slack cost (which proof terms F1.. and which are looser than needed)? |
| Q6 | premise and evidence | What premise (H-statements, probability model, statistic) does rR rest on, what organizer-executed evidence supports it, and what would a judge need to see that is missing? |
| Q7 | preprocessing / advice | What preprocessing, advice or nonuniform data does rR use, how is it charged (time, memory, advice size), and is any of it free or hidden? |
| Q8 | rival best on this row | Who holds the best rival entry on rR on the board, at what score, and where does it save against us (ledger term by term, convention, premise)? If no rival is on the row, record the empty square. |
| Q9 | levers applied vs unapplied | Which levers are applied in our rR entry, and which recorded levers (LEVERS.md, levers_1016/*/RESULT.md) are not applied, each with its measured gain in bits and what a refile needs? |
| Q10 | judge findings and status | What have the organizer judges said about rR entries (ruling, fatal or material findings, status on the board), and which fix is the one the ruling names? |
| Q11 | transfer from neighbouring rows | Which finding or lever measured on a neighbouring row (rR-1, rR+1) transfers to rR unchanged, which needs re-measurement, and which does not transfer? |
| Q12 | structurally special at this round count | Is anything structurally special at rR (a boundary round count, a changed free-round budget, a regime change between straight and rolled, a changed C(r) unit, a rule edge)? |
| Q13 | step program: partial-round / hidden-basis cut | Step program of rR (140+12r field ops in the filed route): how many ops does the partial-round body, the entry/exit of the partial form and the four full-round layers cost, and which basis / form choice lowers it (hidden-basis cut -4 ops, fixed function, monomial forms)? |
| Q14 | DP test, gap budget and recovery | Distinguished-point test cost (AND+compare+branch vs compare+branch), gap-law (geometric) budget 3*gmax versus a sum tail, and the recovery share of the ledger at rR. |

Status rule (SCHEMA.md): a cell is filled (BEDROCK / COMPUTED / LOCAL_ONLY / KILLED) only where one of OUR files records the number, with its evidence path; everything else is OPEN. LOCAL_ONLY = the file answers a neighbouring or sampled row, or an extrapolation the author did not run on this row. Q8 and Q10 are filled from the board snapshot and FILINGS.md for every row (an empty square is recorded as a fact: no rival entry, no filing). Every new cell carries `peak_mem` (UNKNOWN unless a file states it).

### Row x question grid (B bedrock, C computed, L local-only, O open)

| row | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Q9 | Q10 | Q11 | Q12 | Q13 | Q14 | filings | best rival on board | our best on board |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r3 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r4 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r5 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r6 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r7 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 3 | none | b1f61068 126.29614 |
| r8 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 26dd8be7 126.80186 |
| r9 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 3 | none | 72f7c8f7 126.79551 |
| r10 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 19a204b8 126.78977 |
| r11 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 9567320b 126.78455 |
| r12 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 12f85694 126.77979 |
| r13 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 5a74583c 126.77542 |
| r14 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 0fef5876 126.7714 |
| r15 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 5f1139dd 126.76769 |
| r16 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | c1b5818f 126.76425 |
| r17 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | d1573806 126.76106 |
| r18 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 06468284 126.25575 |
| r19 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 0e65a39c 126.25356 |
| r20 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | d1093494 126.25151 |
| r21 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 4666b42a 126.2496 |
| r22 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | abdf0eed 126.2478 |
| r23 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 3 | none | ab786fcb 126.74586 |
| r24 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | bf6d2b58 126.24451 |
| r25 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | bb242a47 126.24301 |
| r26 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | bb9d4290 126.24159 |
| r27 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 30dde4af 126.24025 |
| r28 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 583b769a 126.23898 |
| r29 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 25e887d4 126.23777 |
| r30 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 837cfcd9 126.23662 |
| r31 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | ca40af26 126.23553 |
| r32 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 22a04fe5 126.23449 |
| r33 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 17c54ff4 126.2335 |
| r34 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 5386f1ef 126.23256 |
| r35 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 053e0148 126.23165 |
| r36 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 64a0fba7 126.23079 |
| r37 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 06a93b37 126.22997 |
| r38 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | f120177f 126.22918 |
| r39 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 55f8f78f 126.22842 |
| r40 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | e57a5238 126.2277 |
| r41 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | aab82d89 126.227 |
| r42 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | 34fa90ef 126.22633 |
| r43 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 1 | none | bb856819 126.22569 |
| r44 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r45 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r46 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r47 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r48 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r49 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r50 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r51 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r52 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r53 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r54 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r55 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r56 | C | C | C | C | C | C | C | L | C | C | C | C | C | C | 1 | tanctl 91024c77 126.711157 | 56fb07fc 126.71117 |

Totals: 54 rows, 756 cells; COMPUTED 755, LOCAL_ONLY 1.


## Part 2 - algebraic Poseidon rows (line restriction + powering + half-gcd)


Generated 2026-10-17 by `research/dig/new/gen_new_cells.py` + `gen_grid_md.py` (cells in `research/dig/new/poseidon-algebraic.jsonl`, merged into CELLS.jsonl 2026-10-17). Poseidon algebraic rows r3..r21: two free rounds on a line, odd part g of degree m=(5^(6+r)-1)/2, Euler-exponent powering by Barrett squarings on NTTs, half-gcd root certificate (research/poseidon/algebraic_paper/ledger.py).

Each row is its own dig site with the same needs as the older sites: ledger, memory, packing, success slack, premise, preprocessing, rival, levers, judge findings, neighbour transfer, structure. Fourteen questions per row (Q1..Q12 shared by all families, Q13/Q14 family specific). Cell ids are `PR-poseidon-algebraic-r<R>-<Qn>`; hash field is `poseidon-r<R>`.

### The question template

| Q | name | question (R = round count) |
|---|---|---|
| Q1 | cost ledger | Cost ledger of the row poseidon-algebraic rR: where does every op go, term by term (per step / per trial / per batch, plus recovery, setup, preprocessing), and what is the exact total of the filed or best program? Give shares in percent and bit value of one op. |
| Q2 | dispatch and control charge | Which control ops does rR charge (loop counter, branch, DP/filter test, handlers, dispatch, loads/stores, register moves) and is each charged at best-case exact count, per the organizer cost model as written? |
| Q3 | memory peak and drain | What is the peak-memory phase of rR (which stage, which buffers live), what is the measured or modelled peak in bytes, and do drain / stream / alias / free-early options lower the peak that binds (peak = max over stages, so all binding stages must drop)? |
| Q4 | table / entry packing | How is the table, entry or code packed on rR (bits per entry, entries, bytes per instruction, code bytes versus table slots), and what does a different packing change in the ledger? |
| Q5 | success-bound slack | How far is the proven success probability of rR above the required premise, and what time bit does the slack cost (which proof terms F1.. and which are looser than needed)? |
| Q6 | premise and evidence | What premise (H-statements, probability model, statistic) does rR rest on, what organizer-executed evidence supports it, and what would a judge need to see that is missing? |
| Q7 | preprocessing / advice | What preprocessing, advice or nonuniform data does rR use, how is it charged (time, memory, advice size), and is any of it free or hidden? |
| Q8 | rival best on this row | Who holds the best rival entry on rR on the board, at what score, and where does it save against us (ledger term by term, convention, premise)? If no rival is on the row, record the empty square. |
| Q9 | levers applied vs unapplied | Which levers are applied in our rR entry, and which recorded levers (LEVERS.md, levers_1016/*/RESULT.md) are not applied, each with its measured gain in bits and what a refile needs? |
| Q10 | judge findings and status | What have the organizer judges said about rR entries (ruling, fatal or material findings, status on the board), and which fix is the one the ruling names? |
| Q11 | transfer from neighbouring rows | Which finding or lever measured on a neighbouring row (rR-1, rR+1) transfers to rR unchanged, which needs re-measurement, and which does not transfer? |
| Q12 | structurally special at this round count | Is anything structurally special at rR (a boundary round count, a changed free-round budget, a regime change between straight and rolled, a changed C(r) unit, a rule edge)? |
| Q13 | powering / half-gcd / NTT stage costs | For rR: degree m = (5^(6+r)-1)/2 odd part, NTT plan (2^a or 3*2^a), cost of the Euler-exponent powering (squarings, Barrett reductions) and of the half-gcd / root-certificate stage, as shares of the trial. |
| Q14 | line restriction, centres and trial count | Line restriction at rR: free rounds spent, centre choice and number of trials K charged (centre-1 vs anchored centre), per-trial success probability bound and its premise (plane / complete-intersection genus bound), and the cross-over against the generic row. |

Status rule (SCHEMA.md): a cell is filled (BEDROCK / COMPUTED / LOCAL_ONLY / KILLED) only where one of OUR files records the number, with its evidence path; everything else is OPEN. LOCAL_ONLY = the file answers a neighbouring or sampled row, or an extrapolation the author did not run on this row. Q8 and Q10 are filled from the board snapshot and FILINGS.md for every row (an empty square is recorded as a fact: no rival entry, no filing). Every new cell carries `peak_mem` (UNKNOWN unless a file states it).

### Row x question grid (B bedrock, C computed, L local-only, O open)

| row | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Q9 | Q10 | Q11 | Q12 | Q13 | Q14 | filings | best rival on board | our best on board |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r3 | C | C | C | C | C | C | C | L | C | C | C | C | C | C | 4 | 0xshikhar edd943c9 37.12612 | c4ee5996 37.98182 |
| r4 | C | C | C | C | C | C | C | L | C | C | C | C | C | C | 1 | 0xshikhar 52120fad 40.49661 | 39cb620f 43.82959 |
| r5 | C | C | C | C | C | C | C | L | C | C | C | C | C | C | 6 | 0xshikhar 716c3818 44.98474 | 2f2c30dd 46.98175 |
| r6 | C | C | C | C | L | C | C | C | C | C | C | C | C | L | 0 | none | none |
| r7 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 4 | none | d3050341 58.073570000000004 |
| r8 | C | C | C | C | C | C | C | C | C | C | C | C | C | C | 0 | none | none |
| r9 | C | C | L | C | L | C | C | C | L | C | C | C | C | L | 0 | none | none |
| r10 | C | L | L | C | L | C | C | C | L | C | C | C | C | L | 0 | none | none |
| r11 | L | L | L | C | L | C | C | C | L | C | C | C | C | L | 0 | none | none |
| r12 | L | O | L | L | O | L | L | C | L | C | L | C | L | L | 0 | none | none |
| r13 | L | O | L | L | O | L | L | C | O | C | L | C | L | L | 0 | none | none |
| r14 | L | O | L | L | O | L | L | C | O | C | L | C | L | L | 0 | none | none |
| r15 | L | O | L | L | O | L | L | C | L | C | L | C | L | L | 0 | none | none |
| r16 | L | O | L | L | O | L | L | C | O | C | L | C | L | L | 0 | none | none |
| r17 | L | O | L | L | O | L | L | C | O | C | L | C | L | L | 0 | none | none |
| r18 | L | O | L | L | O | L | L | C | L | C | L | C | L | L | 0 | none | none |
| r19 | L | O | L | L | O | L | L | C | O | C | L | C | L | L | 0 | none | none |
| r20 | L | O | L | L | O | L | L | C | O | C | L | C | L | L | 0 | none | none |
| r21 | L | O | L | L | O | L | L | C | L | C | L | C | L | L | 0 | none | none |

Totals: 19 rows, 266 cells; COMPUTED 136, LOCAL_ONLY 104, OPEN 26.


## Part 3 - empty squares recorded at creation

- Generic r3..r6: no row built (algebraic is 80+ bits better); recorded in the Q12 cells.
- Generic r7..r56 rival column: the board holds no rival entry on most of these rows (see the grid column "best rival on board"); a rival may appear any time.
- Algebraic r9..r21: modelled only (Grok 129 abstract model with our unit mapping), no C program and no filing; LOCAL_ONLY cells say so.
- Algebraic r8 is staged (pos_posalg_r8b) and not filed; r3..r7 are filed (POSR3E/F/G/H, POSR4M, POSR5M/T/U, POSR7ALG*).

## Part 4 - attack-FAMILY grid for the algebraic rows (2026-10-17 night, by hand). Worse is a recorded cell, never a kill. Every family asked, combination noted.

| family | applies to Poseidon alg? | cost (bits/round or best) | vs our univariate | combination candidate | status | evidence |
|---|---|---|---|---|---|---|
| univariate line+powering+half-gcd (OURS) | yes | ~4.64/round (time+mem); r21 124.70 | baseline, LEADS r6-r20 | base for every hybrid | COMPUTED | pos_p9s |
| elimination-free / Groebner (keep sbox vars) | yes | 174-570 bits (Macaulay bound); structured=FreeLunch | WORSE (elimination blowup) | could seed a sparse-hybrid; re-ask with the STRUCTURED d_reg, not Macaulay | RECORDED-worse (loose bound) | pos_wall/dreg.py; LEVERS 336 FreeLunch |
| MITM / claw (fwd+bwd, middle match) | partial | middle 3-D (nonsingular obs/ctrl) -> no small match; full-state p^3 | WORSE | ONLY reopens via a nonlinear bottleneck h:F^3->F^2 (UNTESTED) | RECORDED + 1 open crack | pos_wall/mitm.md |
| birthday / Pollard-rho (memoryless) | yes | 2^127 flat, all rounds | WORSE <=r21, = generic r22+ | seed for algebra+rho hybrid | RECORDED | pos_wall/seam_hybrid.md |
| hybrid (algebra slice + rho) | yes | TIES the wall ~127; PLATEAU | plateau, not dive; but FLATTENS red line r21->r30-35 (real path!) | the plateau is itself a distinct path worth a row | RECORDED-real-plateau | pos_wall/seam_hybrid.md |
| differential (fixed delta) | yes | no excess at boring deltas, 216 configs | no gain | pair with a slice? untested | RECORDED | pos_wall/edison_edges.py |
| composition (lower the degree) | yes | m-dim algebra, degree rigid 5^(R+6), 60 configs | no gain | with annihilation (closed) | RECORDED | pos_wall/degree_rigidity.py, implicit_g_memory.md |
| subspace trail / GKR | yes | Li-Wang 2026/967 ceiling <= 2 partial rounds | WORSE | with free rounds (spent) | RECORDED | LEVERS 319 |
| interpolation / multipoint eval | ??? | NOT ASKED | unknown | unknown | **OPEN - grid it** | - |
| guess-and-determine (fix a few state words) | ??? | NOT ASKED | unknown | with partial-round 1-word structure | **OPEN - grid it** | - |
| Wagner / generalized birthday k-list | ??? | NOT ASKED for Poseidon (checked for sha3/blake3) | unknown | with the sponge truncation | **OPEN - grid it** | - |

### The open squares I never asked (this is where I gave up)
1. **interpolation / multipoint** - can the collision be found by evaluating g at a structured point set cheaper than root-finding? Q13 for this family unasked.
2. **guess-and-determine** - fix s of the 3 state words at a mid partial round, solve the rest; does the single-nonlinear-word partial structure make a cheap G&D? Unasked.
3. **Wagner k-list** - on the sponge's discarded-coordinate freedom, does a k-list beat 2^127? Unasked for Poseidon.


### Luna closure 2615 (2026-10-18)

| item | status | result | evidence |
|---|---|---|---|
| FreeLunch/CheapLunch on Orchard collision line | KILLED / DERIVED | FreeLunch's inverse-power premise is absent; CheapLunch k=1 gives 5^(7+r), one factor worse than our 5^(6+r), with no collision-specific or memory gain | research/luna/item2615_poseidon_freelunch_cheaplunch_wall.md; research/poseidon/levels/freelunch/FREELUNCH.md; research/poseidon/levels/cheaplunch/CHEAPLUNCH.md |


### Luna closure 2618 (2026-10-18)

| item | status | result | evidence |
|---|---|---|---|
| Poseidon r2 half-twiddle table | COMPUTED / KILLED | Functional KAT exact; memory saves 1 MiB (0.0374378784 bits), but known reconstruction lower bound is 465,567,744 extra operations over four centres and complete charge is open; honest credit 0 | research/luna/item2618_poseidon_r2_half_twiddle_reprice.md; research/sol_answer_D462_poseidon_r2_half_table_kat.md; research/sol_answer_C1872.md |


### Luna closure 2619 (2026-10-18)

| item | status | result | evidence |
|---|---|---|---|
| Poseidon r1 register block | COMPUTED / CLOSED | Uncharged wide register-file accesses invalidate 28.11235 as an honest gain; wide-RF honest score 29.358 is worse, and plain exec6 28.45462 is the honest fallback | research/luna/item2619_poseidon_r1_register_block_honesty.md; research/LEVERS.md line 350; single_r1_exec6/7 submission notes |

### LUNA-2624 — Poseidon Orchard third-free-round / partial-bypass doors (2026-10-18)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| `LUNA-2624-POSEIDON-ORCHARD-DOORS-20261018` | Orchard profile and toy doors, LEVERS.md line 478 | COMPUTED / CLOSED | Toy tests at p=53/103 and 2^10–2^18 plus real Orchard checks found no production-safe third-free-round, partial-bypass, streamed-g, or backward-landing gain. | `research/luna/item2624_poseidon_orchard_doors_closed.md`; `research/doors_1015/poseidon_third_free_round.md`; `poseidon_partial_bypass.md`; `poseidon_door9_test.md`; `poseidon_door10_test.md` | 0.00000 bits; no build/package/stage/filing/submission. |
### LUNA-2629 — Poseidon Grok-120 degree-wall re-price (2026-10-18)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| `LUNA-2629-POSEIDON-DEGREE-WALL-20261018` | Poseidon r6–r10 degree/root-finding wall, LEVERS.md line 483 | COMPUTED / CLOSED (qualified) | Two-free-round line and 253-squaring root bound stand; third-free-round is codimension-one in constants, not line-tunable. Orchard dot product is not in copied evidence. | `research/luna/item2629_poseidon_degree_wall.md`; `research/grok/work/job120_poseidon_high_rounds/ANSWER.md` | 0.00000 claimable bits; conditional third-free-round scenario remains unfiled pending the real constant check. |
### LUNA-2630 — Poseidon short-product length restriction (2026-10-18)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| `LUNA-2630-POSEIDON-SHORT-PRODUCT-20261018` | full square and A·μ middle-product lengths, LEVERS.md line 491 | COMPUTED / CLOSED | Full square requires 2m−1 support (or equivalent two transforms); A·μ window requires ≥2m−3. Only q·g low part fits length ≥m. Projected 0.749 time is conditional and not claimable. | `research/luna/item2630_poseidon_short_product_closed.md`; `research/poseidon/orchard/SPEEDUP.md`; `research/grok/work/job127c_poseidon_r7_memory/ANSWER.md` | 0.00000 bits; current rows-2 path remains the owned direction. |
### LUNA-2632 — Poseidon memory-peak reorder re-price (2026-10-18)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| `LUNA-2632-POSEIDON-PEAK-REORDER-20261018` | free stage C before stage D / peak memory, LEVERS.md line 531 | COMPUTED / KILLED | First-fit allocator already reuses freed C space; binding rows have no holes and arena equals live-set lower bound. Memory drop is 0.000 bits. | `research/luna/item2632_poseidon_peak_reorder.md`; `research/levers_1017/pos_peak/RESULT.md` | 0.00000 standalone credit; −0.0166/−0.0189 register-kernel values are separate derived estimates. |
### LUNA-2633 — Poseidon pay-front / guess-and-determine re-price (2026-10-18 23:37)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2633-POSEIDON-PAY-FRONT-20261018 | Poseidon pay-front / guess-and-determine / wave-invert, LEVERS.md line 535 | COMPUTED / KILLED | Toy evidence gives the irreducible one-collision floor min(5^R, p^0.5); middle-map matching, guessed middle words, backward inversion, and alternate domains do not lower it. Low-memory root isolation remains a separate OPEN question. | 
esearch/luna/item2633_poseidon_pay_front_killed.md; 
esearch/levers_1017/pos_wall/pay_front.md | 0.00000 claimable bits; research-only. |
### LUNA-2634 — Poseidon r56 generic-step stack re-price (2026-10-18 23:37)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2634-POSEIDON-R56-GENERIC-STACK-20261018 | r56 generic-step B/C/D and fused branch, LEVERS.md line 537 | COMPUTED / KILLED | B+C+D gives 126.215109 (-0.004085); fused ruling-gated BLTU gives 126.213329 (-0.005865) versus shipped 126.219194. No 0.1-bit lever, package, proof, or organizer KAT. | 
esearch/luna/item2634_poseidon_r56_generic_stack_reprice.md; 
esearch/levers_1018/r56/generic_step/RESULT.md | 0.00000 claimable bits; retain shipped row. |
### LUNA-2635 — Poseidon object-size / duplicate-copy re-price (2026-10-18 23:37)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2635-POSEIDON-OBJSIZE-20261018 | object-size, duplicate-copy, erasure, streamed-factor layouts, LEVERS.md line 538 | COMPUTED / KILLED | Valid streamed layout: mem 68.693, time 72.69210, score 121.38510 versus accepted 121.38511; 3/2-copy targets not reached. Rebuilding/dropping G copies loses time. | 
esearch/luna/item2635_poseidon_objsize_killed.md; 
esearch/levers_1018/objsize/RESULT_2XCOPY.md; objsize/dedupC/RESULT.md | 0.00000 claimable bits; retain accepted row. |
### LUNA-2636 — Poseidon r7 projected-vs-found audit (2026-10-18 23:38)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2636-POSEIDON-R7-PROJECTED-20261018 | PROJECTED_VS_FOUND.tsv line 2; filed Poseidon r7 one-centre row | COMPUTED / KILLED | Projected −0.446 bits has found 0; pure-2^a transform is 1.33x larger on the filed structure and is DEAD. | 
esearch/luna/item2636_poseidon_r7_projected_found_dead.md; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 2; 
esearch/LEVERS.md line 605 | 0.00000 claimable bits; retain filed r7 row. |
### LUNA-2637 — Poseidon stage-D one-at-a-time output trim (2026-10-18 23:38)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2637-POSEIDON-STAGE-D-TRIM-20261018 | stage-D mat_mul outputs one-at-a-time, LEVERS.md line 539 | DERIVED / KILLED | Stage C peak is 4.0 arrays while stage D is ~3.8, so D-only trimming cannot change the charged memory peak. | 
esearch/luna/item2637_poseidon_stage_d_trim_killed.md; 
esearch/LEVERS.md line 539; 
esearch/levers_1018/objsize/dedupC/RESULT.md | 0.00000 claimable bits; score-neutral. |
### LUNA-2638 — Poseidon r12 projected-vs-found audit (2026-10-18 23:38)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2638-POSEIDON-R12-PROJECTED-20261018 | PROJECTED_VS_FOUND.tsv line 3; filed Poseidon r12 one-centre row | COMPUTED / KILLED | Projected −0.376 bits has found 0; pure-2^a plan is transform-domain and not composable with filed value-domain stage C. | 
esearch/luna/item2638_poseidon_r12_projected_found_dead.md; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 3; 
esearch/LEVERS.md line 601; item921 | 0.00000 claimable bits; retain filed r12 row. |
### LUNA-2639 — Poseidon r15/r18/r21 projected-vs-found audit (2026-10-18 23:39)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2639-POSEIDON-R15-R18-R21-PROJECTED-20261018 | PROJECTED_VS_FOUND.tsv line 4; filed one-centre rows r15/r18/r21 | COMPUTED / KILLED | Each projected −0.376-bit row has found 0 and is not composable with the filed value-domain program; w=1 and transform/KAT/organizer premises remain missing. | 
esearch/luna/item2639_poseidon_r15_r18_r21_projected_dead.md; items 924/927/930; 
esearch/LEVERS.md lines 602–604 | 0.00000 claimable bits for r15, r18, r21. |
### LUNA-2640 — Poseidon r9 projected-vs-found audit (2026-10-18 23:39)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2640-POSEIDON-R9-PROJECTED-20261018 | PROJECTED_VS_FOUND.tsv line 5; staged Poseidon r9 row | COMPUTED / KILLED | Projected −0.376 bits has found 0; normalized staged model lacks coded transform/KAT/package and is not composable with filed line. | 
esearch/luna/item2640_poseidon_r9_projected_found_dead.md; item918; 
esearch/LEVERS.md line 600 | 0.00000 claimable bits; retain staged/filed r9 row. |
### LUNA-2641 — Poseidon generic r45–r56 projected-vs-found audit (2026-10-18 23:39)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2641-POSEIDON-GENERIC-R45-R56-20261018 | PROJECTED_VS_FOUND.tsv line 8; generic Poseidon r45–r56 rows | COMPUTED / BELOW FLOOR | Compare-only DP + U6 projections range −0.002173 to −0.001975 bits; no variants built, and all are below the 0.25-bit floor. | 
esearch/luna/item2641_poseidon_generic_r45_r56_below_floor.md; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 8; items 900–911 | 0.00000 claimable bits for r45–r56. |
### LUNA-2643 — Poseidon r7–r22 structural projected-vs-found audit (2026-10-18 23:39)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2643-POSEIDON-R7-R22-STRUCTURAL-20261018 | PROJECTED_VS_FOUND.tsv line 11; filed structural Poseidon r7–r22 rows | COMPUTED / KILLED | Generic-rho projections −0.00735…−0.003823 bits are unbuilt/conditional and not composable with filed structural rows at 56.84–124.94. | 
esearch/luna/item2643_poseidon_r7_r22_structural_dead.md; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 11; 
esearch/LEVERS.md lines 548–563; items 862–877 | 0.00000 claimable bits for r7–r22. |
### LUNA-2644 — Poseidon generic r23–r48 projected-vs-found audit (2026-10-18 23:40)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2644-POSEIDON-GENERIC-R23-R48-20261018 | PROJECTED_VS_FOUND.tsv line 12; filed generic Poseidon r23–r48 rows | COMPUTED / BELOW FLOOR | Projections −0.003556…−0.002107 bits; all conditional/unbuilt and below the 0.25-bit floor; no composable filed-package delta. | 
esearch/luna/item2644_poseidon_generic_r23_r48_below_floor.md; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 12; 
esearch/LEVERS.md lines 564–589 | 0.00000 claimable bits for r23–r48. |
### LUNA-2645 — Poseidon generic r49–r55 projected-vs-found audit (2026-10-18 23:40)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2645-POSEIDON-GENERIC-R49-R55-20261018 | PROJECTED_VS_FOUND.tsv line 13; generic Poseidon r49–r55 rows | COMPUTED / BELOW FLOOR | Projections −0.002087…−0.001988 bits; found 0, unbuilt, and below 0.25-bit floor; no reviewed board entries. | 
esearch/luna/item2645_poseidon_generic_r49_r55_below_floor.md; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 13; 
esearch/LEVERS.md lines 590–596 | 0.00000 claimable bits for r49–r55. |
### LUNA-2646 — Poseidon r56 competitor-gap projected-vs-found audit (2026-10-18 23:40)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2646-POSEIDON-R56-GAP-20261018 | PROJECTED_VS_FOUND.tsv line 14; filed r56 row versus competitor | COMPUTED / BELOW FLOOR | −0.001975-bit projection cannot close ~0.49-bit competitor gap; variant remains unbuilt/conditional. | 
esearch/luna/item2646_poseidon_r56_competitor_gap_below_floor.md; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 14; item911; board snapshot | 0.00000 claimable bits; retain filed r56 row. |
### LUNA-2648 — Poseidon r21 Q3 memory projected-vs-found audit (2026-10-18 23:40)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2648-POSEIDON-R21-Q3-MEM-20261018 | PROJECTED_VS_FOUND.tsv line 62; filed r21 row 3ecf886c | COMPUTED / KILLED | Modeled memory 69.97 log2 bytes is 1.277 bits above filed 68.693; no executable/chargeable gain. | 
esearch/luna/item2648_poseidon_r21_q3_memory_dead.md; item124; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 62 | 0.00000 claimable bits; retain filed r21 row. |
### LUNA-2649 — Poseidon r12–r21 Q4 packed-heap audit (2026-10-18 23:41)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2649-POSEIDON-Q4-PACKING-R12-R21-20261018 | PROJECTED_VS_FOUND.tsv line 63; Q4 packed heap r12–r21 | COMPUTED / KILLED | Modeled heap is +0.60…+0.64 bits above filed memory on every row; no packed executable/KAT/package. | 
esearch/luna/item2649_poseidon_q4_packing_dead.md; items 129–138; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 63 | 0.00000 claimable bits for r12–r21. |
### LUNA-2650 — Poseidon r12–r21 Q7 no-extra-advice audit (2026-10-18 23:41)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2650-POSEIDON-Q7-ADVICE-R12-R21-20261018 | PROJECTED_VS_FOUND.tsv line 64; filed one-centre rows r12–r21 | DERIVED / KILLED | No extra advice/preprocessing beyond the existing twiddle table; 	t_init(32)=2^31 is not a new lever. | 
esearch/luna/item2650_poseidon_q7_no_extra_advice_dead.md; items 148–157; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 64 | 0.00000 claimable bits for r12–r21. |
### LUNA-2651 — Poseidon r3–r5 projected-vs-found audit (2026-10-18 23:41)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2651-POSEIDON-R3-R5-PROJECTED-20261018 | PROJECTED_VS_FOUND.tsv line 65; filed r3–r5 rows | COMPUTED / BELOW FLOOR | Twiddle upper bound −0.08…−0.10 bits; honest lookup loses 0.08–0.11; b3 memory path is GUESS and cannot close 2.00–3.16-bit leader gaps. | 
esearch/luna/item2651_poseidon_r3_r5_below_floor.md; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 65; 
esearch/levers_1016/posledger/RESULT.md | 0.00000 claimable bits for r3–r5. |
### LUNA-2652 — Poseidon r6–r8 b3/twiddle projected-vs-found audit (2026-10-18 23:41)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2652-POSEIDON-R6-R8-B3-TWIDDLE-20261018 | PROJECTED_VS_FOUND.tsv line 66; filed one-centre r6–r8 rows | COMPUTED / KILLED (bounded pass) | Twiddle is below floor; b3 and pure-2^a remain ideal/guess scenarios with no coded charged ledger, allocation trace, KAT, package, or ruling. | 
esearch/luna/item2652_poseidon_r6_r8_b3_twiddle_killed.md; 
esearch/levers_1018/audit/RESULT_PRICES_C.md; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 66 | 0.00000 claimable bits; blockers preserved for any future reopening. |
### LUNA-2653 — Poseidon r9–r11 projected-vs-found audit (2026-10-18 23:42)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2653-POSEIDON-R9-R11-PROJECTED-20261018 | PROJECTED_VS_FOUND.tsv line 67; filed Poseidon r9–r11 rows | COMPUTED / BELOW FLOOR | Twiddle ≈−0.09, honest +1-op ≈−0.03, b3 −0.60 is GUESS; pure plan 1.35–1.39x worse; no leader closure. | 
esearch/luna/item2653_poseidon_r9_r11_below_floor.md; items 1014–1016; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 67 | 0.00000 claimable bits for r9–r11. |
### LUNA-2660 — Poseidon r7 CRT-layout audit (2026-10-18 23:43)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2660-POSEIDON-R7-CRT-20261018 | PROJECTED_VS_FOUND.tsv line 90; filed r7 813d502d CRT layout | COMPUTED / KILLED | Verified exact row is 56.91930 versus filed 56.83857 (+0.08073 loss); note overstated saving ~3.8x and CRT stage source is missing. | 
esearch/luna/item2660_poseidon_r7_crt_killed.md; 
esearch/luna/verify1018/stack_crt_r7.md; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 90 | 0.00000 claimable bits; retain filed r7 row. |
### LUNA-2661 — Poseidon r6 rebuild-on-fly audit (2026-10-18 23:43)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2661-POSEIDON-R6-REBUILD-20261018 | PROJECTED_VS_FOUND.tsv line 91; filed r6 rebuild-on-fly | COMPUTED / BELOW FLOOR | Modeled 52.85281→52.78981 (−0.063 bits); proof text/refile required and no package exists. | 
esearch/luna/item2661_poseidon_r6_rebuild_below_floor.md; 
esearch/luna/verify1018/rebuild_on_fly.md; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 91 | 0.00000 claimable bits; retain filed r6 row. |
### LUNA-2662 — Poseidon r7/r8/r12 rebuild-on-fly audit (2026-10-18 23:43)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2662-POSEIDON-R7-R8-R12-REBUILD-20261018 | PROJECTED_VS_FOUND.tsv line 92; rebuild-on-fly r7/r8/r12 | COMPUTED / KILLED | No score change at r7/r8/r12; stage-C arrays are used each step and rebuild cost exceeds possible memory relief. | 
esearch/luna/item2662_poseidon_r7_r8_r12_rebuild_killed.md; 
esearch/luna/verify1018/rebuild_on_fly.md; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 92 | 0.00000 claimable bits for r7/r8/r12. |
### LUNA-2664 — Poseidon r16/r17/r19/r20/r21 status audit (2026-10-18 23:44)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2664-POSEIDON-R16-R17-R19-R20-R21-20261018 | PROJECTED_VS_FOUND.tsv line 98; status/modelled rows | COMPUTED / KILLED | Status and board review reconcile; stale r21 125.45529 is superseded by authoritative 125.42546; no new lever. | 
esearch/luna/item2664_poseidon_r16_r17_r19_r20_r21_status.md; items 4–8; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 98 | 0.00000 claimable bits for all listed rows. |
### LUNA-2665 — Poseidon r15–r21 Q2 dispatch/control audit (2026-10-18 23:44)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2665-POSEIDON-Q2-CONTROL-R15-R21-20261018 | PROJECTED_VS_FOUND.tsv line 99; Q2 dispatch/control r15–r21 | COMPUTED / BELOW FLOOR | All control is already charged and required; isolated share is not separately tabulated but ≤~1.4e4 ops against N_max and cannot move score. | 
esearch/luna/item2665_poseidon_q2_control_below_floor.md; items 12–18; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 99 | 0.00000 claimable bits; isolated percentage remains documentation OPEN only. |
### LUNA-2667 — Poseidon generic-rho r7–r56 projected-vs-found audit (2026-10-18 23:44)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2667-POSEIDON-GENERIC-R7-R56-20261018 | PROJECTED_VS_FOUND.tsv line 154; generic-rho route2d2 r7–r56 | COMPUTED / BELOW FLOOR | Projections −0.00735…−0.001975 bits, unbuilt and missing gap-law/organizer verification; not composable with filed structural or generic rows. | 
esearch/luna/item2667_poseidon_generic_r7_r56_group_below_floor.md; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 154; generic-rho report | 0.00000 claimable bits. |
### LUNA-2668 — Poseidon algebraic r3 projected-vs-found audit (2026-10-18 23:45)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2668-POSEIDON-R3-ALG-20261018 | PROJECTED_VS_FOUND.tsv line 155; filed r3 algebraic rows | COMPUTED / KILLED | −0.42 projection uses K=1 ledger, while filed rows already power at 2^21; no residual, and unbuilt full model remains ~2.03 bits above leader. | 
esearch/luna/item2668_poseidon_r3_projected_not_composable.md; 
esearch/LEVERS.md lines 460,605; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 155 | 0.00000 claimable bits. |
### LUNA-2669 — Poseidon algebraic r9 projected-vs-found audit (2026-10-18 23:45)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2669-POSEIDON-R9-ALG-20261018 | PROJECTED_VS_FOUND.tsv line 156; filed/staged r9 algebraic rows | COMPUTED / KILLED | −0.376 model-only transform projection, found 0; not composable with value-domain stage C, no code/KAT/package, and even model 66.39 is >1.6 bits above leader. | 
esearch/luna/item2669_poseidon_r9_projected_not_composable.md; 
esearch/LEVERS.md line 600; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 156 | 0.00000 claimable bits. |
### LUNA-2670 — Poseidon r3–r11 Q12 structural-regime audit (2026-10-18 23:45)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2670-POSEIDON-R3-R11-Q12-20261018 | PROJECTED_VS_FOUND.tsv line 160; Q12 structural regime | COMPUTED / KILLED | 3·2^b versus pure 2^b ratios are model-only; pure power-of-two route is not implemented or chargeable on filed ledgers. | 
esearch/luna/item2670_poseidon_r3_r11_q12_structural_dead.md; items 1035–1043,1092; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 160 | 0.00000 claimable bits. |
### LUNA-2671 — Poseidon r7–r11 Q14 K=2 audit (2026-10-18 23:45)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2671-POSEIDON-R7-R11-Q14-K2-20261018 | PROJECTED_VS_FOUND.tsv line 163; Q14 K=2 variant | COMPUTED / KILLED | K=2 (q≈0.247, success 0.43348) is a different configuration from filed K=1 (q≈0.3901, success 0.39009); no transfer. | 
esearch/luna/item2671_poseidon_r7_r11_q14_k2_not_composable.md; items 1057,1059–1061; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 163 | 0.00000 claimable bits. |
### LUNA-2672 — Poseidon r12–r21 Q11 transfer audit (2026-10-18 23:45)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2672-POSEIDON-R12-R21-Q11-20261018 | PROJECTED_VS_FOUND.tsv line 167; Q11 transfer from neighbours | COMPUTED / KILLED | Transfer is LOCAL_ONLY and adds +0.037 time bits/+0.58 memory bits; no gain or package transfer. | 
esearch/luna/item2672_poseidon_r12_r21_q11_transfer_killed.md; items 1082–1091; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 167 | 0.00000 claimable bits. |
### LUNA-2673 — Poseidon r12–r21 Q12 structural-regime audit (2026-10-18 23:45)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2673-POSEIDON-R12-R21-Q12-20261018 | PROJECTED_VS_FOUND.tsv line 168; Q12 structural regime | COMPUTED / KILLED | Pure-2^b route is unimplemented; ratios only confirm the structural lead already in filed K-rows; no counted delta. | 
esearch/luna/item2673_poseidon_r12_r21_q12_structural_dead.md; items 1092–1101; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 168 | 0.00000 claimable bits. |
### LUNA-2674 — Poseidon one-centre r2 CERT-B audit (2026-10-18 23:45)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2674-POSEIDON-R2-CERTB-20261018 | PROJECTED_VS_FOUND.tsv line 184; one-centre r2 CERT B | COMPUTED / KILLED | Authorized run OOM in baby step at ~891s; no witness/residual; route remains dead/not composable. | 
esearch/luna/item2674_poseidon_r2_certb_oom.md; historical-sources/Luna_Orders/answers/S005.md; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 184 | 0.00000 claimable bits. |
### LUNA-2675 — Poseidon one-centre CERT-B factoring audit (2026-10-18 23:46)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2675-POSEIDON-CERTB-FACTOR-20261018 | PROJECTED_VS_FOUND.tsv line 188; six-centre CERT B factoring | COMPUTED / KILLED | Centres c1–c6 all residual_prime=false and factor_degree=0; no qualifying witness; route remains dead. | 
esearch/luna/item2675_poseidon_certb_factoring_dead.md; historical-sources/Luna_Orders/answers/S009.md; 
esearch/luna/PROJECTED_VS_FOUND.tsv line 188 | 0.00000 claimable bits. |
### LUNA-2676 — Poseidon r9 low-h VDC stacked lean-D/VSHIFT sweep (2026-10-18 23:50)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2676-POSEIDON-R9-LOWH-LEAND-20261018 | VDC low-h K=1 + row-outer stage-C + 4.6 placement | COMPUTED / CONDITIONAL / ALIVE | Owned fixed-model winner: =31,VSHIFT=1,CD=8,LEAND=1,NORMALD=1, N=7,200,233,260,932,029, 	ime_log2=44.01519, mem_log2=42.061, score=66.07619; 0.39378 bits below prior 66.46997, still 1.62370 above 64.45249. | research/luna/item2676_poseidon_r9_lowh_leand_vshift_sweep.md; research/levers_1018/pos_vdc_low/probe_fixed.py and base_fixed/costmodel.py | 0.00000 claimable bits; low-h order/generator/self-test, H-ONE/H-NORMAL and organizer acceptance remain OPEN. |
### LUNA-2677 — Poseidon r9 low-h allocator/chunk sweep (2026-10-18 23:59)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2677-POSEIDON-R9-LOWH-ALLOC-20261018 | VDC low-h K=1 + row-outer stage-C + lean-D allocator placement | COMPUTED / CONDITIONAL / ALIVE | LD_SITE=tmp:1,inv:0,div:0, =31,VSHIFT=1, CD4/CD8 tie, gives N=7,199,987,748,483,305, 	ime_log2=44.01514, mem_log2=41.972, score=65.98714; 0.08905 below item2676 and 0.48283 below prior endpoint, still 1.53465 above bar. | research/luna/item2677_poseidon_r9_lowh_allocator_sweep.md; research/levers_1018/pos_vdc_low/probe_fixed.py and base_fixed/costmodel.py | 0.00000 claimable bits; low-h order/generator/self-test, H-ONE/H-NORMAL and organizer acceptance remain OPEN. |
### LUNA-2678 — Poseidon r9 low-h lean-D switch controls (2026-10-19 00:12)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2678-POSEIDON-R9-LOWH-SWITCHES-20261019 | VDC low-h K=1 + lean-D top-node/windows controls | COMPUTED / CONDITIONAL / ALIVE | LD_PIECES=0 scores 66.48109; LD_WIN=0 scores 65.98936; item2677 winner 65.98714 remains. | research/luna/item2678_poseidon_r9_lowh_leand_switches.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; low-h order/generator/self-test, H-ONE/H-NORMAL and organizer acceptance remain OPEN. |
### LUNA-2679 — Poseidon r9 low-h geometric-order certificate (2026-10-18 23:57)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2679-POSEIDON-R9-LOWH-ORDER-20261018 | VDC low-h a=31 geometric nodes | PROVED / CONDITIONAL / ALIVE | K=8, need order >16; exact Pallas q1 certificate gives ord(5^(2^31)) >= 539204044132271846773, so node distinctness/order is proved. | research/luna/item2679_poseidon_r9_lowh_order_certificate.md; research/levers_1017/pos_vdc/zorder_check.py and runs_vdc/zorder.out | 0.00000 claimable bits; generator/self-test, H-ONE/H-NORMAL and organizer acceptance remain OPEN. |
### LUNA-2680 — Poseidon r9 low-h value-domain KAT (2026-10-18 23:58)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2680-POSEIDON-R9-LOWH-KAT-20261018 | Owned low-h stage-C self-test on toy r3/r9 instances | COMPUTED / PARTIAL / ALIVE | Exact value-domain = independent coefficient-domain reference for r3 (m=29,E=1234567,K=3,h=32) and r9 (m=61,E=3846559,K=12,h=16), exit code 0. | research/luna/item2680_poseidon_r9_lowh_kat.md; research/levers_1018/pos_vdc_low/vd_kat.py | 0.00000 claimable bits; production r9 a=31 generator/self-test, H-ONE/H-NORMAL and organizer acceptance remain OPEN. |
### LUNA-2681 — Poseidon r9 low-h production breakdown (2026-10-19 00:00)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2681-POSEIDON-R9-LOWH-BREAKDOWN-20261019 | Corrected owned value-domain stage-C cost breakdown at r9, a=31 | COMPUTED / PARTIAL / ALIVE | After wiring VD_H_BITS into the copied cost model, the exact audit reports S_C=2,268,177,483,133,537 and stage-C peak=1,978,375,797,888 bytes for VSHIFT=1, CHUNK_CC=4, CHUNK_CD=8. | research/luna/item2681_poseidon_r9_lowh_breakdown.md; research/levers_1018/pos_vdc_low/vd_breakdown.py | 0.00000 claimable bits; full generator/self-test, H-ONE/H-NORMAL and organizer acceptance remain OPEN. |
### LUNA-2682 — Poseidon premise arithmetic negative control (2026-10-19 00:00)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2682-POSEIDON-PREMISE-CONTROL-20261019 | r7 plane-genus exact-rational success-bound control | COMPUTED / CONTEXT ONLY / ALIVE | Owned script exits 0: K=2 success lower bound 0.433498045912; the result is explicitly not the r9 complete-intersection premise. | research/luna/item2682_poseidon_premise_negative_control.md; research/levers_1018/pos_vdc_low/premise_numbers.py | 0.00000 claimable bits; r9 premise and organizer acceptance remain OPEN. |
### LUNA-2683 — Poseidon r9 low-h VSHIFT/CD stage-C controls (2026-10-19 00:01)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2683-POSEIDON-R9-LOWH-STAGEC-20261019 | r9, a=31, corrected value-domain stage-C controls | COMPUTED / PARTIAL / ALIVE | VSHIFT=1 with CD8 or CD16 ties at S_C=2,268,177,483,133,537; VSHIFT=0 and 2 are higher-work controls. | research/luna/item2683_poseidon_r9_lowh_stagec_controls.md; research/levers_1018/pos_vdc_low/vd_breakdown.py | 0.00000 claimable bits; total score and production premises remain OPEN. |
### LUNA-2684 — Poseidon r9 low-h CHUNK_CC control (2026-10-19 00:02)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2684-POSEIDON-R9-LOWH-CHUNKCC-20261019 | r9, a=31, stage-C CHUNK_CC controls | COMPUTED / KILLED CONTROL / ALIVE | CHUNK_CC=1,2,4,8 all exactly tie at S_C=2,268,177,483,133,537 and peak=1,978,375,797,888 bytes. | research/luna/item2684_poseidon_r9_lowh_chunkcc_control.md; research/levers_1018/pos_vdc_low/vd_breakdown.py | 0.00000 claimable bits; CHUNK_CC is not a lever in this model. |
### LUNA-2685 — Poseidon r9 low-h full interior-a sweep (2026-10-19 00:12)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2685-POSEIDON-R9-LOWH-A-SWEEP-20261019 | r9, VDC=1, VSHIFT=1, legal a=12..31, current best allocator settings | COMPUTED / CONDITIONAL / ALIVE | Exact minimum at a=28: N=7,110,978,927,202,847, time_log2=43.99720, mem_log2=41.963, score=65.96020; a=31 gives 65.98714. | research/luna/item2685_poseidon_r9_lowh_interior_a_sweep.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; 0.02694-bit model improvement is below alert threshold; production generator/self-test, H-ONE/H-NORMAL and organizer acceptance remain OPEN. |
### LUNA-2686 — Poseidon r9 low-h VSHIFT=0/2 controls (2026-10-19 00:19)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2686-POSEIDON-R9-LOWH-VSHIFT-20261019 | r9, a=24..31, VSHIFT=0 and 2 controls | COMPUTED / CONDITIONAL / ALIVE | VSHIFT=2/a=28 scores 65.96021; VSHIFT=1/a=28 remains 65.96020; VSHIFT=0 is worse throughout the tested region. | research/luna/item2686_poseidon_r9_lowh_vshift_controls.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; 0.02694-bit conditional gain remains below alert threshold and production premises remain OPEN. |
### LUNA-2687 — Poseidon r9 low-h allocator chunk-fraction sweep (2026-10-19 00:22)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2687-POSEIDON-R9-LOWH-ALLOC-FRACTION-20261019 | r9, a=28, allocator LD_CF controls | COMPUTED / CONDITIONAL / ALIVE | LD_CF=1/32 is exact best tested: N=7,111,732,207,721,979, time_log2=43.99735, mem_log2=41.916, score=65.91335. | research/luna/item2687_poseidon_r9_lowh_allocator_fraction_sweep.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; 0.07379-bit conditional gain is below alert threshold; production premises remain OPEN. |
### LUNA-2688 — Poseidon r9 low-h allocator-site controls at a=28 (2026-10-19 00:25)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2688-POSEIDON-R9-LOWH-ALLOC-SITE-20261019 | r9, a=28, LD_CF=1/32, allocator-site controls | COMPUTED / CONDITIONAL / ALIVE | `tmp:1,inv:0,div:0` remains exact winner at 65.91335; alternative sites score 65.94735–65.97535. | research/luna/item2688_poseidon_r9_lowh_allocator_site_controls.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; no new gain; production premises remain OPEN. |
### LUNA-2689 — Poseidon r9 low-h allocator-switch controls (2026-10-19 00:26)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2689-POSEIDON-R9-LOWH-ALLOC-SWITCH-20261019 | r9, a=28, LD_CF=1/32, LD_PIECES/LD_WIN controls | COMPUTED / CONDITIONAL / ALIVE | PIECES=1/WIN=1 scores 65.91335; disabling either is worse. | research/luna/item2689_poseidon_r9_lowh_allocator_switch_controls.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; no new gain; production premises remain OPEN. |
### LUNA-2690 — Poseidon r9 low-h H-NORMAL versus H-ONE (2026-10-19 00:26)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2690-POSEIDON-R9-LOWH-HNORMAL-20261019 | r9, a=28, LD_CF=1/32, H-NORMAL/H-ONE controls | COMPUTED / CONDITIONAL / ALIVE | H-NORMAL score 65.91335; valid H-ONE score 66.24692; direct NORMALD=0/AMORT=0 rejected by the model assertion. | research/luna/item2690_poseidon_r9_lowh_hnormal_hone_control.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; H-NORMAL premise and organizer acceptance remain OPEN. |
### LUNA-2691 — Poseidon r9 low-h TRUNC2 control (2026-10-19 00:29)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2691-POSEIDON-R9-LOWH-TRUNC2-20261019 | r9, a=28, LD_CF=1/32, TRUNC2 control | COMPUTED / KILLED CONTROL / ALIVE | TRUNC2=0 and 1 produce exactly the same N, time, memory, and score 65.91335. | research/luna/item2691_poseidon_r9_lowh_trunc2_control.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; TRUNC2 is not a lever at this point; premises remain OPEN. |
### LUNA-2692 — Poseidon r9 low-h MIDPROD sweep (2026-10-19 00:30)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2692-POSEIDON-R9-LOWH-MIDPROD-20261019 | r9, a=28, LD_CF=1/32, MIDPROD masks 0..7 | COMPUTED / KILLED CONTROL / ALIVE | Every MIDPROD mask ties exactly at N=7,111,732,207,721,979 and score=65.91335. | research/luna/item2692_poseidon_r9_lowh_midprod_sweep.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; MIDPROD is not a lever here; production premises remain OPEN. |
### LUNA-2693 — Poseidon low-h extended value-domain KAT (2026-10-19 00:32)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2693-POSEIDON-LOWH-EXTENDED-KAT-20261019 | Owned value-domain stage-C self-test across 8 additional small shapes | COMPUTED / PARTIAL / ALIVE | Exact equality with independent coefficient-domain reference for m=1,3,7,15,31,63,97,127 and varied K,h; all checks pass. | research/luna/item2693_poseidon_lowh_extended_kat.md; research/levers_1018/pos_vdc_low/vd_kat.py | 0.00000 claimable bits; production r9 self-test, H-NORMAL premises, and organizer acceptance remain OPEN. |
### LUNA-2694 — Poseidon r9 low-h neighboring-a check at LD_CF=1/32 (2026-10-19 00:34)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2694-POSEIDON-R9-LOWH-CF32-A-20261019 | r9, LD_CF=1/32, neighboring a controls | COMPUTED / CONDITIONAL / ALIVE | a=28 remains exact minimum at 65.91335; a27/29/30/31 are 65.91647/65.98019/66.01700/65.98729. | research/luna/item2694_poseidon_r9_lowh_cf32_neighbor_a.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; no new gain; production premises remain OPEN. |
### LUNA-2695 — Poseidon r9 low-h fine LD_CF plateau (2026-10-19 00:37)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2695-POSEIDON-R9-LOWH-CF-PLATEAU-20261019 | r9, a=28, fine allocator fractions around 1/32 | COMPUTED / KILLED CONTROL / ALIVE | LD_CF=1/40..1/31 all exactly tie at 65.91335; 1/28 and 1/24 jump to 65.96030. | research/luna/item2695_poseidon_r9_lowh_cf_fine_plateau.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; no hidden gain; production premises remain OPEN. |
### LUNA-2696 — Poseidon r9 low-h VCNT sweep (2026-10-19 00:45)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2696-POSEIDON-R9-LOWH-VCNT-20261019 | r9, a=28, LD_CF=1/32, VCNT controls | COMPUTED / CONDITIONAL / ALIVE | VCNT=32,768–131,072 form a shallow floor; VCNT=65,536 full ledger N=7,111,040,815,586,811, score=65.91321. | research/luna/item2696_poseidon_r9_lowh_vcnt_sweep.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; only 0.00014-bit model gain; production premises remain OPEN. |
### LUNA-2697 — Poseidon r9 low-h BIG_EXP allocator threshold (2026-10-19 00:47)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2697-POSEIDON-R9-LOWH-BIGEXP-20261019 | r9, a=28, VCNT=65536, allocator threshold controls | COMPUTED / KILLED CONTROL / ALIVE | BIG_EXP=24 is exact best at 65.91321; forced exponents 22,23,25–28 are worse. | research/luna/item2697_poseidon_r9_lowh_bigexp_controls.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; no gain; production premises remain OPEN. |
### LUNA-2698 — Poseidon r9 low-h allocator sites at VCNT=65536 (2026-10-19 00:49)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2698-POSEIDON-R9-LOWH-VCNT-SITES-20261019 | r9, a=28, VCNT=65536, allocator-site controls | COMPUTED / CONDITIONAL / ALIVE | tmp1/inv0/div0 remains exact winner at 65.91321; alternatives 65.94721–65.97521. | research/luna/item2698_poseidon_r9_lowh_vcnt_allocator_sites.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; no new gain; production premises remain OPEN. |
### LUNA-2699 — Poseidon r9 low-h TRUNC2_SHRINK control (2026-10-19 00:59)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2699-POSEIDON-R9-LOWH-SHRINK-20261019 | r9, a=28, VCNT=65536, TRUNC2_SHRINK masks | COMPUTED / PARTIAL / ALIVE | Masks 0,1,2 tie at 65.91321; masks 3–6 hit model/host memory failures and mask7 was not run. | research/luna/item2699_poseidon_r9_lowh_shrink_controls.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; failed masks are unpriced, not evidence of a gain; production premises remain OPEN. |
### LUNA-2700 — Poseidon r9 low-h shrink-mask threshold classification (2026-10-19 01:03)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2700-POSEIDON-R9-LOWH-SHRINK-THRESHOLD-20261019 | r9, shrink masks across a/VCNT controls | COMPUTED / PARTIAL / ALIVE | Shrink masks 3–7 are score-neutral where computable; a28/VCNT32768 mask3 completes at 65.91321; only VCNT65536 event walk fails memory. | research/luna/item2700_poseidon_r9_lowh_shrink_threshold.md; research/levers_1018/pos_vdc_low/probe_fixed.py | 0.00000 claimable bits; failures are resource limits, not score evidence; production premises remain OPEN. |

### LUNA-2701 — Poseidon A09 strict stage-C/stage-D transfer (2026-10-19 15:16)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| LUNA-2701-POSEIDON-A09-STRICT-STAGED-20261019 | A09 strict stack, r13/r17/r19/r20/r21/r22, `LD_OUTER=2` | COMPUTED / DERIVED / CONDITIONAL / ALIVE | Combined scores are 83.58000 (r13), 102.17503 (r17), 121.10171 (r21), and 126.03533 (r22); exact stage-D savings are 0.10986, 0.16744, 0.18210, 0.18994, 0.19162, and 0.20266 bits for r13/r17/r19/r20/r21/r22 respectively. | research/luna/item3026_poseidon_a09_strict_stage_d_transfer.md; research/levers_1018/pos_stack/stageC_time/RESULT.md | 0.00000 claimable bits; package/kernel proof, production premise, and organizer acceptance remain OPEN. |
### LUNA-3419 — SC_PRUNE toy KAT post-crash replay (2026-10-20)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| `LUNA-3419-POSEIDON-SC-PRUNE-TOY-KAT-20261020` | finite-field grouped SC_PRUNE forward/retained-output model | VERIFIED / COMPUTED / PARTIAL | 252 checks pass at p=998244353 for lengths 16,32,12,24, all K<=L/2, with 3 vector cases. Production source integration remains absent. | `research/luna/item3419_poseidon_sc_prune_toy_kat_postcrash.md`; `research/luna/poseidon_sc_prune_exact_toy_1020.py` | 0.00000 claimable bits; toy-only evidence, no production score. |
### LUNA-3420 — SC_COL toy KAT post-crash replay (2026-10-20 04:12)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| `LUNA-3420-POSEIDON-SC-COL-TOY-KAT-20261020` | finite-field grouped-column SC_COL forward/inverse toy model | VERIFIED / COMPUTED / PARTIAL | 80 checks pass at p=998244353 for lengths 16,32,64,128 and group layers 2,3. Production source integration remains absent. | `research/luna/item3420_poseidon_sc_column_toy_kat_postcrash.md`; `research/luna/poseidon_sc_column_exact_toy_1020.py` | 0.00000 claimable bits; toy-only evidence, no production score. |
### LUNA-3425–3431 — post-crash SC arithmetic/source replays (2026-10-20)

| id | scope | status | exact result | evidence | score treatment |
|---|---|---|---|---|---|
| `LUNA-3425-POSEIDON-SC-PRUNE-COUNT-REPLAY-20261020` | SC_PRUNE split-boundary charge formulas | VERIFIED / COMPUTED / PARTIAL | 6,944 explicit-loop checks pass for `VD_SPLIT=0,1`, `cnt=1,7,8,9`, radix-2 lengths 16..256, radix-3 lengths 12..192, all `K<=L/2`. | `research/luna/item3425_poseidon_sc_prune_count_replay_20261020.md` | 0.00000 claimable bits; field/source integration open. |
| `LUNA-3426-POSEIDON-SC-FUSE-SOURCE-REPLAY-20261020` | existing fused NTT source precedent | VERIFIED / COMPUTED / PARTIAL | `pu4c_sq` and `pu4c_mul` register-interval checks pass; SC_FUSE-specific G/R, twiddle, split, liveness and KAT remain open. | `research/luna/item3426_poseidon_sc_fuse_source_replay_20261020.md` | 0.00000 claimable bits. |
| `LUNA-3427-POSEIDON-SC-OUT-TOY-REPLAY-20261020` | SC_OUT row/position toy layout | VERIFIED / COMPUTED / PARTIAL | 90 finite-field forward/inverse checks pass for lengths 16,32,64,12,24 and positions 1,3,7. | `research/luna/item3427_poseidon_sc_out_toy_replay_20261020.md` | 0.00000 claimable bits; C/source integration open. |
| `LUNA-3428-POSEIDON-SC-REGISTER-FLOOR-REPLAY-20261020` | SC register-live floor | VERIFIED / COMPUTED / CONDITIONAL | Sequential `SC_FB2` b=1 uses 16 words and fits 18; eager all-lane R2/G2 uses 22 and spills 4. | `research/luna/item3428_poseidon_sc_register_floor_replay_20261020.md` | 0.00000 claimable bits; compiler/ABI open. |
| `LUNA-3429-POSEIDON-SC-MID-TOY-REPLAY-20261020` | fused SC_MID segment | VERIFIED / COMPUTED / PARTIAL | 220 fused-versus-unfused finite-field checks pass for lengths 16..256 and positions 1,3,7. | `research/luna/item3429_poseidon_sc_mid_toy_replay_20261020.md` | 0.00000 claimable bits; production integration open. |
| `LUNA-3430-POSEIDON-SC-MID-CHARGE-REPLAY-20261020` | SC_MID charge table | VERIFIED / COMPUTED / CONDITIONAL | Exact `a=4..32` table reproduced; savings are positive for `a mod 3=1,2` and negative for `a mod 3=0`. | `research/luna/item3430_poseidon_sc_mid_charge_replay_20261020.md` | 0.00000 claimable bits; source absent. |
| `LUNA-3431-POSEIDON-SC-MID-PLAN-REPLAY-20261020` | SC_MID row/exponent map | VERIFIED / COMPUTED / CONDITIONAL | Exact r13/r17/r21/r22 plan deltas reproduced; r17 Lq and r21 Le/Lq lose while other plans save. | `research/luna/item3431_poseidon_sc_mid_plan_replay_20261020.md` | 0.00000 claimable bits; implementation/organizer premise open. |
