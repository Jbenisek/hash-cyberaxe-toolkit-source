# Where the deciding compression can sit (blake3-r2), 2026-10-08

Key: FIX = fixed constant; TRIAL = free per trial (solvable inside a trial at no extra cost); OUTER = free per outer step (fresh random value, not chosen); COST = choosable only at the stated cost; DIFF = usable only as a difference between the two messages. L = length-difference lever (v14). C = counter solved per trial (v12). t = chunk index, n = chunk count.

| # | Context (both messages, unless a pair is named) | v15 flags | v14 block length | v12, v13 counter | v0..v7 | Levers |
|---|---|---|---|---|---|---|
| 1 | Single-block chunk = root (message 0..64 B) | 11 FIX | 0..64; 0 only for the empty message; bytes past the length are forced to 0. DIFF (e.g. 55 vs 63): 65 values, not a solvable word | 0, 0 FIX (root counter) | IV FIX | L yes, C no |
| 2 | First block, root chunk (message 65..1024 B) | 1 FIX | 64 FIX | 0, 0 FIX | IV FIX | none |
| 3 | Middle block, root chunk | 0 FIX | 64 FIX | 0, 0 FIX | chained: OUTER (1 compression per fresh value); chosen value COST 2^256; a 1-word difference COST 2^112 (AROUND sec. 6) | none |
| 4 | Last block, root chunk (message 65..1024 B) | 10 FIX | 1..64, DIFF | 0, 0 FIX | chained: OUTER, as row 3 | L yes, C no |
| 5 | First block of a non-root chunk (any t) | 1 FIX | 64 FIX | t: v12 any 32-bit, v13 0..2^19-1 (t <= 2^51-1). TRIAL, shared by both messages. Price: message > t KiB (up to 4 TiB over the full v12 range), about 17t compressions once to hash it | IV FIX | C yes, L no |
| 6 | Middle block of a non-root chunk | 0 FIX | 64 FIX | t: OUTER only. t also feeds the chained CV, so changing it costs the earlier blocks again | chained: OUTER | none |
| 7 | Last block of a non-final chunk | 2 FIX | 64 FIX (non-final chunks are always 1024 B) | t: OUTER | chained: OUTER | none |
| 8 | Last block, multi-block final chunk (final chunk 65..1024 B, n >= 2) | 2 FIX | 1..64, DIFF | t = n-1 >= 1: OUTER (feeds the chained CV) | chained: OUTER | L yes, C no |
| 9 | Single-block final chunk (final chunk 1..64 B, n >= 2) | 3 FIX | 1..64, DIFF | t = n-1 >= 1: TRIAL, shared. Same price as row 5 | IV FIX | L yes, C yes (only context with both) |
| 10 | Parent node, not root | 4 FIX | 64 FIX | 0, 0 FIX | IV FIX. Block = child CVs: OUTER (at least 1 child compression per fresh half); a chosen value COST 2^256 | none |
| 11 | Root parent (n >= 2) | 12 FIX | 64 FIX | 0, 0 FIX | IV FIX. Block = child CVs, as row 10 | none |
| 12 | Pair, block shift: A's first block vs B's later block, same t (A's chunk is shorter) | DIFF in bit 0: 1 vs 0, 3 vs 2, 11 vs 10 | 64 vs 64, or DIFF on a final block | equal (0, or t on both) | IV vs chained: a forced DIFF (START bit set exactly when CV = IV). Pinning B's CV to IV on all but the chosen words COST >= 2^224 | L possible. C no (t moves B's chained CV) |
| 13 | Pair, root level: single-chunk root vs root parent | DIFF: 11 or 10 vs 12 | len vs 64, DIFF | 0, 0 on both | IV vs IV, or chained vs IV | L only alongside a forced flags DIFF. Dead at 2 rounds (AROUND sec. 0.3) |
| 14 | Pair, leaf vs parent: final chunk of the shorter message (t = n1-1) vs a parent of the longer (n2 = t+q, 2 <= q <= lowbit t) | DIFF: 2 or 3 vs 4 | len vs 64, DIFF | t vs 0: the only legal counter DIFF | IV (or chained) vs IV; partner block = child CVs | C only as a DIFF. Dead at 2 rounds except t a multiple of 2^32, about 2^256 (AROUND sec. 0.4) |

Notes
- COMPUTED: ctx_check.py and ctx_check.txt in this folder, with the organizer verifier imported read-only at rounds=2. They log flags, length, counter and CV origin for message lengths 0, 1, 64, 65, 1024, 1025, 2112 and 3772. Checked: START is set exactly when CV = IV (9 lengths); root counter is 0; parents use IV, counter 0, length 64. Leaf vs parent: A (3 chunks) and B (4 chunks) give equal root inputs except words 8..15, which are CV(A chunk 2: v12=2, v14=50, v15=3) and CV(B parent: v15=4). Block shift lines up for the root chunk and for the final chunk at t=1. Largest t = 2^51-1, so v13 <= 2^19-1.
- Why "flag" is empty: v15 is FIX in every context, rows 1-11, so it is never a free word. A flags difference appears only in rows 12-14. Each one brings a second difference that either kills the attack at 2 rounds (rows 13, 14, per AROUND) or costs at least 2^224 (row 12, IV vs a random chained CV). No flags path survives to be counted.
- Why CV has 1 path: v0..v7 is either IV (FIX) or a random chained or child output (OUTER). Nothing chooses it below preimage or partial-collision cost, so the only CV route is AROUND's h2-difference route at 2^112.
- "mem": the files this audit was allowed to read do not cover it, so it gets no answer here.
- Untested: the counter lever (rows 5 and 9) needs a message of about t KiB, up to 4 TiB. The domain allows that, but we did not check whether intake or the verifier run accepts it.
- DERIVED, not run: a difference in END or ROOT alone never lines up. A chunk-final or root output goes to the tree or the digest; a non-final output goes to the next block. Two middle blocks (0 vs 0) are a plain chained-CV collision.
