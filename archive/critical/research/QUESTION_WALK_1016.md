# QUESTION_WALK_1016 (merged from 8 walks, about 110 items, 10-16 00:34 MDT)

Nothing was run during these walks; everything comes from reading files. The one exception is a seconds-long check of the Orchard MDS characteristic polynomial, which closes GKR. Gains not marked "measured" are estimates or ledger arithmetic.

## 1. BUILD now (ranked by gain)

1. **Poseidon r7 algebraic paper entry.** New row: about 58.1 against generic 127.0.
   - Next: build it from the POSR5T template (m = 6.10e8, N = 3·2^29, memory about 2^37.22, P14 ladder plus r3-r5 outcomes, no experiments).
   - First run ledger.py at r6/r7 (seconds). Measured stage-D share rises: 0.20 at r4, 0.28 at r5.
   - Stage it. File after the e51feba1 ruling shows the no-experiment template passes. The r6 run keeps going.
2. **R37ZF4 = exact event plus R37M.** About -1.3 bit (exact/cell 2.458, measured on a different line), plus about -0.05 from PLACE 7 to 6.
   - Next: replace the lowm.py rows-22+ q3 stage with an exact replay. Run the joint check under R16x plus the four patterns (16 reps, against a cell control).
   - If the ratio is 2.3 or more: preregister 2×128 reps (about 1 h on 12 cores), restate H2 and H3 (q3 then exceeds 2^-70), and set PLACE = 6.
   - File as a refile or a new best, depending on the 96933f8e ruling.
3. **LS1 r9..r22 (new rows), with bitpacking checks.**
   - Next: in wf_2100e2fc, for each row:
     - confirm the streamed and non-streamed generators give the same prog.bin;
     - confirm the generator peak is ≤ 2^20 under prlimit;
     - confirm sha3gen v3 gives -0.060 at r9 and -0.112 at r24 under cert.py;
     - run prefile, then let lanefiler queue rows from r9 upward.
   - Skip r23 and r24 (they lose).
4. **sha256-r39 composed build** (rolled bitslice -0.352 measured, peel, 744875ec tricks, D2): about 124.39 against the leader at 124.83.
   - Next: check slot pos_sha256v3_r39 ships the dariolina prefix, with credit and the dependency id.
   - File when intake passes, under the standing go. Retire the s39-bitslice LEVERS row.
