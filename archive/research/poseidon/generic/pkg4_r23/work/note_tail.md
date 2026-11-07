## The claim
Target poseidon-orchard-r23-prefix-v1: the Orchard Poseidon hash with 8 full and 23 partial rounds, initial state [m0, m1, 2^65], digest = state[0], the whole canonical field element compared. Claim: time_log2 = 127.020 target-compressions, memory 2^20 bytes (actual total 1,020,704 bytes), success probability 0.39, preprocessing 0, nonuniform advice 0. Cost model orchard-field-ram-v2, C = 216 + 21 * 23 = 699. The nominal reference is 127.0; this entry is the generic row for r = 23 and uses no algebraic structure.

## Approach
1. Walk. Draw rho0 and x_0 (low 254 bits of two random words, both canonical) and iterate F(x) = digest(x, rho0). Two inputs (x, rho0) and (y, rho0) with x != y and F(x) = F(y) are a collision.
2. One trail. A value whose low 128 bits are below 27554 is a distinguished point (exact density (2^126 + 1) * 27554 / p = 2^-113.25). Each one is stored with its index in a 64-byte entry, at most 15,500 of them. A stored value that comes round again means the trail has closed on its cycle.
3. Recovery. From the stored point before the repeat, walk to the matching point one cycle length ahead, then walk both in lockstep until their images agree: the two points are the collision (proof.md Section 3, deterministic).

## Success lemma
For a uniformly random function on N = p points, conditioned on any start: a fresh step repeats one of the i + 1 earlier values with probability (i + 1)/N; given the repeat pattern, the distinct values are a uniform sample without replacement, so each fresh value is distinguished with conditional probability between theta_lo = (D - 2^128)/N and theta_hi = D/(N - 2^128), whatever came before (Lemma 1). Lemma 2 then bounds every failure: no repeat in n steps (exp(-n(n + 1)/2N)), start on the cycle (n/N), no distinguished point in the first d = ceil(8/theta_lo) cycle values (e^-8 + n d/N), a gap above gmax = ceil(18/theta_lo) ((S theta_hi + 1) e^-18), table overflow (Chernoff on Binomial(S, theta_hi), e^-109.4). With n = 133698538 * 2^100 the bound is 0.390000002301729877 >= 0.39 (80-digit decimal arithmetic in `plan`).

## Ledger
S = n + d = 1.6958e38 trail steps at 1 + 9/699 units (the instruction listing in proof.md Section 5: 2 state assignments, counter, move, AND, compare, branch, loop compare, branch); 3 gmax = 6.67e35 recovery evaluations at most, charged 1 + 10/699 each (the listed loops use 5 and 7.5); table scan 6 operations per entry, insertion 3, bisection 12 per probe, setup 2000: 1,441,827,698 operations in all. Total 1.7244182e38 units, log2 127.019377, claimed 127.020. Memory: (15,500 + 2) * 64 = 992,128 bytes of table + 21,600 code + 6,464 constants + 512 registers = 1,020,704 bytes.

## The premise and its evidence
H1 (score-critical; an assumption, no proof is known): the real map with a random rho0 succeeds at least as often as Lemma 2's random function. Evidence, measured with our own code on the real map at r = 23 (proof.md Section 7, program in Appendix C, data in Appendix D). Outputs were truncated to w = 16, 20, ..., 40 bits, with a fresh rho and start per walk, and every walk ran to its exact first repeat. Two independent runs per width gave {{KALL}} walks. The collision-rate multiplier is {{CPOOL}} (95% interval [{{CLO}}, {{CHI}}]; a random function has 1), with slope {{SLOPE}} per bit across widths (standard error {{SLOPE_SE}}). The full search succeeded in {{SUCC_ALL}} runs against a mean lemma bound of {{SUCC_LB}}. Distinguished-point gaps followed the geometric law. A keyed pseudo-random control run through the same program gave the same picture. The organizer digest confirmed all {{PAIRS_OK}} pairs the runs returned. The full width cannot be measured. A collision rate 1, 5 or 10% below random would cost 0.0072, 0.0370 or 0.076 bit, and the lower end of the measured interval costs {{DT_LO}} bit.

## Files and commands
The package holds claim.json, proof.md and an empty certificate manifest. proof.md Appendix B is the program (`rho.py`, standard library only): `python3 rho.py --plan` prints every parameter, the bound and the total; `python3 rho.py --selftest` runs the search at width 14 and checks its counted operations against the ledger formula. Appendix C is the measurement program, and Appendix D holds the per-run results.

## Experiments
None are declared: the organizer runner calls the digest on the empty message (`digest_fn(b"")`), which the Orchard digest rejects, so a declared Poseidon experiment fails before it runs.

## Changes from the earlier version of this row (one line each)
- Success transfer had no evidence: measurements of the real map at r = 23 on truncated outputs, two runs each (proof.md Section 7).
- DP conditioning ((1 - theta)^g after a stored point): Lemma 1 bounds every conditional DP probability between theta_lo and theta_hi given any history and any start; d and gmax use theta_lo, table and gap terms use theta_hi.
- 48-byte packed entries on a 256-bit word machine: entries are two aligned 256-bit words (64 bytes); the table cap is 15,500, and memory is 1,020,704 bytes.
- Tight 9-operation step: the instruction listings of the trail step, the recovery loops, the scan, the insertion and the probe are in proof.md Section 5.
- Fixed walk map: the attempt draws rho0, so its probability averages over maps (a single fixed map's success over starts varies with its longest cycle, measured in Section 7).
