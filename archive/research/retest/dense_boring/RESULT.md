# Dense part (rows 0..15) boring-details audit - own code, from chi37.txt + proof.md definitions (2026-10-12)

Own C in this directory (common.h = SHA-256 trace + chi37 parser; basic.c, f67g.c, l16.c, lrelax.c, fib.c/fib2.c/fib3.c, hidden.c, hidden2.c, smc.c). No rival code run. WSL, <= 2 threads, machine load ~50.
Sanity first (basic.c): both members of the published pair reproduce the digest; every cell of rows -4..36, every '+' pair and all 31 two-bit conditions hold (0 failures). My own derivations give C4=000b362e, W8C=da3a7d2f, c7 const=ab9a1763, C6=f538a8f7, K3C=478132ed, d6/t6/d7/t7, dS0(W8)=043ff800=-d7: all equal the printed constants.

| # | printed | our count | match | method | time |
|---|---|---|---|---|---|
| 1 | \|F7\|=68,157,440 ; \|F6\|=287,309,824 ; p7=2^-5.97763 ; p6=2^-3.90197 | 68,157,440 ; 287,309,824 ; 2^-5.97763 ; 2^-3.90197 | yes | all 2^32 words, definition s0(w+d)-s0(w)=t; also their bitwise forms: 0 mismatches both | 56 s (2 thr) |
| 2a | \|G\|=12,103,680 | 12,103,680 (W8 cell + 3 printed two-bit conds = cell + exact modular s0 diff) | yes | 2^29 E4 values | ~40 s |
| 2b | 22,976 c7 classes (sizes 2..3600; 222 classes >=3456 = 782,800 variants) | 22,976 ; 2..3600 ; 222 ; 782,800 | yes | sort G by c7 | same run |
| 2c | mean passing classes 364.6 ; variants in passing classes 192,075 | 364.61 ; 192,075.0 (exact by bijection) | yes | formula | - |
| 3 | \|L\|=4096, \|L*\|=32, W14x=bd1d3f7b, 32 W15x values | \|L\|=4096 (262,144 pass rows 14-15 cells; 4096 also satisfy the four expansion differences ds0/ds1 of W14,W15) ; \|L*\|=32, same W14x, same 32 W15x (5-dim affine set) | yes | enumerate W14x (22 free bits) x E15x (18 free bits), row-16 (dE16,dA16) test | 165 s |
| 4 | 1,052,672 (u,l) pairs ; 1,042,240 distinct u ; 28 l usable ; mean 2^-16.994 | 1,052,672 ; 1,042,240 ; 28 (4 l have R16=0) ; 2^-16.994 ; Pr[u in R16]=2^-12.009 | yes | 32 l x 2^23 E16x, all row-16 cells + two-bit conds | in item 3 run |
| 5 | kept variants 122,253 ; kept fibres 1,221.4 ; four-groups 30,577.1 ; g = 8,129 | 121,602 +- 525 (1 se) ; 1,214.6 ; 30,414 ; g: 8,086 (=p6*kept/1.006), sampled-cb 8,183 +- 57 | yes (-0.53%, 1.2 se; p6*kept/1.006 is 0.5% below 8,129) | 300,000 uniform (x,cb) samples, THETA 40; mean variants in passing classes 191,807 vs exact 192,075 (-0.14%) | 10 min (2 thr) |
| 6 | q3_model 2^-74.03 (study B), q3_used 2^-74.08; stage means 16.994/13/15/6/7/1/11/4 | own SMC, NP 8192, 8 reps: log2 q3 = -73.994 +- 0.015 (se); stages -16.994 -13.000 -15.00 -6 -7 -1 -11.00 -4.00 | yes (ours 0.09 bit above q3_used) | independent particle filter from chi37, rows 16-36 all cells + two-bit conds | 2.5 min |
| 6 | lane safety: max S0(a0)=ffffff58, a0<2^29 ; "min 8" | max ffffff58 ; max a0=1ff4c6ff ; min S0(a0)=000000c0 (not 8) | max yes; min differs but harmless (printed bound only needs >= 0) | scan of G | 40 s |
| 6 | table-build arithmetic: 12,103,680*|F7|=2^49.55 ; 22,976*2^32*80=2^52.8 ; x256 = 2^57.55 | 2^49.551 ; 2^52.810 ; 2^57.551 | yes | arithmetic | - |

Not recounted: C=cost per unit and the Section 9 operation counts (out of the 4-8 scope); the PRE=2^58 bound is a bound, not a count.

## Findings
1. Everything printed in sections 4-8 recounts. No mismatch (only the harmless "min 8" lane number).
2. Unprinted conditions the cells imply (each tested on all cell-consistent words; "ds" = modular difference of the sigma output):
   - Tail rows 25..36 add no condition: in my SMC every row-24 survivor passes rows 25..36. The tail 2^-4 is exactly the 4 W24 conditions; ds1(W24) is fixed by the 3 printed two-bit conds (8 sign patterns -> 1), ds1(W22) by the 4 printed (16 -> 1). Complete.
   - ds0(W9) (feeds W24, needs ds1(W22)+ds0(W9)=40000000): 2^-6 of W9-cell values (2^-5 if any W22 sign pattern is allowed = the "1/32"). NOT enforced by rows 9 cells alone: of 256 E9 patterns passing A9/E9 cells, 12 pass the W9 XOR cell, only 2 have the needed ds0 (2^-2.6 beyond the W9 cell, 2^-7 beyond A9/E9).
   - ds0(W10) (W25, needs 04ff0e66): 2^-9 of W10-cell values, but row-10 cells enforce it fully (8 of 8). 0 bits.
   - ds0/ds1 of W14,W15: 2^-6 over rows 14-15 cell solutions (262,144 -> 4096), then 2^-7 to L* (this is the printed 32).
   - These affect only a search for a new S (Step 1, W9: <= ~2.6-7 bits on the 2^41.3 solve, inside the 2^50 A_S allowance). For the attack with the published S: 0 bits, no ledger change.
3. LEVER found (not in any ledger): the W8 XOR cell and its 3 two-bit conditions are not needed for a collision, only the modular s0(W8+e0000000)-s0(W8)=043ff800 is. G' (that condition alone, E4[31:29]=000) has 18,978,816 variants (+56.8%, 46,557 c7 classes). SMC with W8 drawn from G': log2 q3 = -74.009 +- 0.008 (tail -4.00, same as G), so the tail probability is unchanged. Fibre statistics at THETA 40 (80,000 samples): kept variants 161,111 +- 1,284 (x1.325), g x1.31. With the proof's own ledger split (about 2.6 of 38.2 units per first block are fixed, the rest scales with examined pairs) that is about 0.02-0.03 bit off T (61.178 -> ~61.15); PRE grows x1.5 (negligible). Small, free, needs a rebuilt table and fresh premise H2 for the new subset.
4. Dropping the W14/W15 XOR cells (keep modular dW14, dW15, A/E cells, four expansion diffs) gives the same L (4096) and L* (32): no extra l. W6/W7 XOR cells are already dropped by the proof (F6/F7 are exact modular conditions).
5. Caveat on all of this: my SMC draws W8 uniformly from G (or G'); the proof's examined subset is x-dependent (H2 hedge 0.05 bit). Sampled q3 exceeds q3_used by 0.09 bit, so the hedge is not tight.