5. **POSR5U smallblock / arena** (merged from 3 walks): -0.234 against 5T (RECOMPUTE #1). It stacks with #8 to about -0.500.
   - Next: allocator-replay simulator with SMALL_BLOCK 4 MiB. Replay r3, then the r5 plan sizes, and set ARENA to the extent plus about 2%.
   - Then one counted r5 run on the cloud (nice 19, beside r6). File after the 27d33f4a ruling.
6. **B3R4f** on 9f69f1cc: 7-byte entries -0.0689 (measured, certify passed) plus kappa 11 to 10 at -0.0087.
   - Next: one lean agent builds it and adds the H4 conservativeness premise from the 41b32afc dossier. File after the 9f69f1cc ruling.
7. **B3Z8 (honest SEL), with the sel-rss correction.** The earlier "not valid" audit was a meter artifact: kissat exit code 10 means SAT. Runs 11, 38, 51 and 72 are valid at 2^26.28-26.73. Stopped runs peaked at up to 2^27.26.
   - Next: give the B3Z8 build the 8-run table. Set the SEL cap at or below 2^27.657 and disclose that the stopped runs were still growing.
   - Make `--ok-exit 10,20` the default in sel-rss one.sh. File after the 49b6e819 ruling.

## 2. PROBE in minutes (ranked by prize)

1. **Poseidon K=1 probability bound** (1 bit on every algebraic row).
   - Next: exact inclusion-exclusion root probability for a random degree-m polynomial over F_p, plus a small-prime toy count in a fresh script.
   - If it holds, build a K=1 twin of the r7 entry as the second filing.
2. **B3Z SEL cap ladder** (lanecopy plus self-driving SEL; up to about 1.3 bit if SEL can sit near 2^26).
   - Next: run one of the 116 SEL instances under prlimit at 128, 96 and 64 MiB (kissat --time, nice 10, own PIDs).
   - If SAT at 96 MiB or less: build B3Z9 (single-copy tables plus a C generator; check the CNF sha256 against the log).
3. **Lean CDCL constraint** (prize about -6 on both r37 and r38).
   - Next: stop the 8 stuck cloud seeds (own PIDs via cloud_leancdcl_check.sh).
   - Add the merged 6/7-operand adder constraint to leanchar.c; also hand-read 2026/232 and arXiv 2406.20072 for constraints.
   - Benchmark the row-14 truncation (300 s, 3 seeds; row-10 baseline is 65 s). Relaunch only if row 14 solves.
4. **r6fast validation** (about 0.75 bit: time -0.54, memory -0.21).
   - Next: when cloud cores free up, run exec_r6fast/val_run.sh at RR=3, then RR=4, and diff against exec_r6mt.
   - Build the package after the r6 run reports its stage-D peak (ARENA about 31.46e9).
5. **Poseidon control share** (ctl is 37.6% of r5 ops; estimate -0.30 to -0.68).
   - Next: separate counters (address, kf_run dispatch, block loops, group loops) in a copy of exec_r6mt at r3.
   - If dispatch plus address is 20% or more: add an unrolled kernel to gen_kern.py and price r6/r7.
6. **Poseidon ledger agent** (one scratch copy of ledger.py, r3-r8). It prices:
   - the two-level twiddle table (net about -0.03 to -0.06 per row);
   - one buffer less at the peak, GBUF/PEAK (about -0.56 at r7 per 51.5 GB buffer);
   - drain schedule (free each C/D buffer at its last read);
   - CACHED_POW (time plus memory).
   - Fold into the r7/r8 paper rows only. Do not touch r3-r6.
7. **Poseidon funcdec d=78,125 and r3 d=390,625** (j=0): -2.3 if it decomposes, low prior.
   - Next: full-expansion B-adic digit test with flint, 15 min cap, nice 10.
8. **minipos BACKSKIP / ZEROSUM / MITM**: -2.3 bit if wrong; expected CLOSE.
   - Next: one agent on our own minipos.py.
   - Counts: q = 23/43 line-pair collisions against random; q = 103/257 coset sums.
9. **s37-Gprime** (+0.43 to +0.63, or -0.21).
   - Next: split the 96933f8e ledger into per-first-block and per-variant cost. If per-first-block dominates, build G'; otherwise CLOSE at -0.21.
10. **s37-ACfloor.**
    - Next: minilab sha256 w=8, S=39 CNF with kissat --time=300, against w8 rho wall time.
    - Full metered search only if the 96933f8e ruling names published inputs.
11. **512 lanes at r9 generic** (ideal -0.050).
    - Next: exact ledger trading DP-table size against lanes. Build if the net is below -0.02.
12. **s6-dprho** (about -0.06 against 124.19636).
    - Next: count transpose/gather ops per step (minilab lw=8). Build if the margin is 0.05 or more; otherwise CLOSE.
13. **b3r7-unroll** (+0.236 loop cost to win back).
    - Next: B3R7b listing, net time_log2 for unroll 1..5. Fold into the Lemma v2 refile if the gain is 0.05 or more.
14. **s6-chi 10-gate on r6** (about -0.03).
    - Next: diff trick/gen.c against the LS1C2 r6 generator, then selftest, a 300-message KAT and the ledger. Fold into the next r6 refile if better than -0.01.
15. **b3-ratemult.**
    - Next: charge the D431 ExtraTrees feature ops and score on D448 held-out data. PARK if the net is under 0.05.
16. **tail1618 r38, then r37** (expected CLOSE).
    - Next: re-key wall_sat cnf to chi38/chi37 rows ≤16 with CV1 fixed. kissat --time=280 on 8 CV1s, 2^28 cap.
17. **SOLCLOUD-19.**
    - Next: bit-blast q=4 shared-E3 to CNF, kissat --time=600. SAT means lift to q=8; UNKNOWN means PARK all rows.
18. **Close-tests, minutes each:**
    - s7-partialbday: minilab 12+12 against rho.
    - s39-lut16: build_lines dependency walk.
    - cr-constants: line-eval ops against C(r) on minipos w=20.
    - posr2-hcent: `yukon benchmark show --json`; stage a seeded-centre fix if live.
19. **Greps that may close, seconds each:**
    - pos-r2-qn1: MU/g recompute per trial in exec_r3/r5 lean.c.
    - b3-alignedwalk: walk terms in b3z7 frontline.py.
    - b3-Zrate: hit factors against gridwave6.
    - b3-swaplength: does B3Z use the omega list?
    - b3-h1lambda: H1' in the B3Z8 ledger.

## 3. CLOSE (with reason; empty squares count)

- **Already filed, awaiting a ruling:**
  - posr5-arena: 27d33f4a.
  - posr3-transform: c4ee5996; fix the LEVERS row.
  - ls1r8 and s8-band: b42c0bd2.
  - b3z7-selcap, b3z7-exact, b3-fillpremise and b3z6-codecount: in B3Z7E/E2.
- **Already applied or in-line:**
  - s37-R16x (in R37ZF3).
  - s38-W23full (the P8 event already counts it).
  - s38-d783 (R38V §7.4 is stronger).
  - s6-8xor and s6-batchK (filed; stranded under the memory rule).
  - s5-popcount (R5N3 rejected it).
  - b3-coupledomega (B3Z already couples).
  - s39-prefixgrind (in the composed build).
- **Superseded:**
  - pos-shortprod (about 1.0x; r6fast dominates; mark LEVERS 481).
  - s39-bitslice (in the composed build).
  - s37-zplane (table line about 93).
  - s38-stack (P8 has its own trail).
  - s6-widerkey and s6-pcache (table line).
  - b3-Zrate (B3Z dominates).
  - b3r3bs2 (BS3 replaced it).
  - s7-exitboard (stale; check f4f7b40e is pkgU).
  - b4-mem2to20 (7-byte entry wins).
  - b3z5-selrss (as a B3Z5 audit; its numbers go to B3Z8).
  - d180 blocker (owner gone).
  - s37-accap (A_C dropped).
  - s37-cube (spent development memory sets the floor; lean CDCL supersedes; drop d10/d12 after reading their outputs, owner's call).
- **Wall or structure, our own tests:**
  - s39-paper1120 and s39-semifree (C1981, Grok 121/122, 0/512 neutral bits).
  - s3940-sched (r39 structured path closed).
  - b3r3-diff and b3r3-modetree (spider test, Grok 125, +1 bit).
  - s7-multiblock (D4: 0/30,000).
  - s39-lazyrot (measured 2206 ops; send mask-sharing, about -0.08, to the composed build).
  - b4-pivot for 2-input gates (BFS lower bounds; narrow or cancel Grok 130).
  - b4-lazycarry.
  - b4-keyedmode and b4-treemode (excluded by rule; tested negative).
  - b3-thiwalk (-0.003; invalid variant).
- **Poseidon r1/r2 (track closed):**
  - pos-skip-gkr and pos1/2-gkr: census z = 0.77; Orchard MDS charpoly irreducible, rank 3, so no invariant subspace. Add this as a COMPUTED cell.
  - pos1-freelunch and cheaplunch: floor D² exceeds N on live rows.
  - pos1-groebner: conditional on the Luna 3 regularity formula giving d > 8.
  - pos2-machaddr: the r2 cells close; the transfer is PROBE #5.
- **Measured outcomes:**
  - posr4/5-centre1: r4 centre 1 failed and centre 2 succeeded; r5 centre 1 succeeded. Record in PR4-O01.
  - posr4-ladder: D share rises at r4/r5. Record in PR4-O02.
  - pos-funcdec r ≤ 2, d ≤ 125: complete.
- **Zero score value:**
  - cr-constants (all 15 match).
  - s38-densesigned (about 2^-12 of N).
  - s38-102cond (no ledger uses it; errata note).
  - b3-d179 (wrong line, ≤ 0.02; stop SMT).
  - s7-regconv dig cell (priced at 0.449; fallback 3183c941).

## 4. PARK (with trigger)

- **Ruling triggers:**
  - s37-densesigned and s37-prepmem: reopen if the 96933f8e ruling names published inputs or memory. The H.2 sentence is ready: claim 2^27.57 (-0.43) and scope out the old 2^28.1-2^31.5 runs.
  - s7-regfile: package KR=1188 if f4f7b40e is refused.
  - r5n3-legacy and s5-round2anf: only if fc57f343 is refused or R5N is rebuilt anyway.
- **Owner decisions:**
  - b4-zerodecode (convention).
  - b3r7b-crumbs (compact encoding decision first).
  - s6-rotation (separate four-copy filing needs a go).
  - Organizer batch: add R8 and R2 (s39-wordop), and the C(7) normalisation.
- **Low value or unproven:**
  - s37-workcap, s38-prologue, s37-zoned, s37-r37m-dense, s37-altsign.
  - s6-row, s6-alt8bridge, s6-widerkey-coset/141, s7-ktighten (literals in the next LS1R7 rebuild), s7-algdegree.
  - b3m-stream, b3-swaplength, b3-alignedwalk, b3-h1lambda (greps in PROBE #19).
  - pos1-regs, pos1-zinf, pos2-qn1 (via PR4-L02), dig-lit-poseidon (waits for minilab v2).
- **Need an outside answer:**
  - s37-bit31char: Grok 119 pure-math ask.
  - s6-zerodigest: ask Grok for an explicit core.

## Rulings to fetch

27d33f4a, c4ee5996, b42c0bd2, 49b6e819, 9f69f1cc, e51feba1, 96933f8e, fc57f343, f4f7b40e, 8fbecd8a (Lemma v2).

## LEVERS / OPEN.md relabels

- Mark 481, 483, 313, 161 and 236 (and the rows above) per the CLOSE list.
- OPEN.md rows 20, 24, 33-37, 39-43, 46-47, 51-54, 59, 163, 166, 191-203 and 207-208.
- Nothing has been edited yet.

Files:
- ./research/QUESTIONS.md
- ./research/LEVERS.md
- ./research/dig/OPEN.md
- ./HANDOFF.md