# BATCHPRICE: do the batch-S inversion bounds re-price the per-frame table route?

2026-10-09. Exact arithmetic and reading only, local. Script `batchprice.py` (run `python -B batchprice.py`; output in `batchprice_out.txt`). Every price below uses T <= O/430 + 2^38 and is rounded up at the 4th decimal with the integer test (O + 430*2^38)^10000 <= 430^10000 * 2^k, passing at k and failing at k-1.

## Answer

Neither Astra's mean bound nor the cloud's universal bound can simply be dropped into any of the three rows. The cloud's universal bound is a valid worst-case sweep. Even so, pkg16f performs no inversion over a frame: it reads only K*. AP's per-G inversion work is not split out from its AC filter. In AP's fresh-table row the table serves one G. The S-curve work can move AP's 70.67 by at most 0.14 bit. That ceiling still assumes a free AC filter, so it is not a price. The cheaper component that is valid and proved sits in pkg16f's own text. Computing K_O(g*) directly, with no table, gives **113.4454 -> 110.1260** and needs no new premise.

## 1. What each route charges for K over a frame

| Route | Ledger term(s) | Source |
|---|---|---|
| AP conditional, 70.67 | **303 per G** on Bf = J*2^32 = 819,214,401,994,932,355,072 G values. The 303 is made of **80**, **117** and **106**. The 80 is the generator: AM's direct-bucket *target* table, built by the record scan at 80*2^32 per O (AM's cap was 72*2^32; bucket lengths add 8*2^32) and charged as 80 per G. The 117 is AM's per-G scalar scan, which runs on every G and computes K_O(G) and the AC filter; AP does not split it. The 106 is test2, charged at its worst case on every G. Other terms are 4096 per O and 144164 per AC pass (Lf+1 passes). | AP lines 26, 32-38, 59-62 |
| AP fresh-table, 99.04 | The same 80*2^32 target table, rebuilt for **every single proposal**, with one G per table. The row's formula is not in lines 46-81. | AP line 77 |
| pkg16f, 113.4454 | Row "the table of a frame: one value of D2.a1 (9.5)", at **512 per g x 2^32 per frame** = 2^41 per frame and 89.98 % of O_tot. The table is built in full **but only K* = K_O(g*) is read from it** (proof.md 1633-1636, 2587-2590). The actual matching is the step-3 record scan, 64 per record x 53*2^26 records per frame (9.31 %). | proof.md 1613-1621, 1953-1969, 2532-2545 |

The brief describes this route as "one K table per frame serving the 2^21 cube targets". **Neither text matches that description.** In pkg16f the K table serves the single value g*. In AP the per-O table indexes the records (at most Nrec = 53*2^26 targets) by H_O, and all 2^32 values of G are scanned against it. In pkg16f, 2^21 is the size of the cube Q*, which bounds the roots per frame. It is not a number of K-table queries.

## 2. Units and cost models

| Source | What costs one | Conversion | Bound type |
|---|---|---|---|
| Ours: pkg16f §11, lines 2515-2521; AP line 63 | Every primitive word operation, every load and every store is one machine unit. A word holds one scalar 32-bit value or one 256-bit record. | 430 machine units = 1 unit (one 2-round compression). T <= O/430 + 2^38. | Worst case, deterministic |
| Astra (Result, §1, §4 line 99) | add, sub, XOR, AND, rotate, comparison, memory read and memory write cost 1 each. **Assignments, branches and allocation are free.** Operands are 32-bit. | §1 divides by 430, so 1 op = 1 machine unit. | **Mean** over uniform q and a uniform set of distinct targets that is independent of the constants. |
| Cloud (lines 11-15; §6-7, 180-269) | Under the brief's "abstract word model": arithmetic, reads, writes, loop increments, comparisons and outputs. The file does not say how branches or moves are charged. | **No /430 conversion appears in the file.** Setting 1 op = 1 machine unit is our assumption. | **Universal**: holds for every constant set and every target batch. |

The cloud's bound comes from its own ledger: C = 20*2^32 + 29I + E + 4m + 5R + 27, with 29I + E <= 10,793,677,616 (prefix certificate) and R <= 2^32. That gives **C <= 118,167,860,043 + 4m**. At m = 2^20 this is the quoted 118,172,054,347. At m = 2^21 it is 118,176,248,651, which is 27.515 per g and 2^36.782. Astra's mean at m = 2^21 is 84,664,467,756.44, which is 19.712 per g. For comparison, pkg16f charges 512 per g.

Mismatches:

1. **Branches and moves.** Astra charges nothing for branches or moves, and the cloud does not say. Our model charges every primitive op, so the batch counts undercount by at least the marker-test and loop branches, about 2 per g.
2. **Mean versus worst case.** Astra's figure is a mean, and the targets it assumes are uniform and independent of q. Our targets, H_O of the frame's own records, are functions of the same frame. Astra itself says I(q) must not be replaced by its mean in a worst-case claim (line 148).
3. **Inputs.** Both batch solvers take the targets as a given list at 4 ops per target. They do not generate the targets with a record scan, and they give no bucket lengths. AP's candidate route, which branches on m <= 35 versus m >= 36, needs those lengths.

## 3. Prices (exact)

