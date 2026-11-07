# Poseidon-algebraic row dig, r3..r21 (2026-10-17, dig agent)

Cells: 266. Before: 159 OPEN. After (poseidon-algebraic.dug.jsonl): 136 COMPUTED, 104 LOCAL_ONLY, 26 OPEN. 133 cells closed. CELLS.jsonl and the other families' files untouched. Method: ledger.py run at nice 19 (r3..r11 full evaluate, minutes), small patched scratch runs, and our RESULT files. Nothing built, filed or staged.

## What was run
- ledger.py evaluate(r,[0]) r3..r11: reproduces 38.58536 / 42.87211 / 47.12610 / 52.81457 / 57.07357 / 61.35502 (r3..r8) and gives notional r9 67.04342 (staged block model 68.66055), r10, r11.
- Stage shares (Q13): half-gcd D share 16.3 % (r3), 20.1 % (r4), 28 % (r5), 25 % (r6), 29.6 % (r7), 36.7 % (r8), 34.6 % (r9 notional), 40.0 % (r10), 44.5 % (r11). Powering C falls correspondingly. B (build_g) under 1 %.
- Control (Q2): all loop control is 0.03-0.08 % of a trial; the modelled xalloc walk is under 1e-6. Control cannot move the score. Allocator over-charge is 0.0055-0.0072 bit (LEDGER.md).
- Packing (Q4): 32 B elements are 0.4 % above ideal (0.006 bit); the padded transform length is the real packing term.
- Preprocessing (Q7): only the twiddle table, 0.00001 % of the total. Nothing free or hidden.
- Number theory: p-1 = 2^32 * 3 * 463 * ...; 9 does not divide, so radix 3 is the only usable small odd factor.
- Plan regime (Q12): N/(2m-1) for the 3*2^b plan is 1.611 (r3), 1.288 (r4), 1.031 (r5), 1.649 (r6), 1.319 (r7), 1.056 (r8), 1.689 (r9); the pure 2^a plan is 1.074, 1.10, 1.126 at r3, r6, r9.

## Empty squares (recorded, not guessed)
- No rival entry on the board at r6..r21 (01:00 MDT snapshot). Rivals exist only at r3-r5 (0xshikhar, 37.1 / 40.5 / 45.0 vs ours 37.98 / 43.83 / 46.98).
- No filing of ours at r6, r8, r9, r10 (r8b, r9, r10 staged; r6 not staged). r11 not buildable (half-gcd assumes matrix entries fit one block). r12 needs the w=1 premise (Grok 138/139) and L=3*2^41 products. r13..r21 only paper values.
- 26 cells still OPEN: Q2, Q5, Q9 at r12..r21 except where answered by structure. They need a block-multi cost model (r11), a premise branch for r>=12, and ledger support for a>39 (the r12..r21 ledger attempt did not finish in time).
- Not tested anywhere: A1 and A2 at r>=6, the r6 counted run (cloud, status not re-read), judge reading of the H_ci premise.

## Top 5 levers (bits x rows touched, all untested as programs)
1. Pure 2^a powering plan on rows r = 0 mod 3. Where 2^a >= 2m-1 closely (r3 1.074, r6 1.10, r9 1.126, ... r21), N falls by a third. Approximate model from ledger pass formulas: stage-C step ratio 0.697 (r3), 0.643 (r6), 0.648 (r9); total -0.42 (r3), -0.45 (r6), -0.38 (r9), about -0.38 for r12/15/18/21. 7 rows. It is the wrong direction at r = 1, 2 mod 3 (x1.35-1.39). Brief: add a rows==1 charge path to ledger.py (stageA_fwd, mulc_otf_row for one row), confirm with exec_r6mt at r3 (a 2^21 plan fits the 2^32 field), then build r6 first (unfiled row).
2. Buffer cut in both C and D (b3). -0.60 (r8) to -0.77 (r6) bit on r3..r8, GUESS. C and D tie within 448 B, so both must drop. Brief: audit the D peak composition above r3 (only verified at r3), design one N-buffer fewer in each.
3. Fractional trial charge. Success 0.4347 vs 0.39 required; the smallest real K is 1.73, worth 0.21 bit on r6..r21 if an early-stop or expected-cost charge were accepted. Judges charge worst case, so risk is high. Brief: ask the rules (cost-model text) before any build; no code needed.
4. Faster half-gcd. D is 25-45 % of a trial from r6. A 25 % cheaper hgcd gives -0.09 (r6), -0.14 (r8), -0.17 (r11) bit, on r5..r11. Brief: transform-reuse in apply_inv/mat_mul, price in ledger.py first.
5. Exact arena plan. Allocation order is deterministic; arena factor 1.177 costs 0.235 bit of memory on every row. r4 ran at 1.144 (-0.04 proven). Brief: simulate the allocation sequence with fragmentation at r3 (minutes) and find the smallest safe factor; all rows r3..r10. (Two-level/hoisted twiddle adds -0.03..-0.10 on top, already in Q9.)

## Pattern across rows
The three-row pattern (r = 0, 1, 2 mod 3) in transform padding drives which lever applies. The paper-score margin over generic is large (57+ bits at r8..r10) while every rule-risk is premise/evidence, not cost: rows r6, r8, r9, r10 are the unfiled paths.
