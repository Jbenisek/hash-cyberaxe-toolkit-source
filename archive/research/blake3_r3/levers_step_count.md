# Chain step count: can 595 ops per 7-lane batch go lower?

Scope: `candidate_blake3/experiments/rho.py` (traced circuit, `build_hash` lines 124-149) and the ledger it prints.
Ran only: `py rho.py --selftest` (True, 595 = add 100, xor 88, shr 80, and 167, shl 80, or 80) and `py rho.py --ledger` (time_log2 125.10856). Scratch scripts were in the temp folder; nothing in the package was edited.

Answer: **0 operations saved. No lever in (a), (b), (c) or (d) beats 595 inside the stated op model (add, and, or, xor, shl, shr).**
The shipped tracer already does every constant fold asked about, and there is no dead work in the last round.

Value of an op: main loop per batch = (16*(595+4)+3)/16 = 599.1875 ops, share 0.9944.
time_log2 change per op saved = log2(1 - 0.9944/599.1875) = -0.00240. For 3 ops: -0.0072. For 4 ops: -0.0096. For 7 ops: -0.0169. (COMPUTED from the ledger formula; reference only, since no saving exists.)

## (a) Constant folding - ALREADY DONE (COMPUTED)
- Round-0 column G calls (m0..m7 = 0, IV, counter 0, length 64, flags 11): all 16 rotations and all adds/xors are on constants. `Tracer.add` returns ('c', ...) when no operand is variable (rho.py:84-85), `xor` likewise (101-102), `ror` likewise (115-116). State built from constants at rho.py:127; message zeros at rho.py:128. Zero message words add nothing (constant sum is 0, no add emitted, rho.py:82, 94).
- Round-0 diagonal G: v[a]+v[b] are both constants and are summed into one immediate (rho.py:82 sums all constants, 94-97 emits one add with an immediate). So `K + m8` is a single add. Emitted code has exactly 8 `add imm` (K+m8 and C+d in the 4 diagonal G) and 8 `xor imm` (D^A and B^c in the 4 diagonal G). These 16 immediate ops are the only constant-operand ops left.
- After round 0 all 16 state words are variable (the 4 diagonal G touch every word), so there is nothing more to fold in rounds 1-2.
- Fold the 8 xor-with-immediate? ror(x ^ K) = ror(x) ^ ror(K); the xor is still one op, and the rotated word is needed clean for both an add and an xor, so no absorption exists. Fold the 8 add-with-immediate (C + d)? C is added to a variable from a rotation; no. Result 0.
- swar_count.py gives 612 for the same job (it adds constants as separate ops: 116 adds against 100 shipped). The shipped circuit is already 17 ops better than the counter.

## (b) Last round, dead results - NONE (PROVED by data flow, COMPUTED by program)
- Digest = v[i]^v[i+8] for i = 0..7 uses all 16 final state words: v0..v3 (a), v4..v7 (b), v8..v11 (c), v12..v15 (d). Every final-quarter-step output reaches a digest xor (rho.py:142-146).
- Dead-code check on the emitted 595 lines (backward reachability from the return tuple): 0 dead lines. Common-subexpression check (also with swapped commutative operands): 0 duplicates.
- Last-step rotation: z_b = ror7(B^C2) ^ d2'. The d2' (ror8 result) already exists clean because c2 = C + d2' needs it. Rewriting as ror7(t1 ^ rol7(d2')) needs a new 5-op rotation: worse (+5).
- Digest xor of two unclean values (z_a = a2 ^ c2) needs a mask for a clean output: 4 `and` (ops 584-590). Tested: leaving some of the four unmasked and feeding the unmasked word to the next batch (fixed point on input bounds, brute force over the 2^4 mask choices x lane bound 2^33..2^36): best = all four masked (595); every dropped mask costs +2 net (597, 599, 601, 603) because the unclean input overflows the 36-bit lane and forces extra internal masks. COMPUTED. Masking at first use instead of at output is the same 1 op.
- The filter mask is already shared: for s1 = 32 the ledger counts no `and` for the filter (rho.py:218), and z[0] is already masked by the circuit.

## (c) Rotations - NO SAVING (COMPUTED / PROVED for the 36-bit lane layout)
- Each variable rotation = shr, and, shl, and, or = 5 ops (rho.py:113-121): 80 variable rotations = 400 of the 595 ops. 16 of the 96 rotations are constants (round-0 columns).
- Both ands are needed at pitch 36: the right shift pulls the next lane's low r bits to positions 36-r..35, which overlaps the left piece's valid positions 32-r..31 whenever r > 4 (r = 7, 8, 12, 16 all do); the left shift sends bits r+4.. into the next lane. One mask after the or cannot separate them. Wrap tricks like (t + (low<<32))>>r need pitch >= 32+r.
- Merge a rotation with the next XOR or add: every rotation output is used twice (by an add and by the next xor), so the `or` cannot be dropped: splitting into two adds plus two xors costs 4 ops against 3. No rotation can be deferred past an add.
- Sharing masks when two rotations are xored (ror7(t1)^ror8(t2): shared lo mask, three-mask form, 10 against 11) does not apply: in the digest the second term is the already-computed d2'.
- 3- or 4-op rotation forms exist only for duplicated lanes (pitch 64, 4 lanes) or pitch >= 32+r, which cuts the lane count. 8 lanes at pitch 32 needs about 6 ops per add (SWAR add), far worse. GUESS that no 7-lane layout does better.

## (d) Other exact simplifications - NONE FOUND
- Adds: constants merged, zero message words skipped; operand order does not change the number of overflow masks. Internal masks: 3 (ops 507, 538, 568, in round-2 diagonal G5, G6, G7, where the a-chain bound passes 16 units = 2^36; chain bounds printed: 15.53, 14.81+1+1, 15.07+1 units). Avoiding them needs a tighter worst-case sum bound (a proof that the maximal terms cannot coincide). GUESS that this is false: the terms are independent-looking 32-bit values. Not shown.
- Mask count: 160 inside rotations + 3 internal + 4 final = 167 `and`.
- Loop overhead (outside the step): stage1 = 4 ops (add, and, compare, branch), 3 ops per 16-batch body. Raising U_UNROLL from 16 to 64 would save 0.14 op per batch: time_log2 about -0.0003 (COMPUTED from the ledger formula). The 64 KiB source limit may forbid it; not checked.

## Conclusion
- Savings found: (a) 0, (b) 0, (c) 0, (d) 0 chain-step ops. time_log2 stays 125.1086 from this direction.
- The only things that could still move the chain step: a different lane layout, or a proof of tighter lane bounds (removing the 3 internal masks would be -3 ops = -0.0072 bits). Neither is shown.
- No program change is proposed.