| Row | Change | O (numerator) | time_log2 |
|---|---|---:|---:|
| AP conditional, as Sol priced it | none (checked) | 805,538,240,453,692,110,434,000 | 70.6662 (Sol: 70.67) |
| AP conditional, **ceiling only** | All of the 117 per G replaced by the cloud's universal sweep at m = 2^21. The AC filter is treated as free, which is invalid. | 732,230,882,321,464,529,572,633 | 70.5285 |
| AP conditional, **ceiling only** | Same as above, using Astra's mean sweep | 725,838,905,001,662,604,393,793 | 70.5159 |
| AP fresh-table | not recomputable from lines 46-81. A batch inverter has nothing to amortize, because each table serves one G. | n/a | 99.04 |
| pkg16f filed (proved rho <= 3,071) | none (checked) | 6,080,111,232,731,503,201,962,608,254,739,666,816 | 113.4454 |
| **pkg16f, K*-only** | Step 2 computes K_O(g*) alone, charged the full 512 per-g allowance of 9.5 once per frame instead of 512*2^32. Per frame: 4096 + 512 + 64*53*2^26 + 8192*2^21 = 244,813,140,480. | **609,079,694,566,501,146,181,744,462,938,870,656** | **110.1260** |
| pkg16f with the cloud sweep in place of the table | for reference only; it is not needed, and it would also need the cost models to match | 903,094,766,552,959,756,320,429,028,356,103,562 | 110.6942 |

The AP rows are dominated by S64 (51.87 %) and the passes (17.32 %). The 117 per G is 11.90 % of O, which is why the ceiling is only about 0.14 bit. The K*-only cut is a factor of 2,443,836,395,520 / 244,813,140,480 on the frames, which is -3.3194 bit for any frame count. After the cut, the records take 92.98 % of the time and the roots take 7.02 %.

## 4. Premises each new price still needs

- **pkg16f K*-only, 110.1260.** It needs the same premises as the filed 113.4454 and nothing new. The charge is a deterministic worst case. On the success side it uses H1' (10.3) together with the proved Lemma S7/S8 (b(3,071) = 1/3,072). The run's output, the trials it covers and the success probability are all unchanged, because the table was only ever used for K*. The text must change in step 2 (9.1), in rows 9.5 and §11, and in §12: memory falls by the 2^32-record table, though memory is free in any case.
- **AP conditional ceilings, 70.5285 and 70.5159.** These are not prices. They still need the two OPEN frame premises (FRAME factorial, FRAME pass-budget). They also need a proved split of AM's 117 into K_O(G) work and AC-filter work, plus a branch and move charge for the sweep. The Astra version additionally needs expected time to be accepted, and targets that are uniform, distinct and independent of q. That last condition is false here.
- **AP fresh-table, 99.04.** Unchanged. It keeps the ordinary H1/H4.

## 5. Lead (unverified, outside this brief)

In pkg16f step 3, for a fixed frame and c, the equation H = K* has exactly one solution, given in closed form by b = ROR12((u - K*) XOR c), a = b + u + w5, z = ROR8(a XOR d). AP's line 15 already states that H_O(c,.) is a permutation. Step 3 could therefore visit the 2^21 values of c in Q* and look up (c, z) in an index of the E1 record table built once, instead of scanning 53*2^26 records per frame. With an assumed 512 per c, plus a one-time charge of 2^46 for the index, the result is 106.3805, with O = 45,413,847,485,645,553,179,883,844,166,587,264. The 8192*2^21 worst-case root allowance would then dominate. This needs a design for the index, a derived per-c charge, and a check.

## 6. Independent recheck (2026-10-09, `recheck_bp.py` -> `recheck_bp_out.txt`)
- AGREE, all 8 prices: each reproduces exactly from the cited lines, and each integer test passes at k and fails at k-1. AP 70.6662; ceilings 70.5285 (cloud) and 70.5159 (Astra, same under either rounding order); fresh-table 99.04 (AP 46-81 give no formula, and each table serves one G); pkg16f 113.4454 (every §11 row product matches); K*-only 110.1260; cloud-in-place 110.6942; lead 106.3805.
- AGREE that K*-only is valid under the same model. In 9.5 (1955-1958), the 29 g-lines plus one add cost 12 each, so 360 <= 512, and the price is still 110.1260 at 360. Step 3 compares with K* "in place of a query" and follows no list (1620, 1967). Premises: H1' plus S7/S8, unchanged. Line 1636 says "not claimed", so the text of 9.1 step 2, 9.5, §11 and §12 must change.
- DISAGREE, wording only: "at most 0.14 bit" holds for the cloud (0.1377), but Astra's limit moves AP by 0.1503, and dropping the 117 at zero cost gives 70.4834 (0.18). Also, m = 2^21 is the brief's count. AP's targets are record keys, up to Nrec = 53*2^26, which gives cloud 70.5338 and Astra 70.5253. AM line 104 splits 117 into loop 4 + w8 cone 90 + test(2) 23; keeping the 23 gives cloud 70.5652.
- AGREE on units. The cloud bound recomputes: I <= 15286*18098, J <= 6657 + 15286*7881, 29I+E <= 10,793,677,616, C <= 118,167,860,043 + 4m. The cloud file never mentions 430 or a charge for branches. Astra line 99 makes branches free, and line 14 states a mean. The lead's closed form is an exact identity (z -> H is a bijection for each c; 20,000 random checks agree), but the 512 per c and the index are unproved.
