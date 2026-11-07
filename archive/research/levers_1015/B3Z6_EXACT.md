# B3Z6 exact code counts - 2026-10-15
**Verdict: NOT COUNTABLE as of now. No code generator exists; the 2^21 and 2^20 parts are proof-text allowances for machine code that was never emitted.** Nothing was run (no counting run possible), so no peak_mem measured.

## What was found
- make_b3z6.py does not generate code. It text-edits pkgB3Z5's proof.md/claim.json. Line 72: CODE_I = 28*2^9 + 2^17+2^7 + 10*2^9 + 2^21 + 2^20 is a sum of bounds from the proof (Section 12 "Its size", proof.md line 971); CODE_I_BOUND = 3,300,000 is charged (3,300,000*32 = 105,600,000 B).
- The package program (experiments/) is a Python program with loops; the proof (line 866) says its schedules are "an upper bound written out by blocks ... not counts of an executed program". memcomp/blake3-B3Z has only DESIGN.md/ANATOMY.md notes (ANATOMY line 24: "generator is ~ few KB"), no emitter. Grep for emit/instr-count in b3z6_build, pkgB3Z6, memcomp/blake3-B3Z: nothing relevant.
- So the step 2 premise (run a generator count-only) fails: the machine-code program for the solver / context / routine does not exist. Per the task, stopped; nothing run, nothing uncapped.

## Bounds that could be tightened, with what is known (NOT counts)
- Solver: proof line 961 says "432 static nodes over the six rows of S ... fewer than 2^14 labels, at most 256 operations each"; Section 12 charges 2^14 labels x 2^7 instr. 432 nodes x 2^7 = 55,296 instr would be 38x below 2^21, but 432 is the node count of the 6 rows only; the G7/G15 prescribed-bit nodes and the "prefixes of free choices" expansion (up to 5 free choices per path) multiply it, which is where 2^14 comes from. Unknown without writing the traversal emitter.
- Context+routine+rest 2^20: context is 39 straight-line lines (90,917 units), plus step 3 compression, certificate, (G15), meter, cache/fill code. Plausibly ~1e5 instr, unmeasured.
- Illustrative ledger arithmetic only (all other terms unchanged: tables 4,895,744 w, misc 499,530 w, N = 3,162,212,250,308,201,329,187): base 70.72503.
  | assumed code instr | memory B | log2 mem | score |
  |---|---|---|---|
  | 3,300,000 (now) | 278,248,768 | 28.0518 | 70.725 |
  | 150,656 + 55,296 (solver 432x128) + 2^20 | 212,793,664 | 27.665 | 70.338 |
  | 150,656 + 55,296 (rest 0, floor) | 179,239,232 | 27.417 | 70.091 |
  | 0 | 172,648,768 | 27.363 | 70.036 |
  Gain range if a real emitter gave small counts: 0.39 bit (solver only exact) up to 0.69 max. Gain is at zero time cost ONLY if the solver is truly statically written; the proof already assumes that (60-line "written statically per row and per prefix", registers named in code), so exact counts would be consistent with the proof.

## What a B3Z7 filing would need (gain >= 0.03 bit is very likely IF exact counts exist)
1. Write an emitter for the solver traversal (statically per row and per free-choice prefix, per proof 9.4/9.5 "Registers of steps 2 and 3") and for the context/routine/step-3/meter code; count emitted instructions (count-only mode, under prlimit --as=268435456, nice 10). Needs the real machine layout (64 registers, 32 B/instr); sizeable build, hours.
2. Proof lines to change (line numbers of pkgB3Z6/blake3-r2/proof.md): 231-232 equivalent text at line 971 ("fewer than 2^14 labels of fewer than 2^7 instructions, fewer than 2^21; ... fewer than 2^20: ... 3,296,384 < 3,300,000 ... below 105,600,000 bytes"), the Section 12 memory table (search total 278,248,768 B, code row 105,600,000), the intro memory sentence "below 2^28.05181 bytes", claim.json memory value, and the SEARCH_B / SEARCH_L constants in make_b3z6.py (lines 72-76, assert SEARCH_B == 278248768). Ledger constants: CODE_I_BOUND, SEARCH_B, SEARCH_L (log2 ceil 5 decimals), and the memory term in the score. Time terms unchanged (N unchanged) provided the emitted code's units equal the ledgered ones.
3. Must also note the "once" 2^26 charge "writing the code of the search" (line 961) is a time allowance, unchanged. The note must follow research/rulings/ACCEPTED_PATTERNS.md (credit 40087647, same board; executed outcome, exact ledger).
4. Risk: judges accepted "upper bound written out by blocks" for time; replacing a memory bound with a count requires the program (shipped source) to actually contain that code or the judge cannot verify the count. Unclear whether the shipped Python's own instruction count can be claimed; that is the open question.
