# e20_e19_drop: do E20[2]!=E20[16] and the E19 value mask 01848010 cost anything? (2026-10-12)

Tool: research/tools/traillab (chi/chi37.txt). A copy lives in this folder (src/, built ./traillab) with two diagnostics added and nothing else changed:
per-class tallies (class = violates a / violates b) at every E-driven prefix stage (`PSTAGE`) and on the final samples (`CLASS`, `CDEATH`).
Scripts: run.sh, analyze.py. Raw output: out/{n,a,b,c}.txt. WSL, --threads 2, no call over 5 min.

Method: `window --rows 22 36 --event out --prefix-relax R`. SMC with resampling at every row 16..21 (np 4096, m 256, mt 1024 = 4.19M final
samples per seed), exact weights, 8 seeds (1..8, same seeds for all four conditions). EXACT = equal outputs after step 36 with the
schedule recomputed. Conditions: n = neither dropped, a = `dropx2 E20` (E20[2]!=E20[16] dropped), b = `dropv E19 01848010`, c = both.
Full event = 2^(log2 P(rows 4..21)) x EXACT rate.

## Table (8 seeds each)

| cond | log2 P(rows 4..21) (mean, seed sd) | EXACT rate log2 | full event log2 | ratio to n (paired, 95%) | log2 ratio |
|---|---|---|---|---|---|
| n neither | -59.011 (0.021) | -13.669 | -72.679 | 1 | 0 |
| a drop E20[2]!=E20[16] | -59.010 (0.030) | -13.734 | -72.744 | 0.957 +- 0.055 | -0.065 |
| b drop E19 mask | -58.919 (0.100) | -13.690 | -72.606 | 1.053 +- 0.066 | +0.073 |
| c drop both | -58.920 (0.101) | -13.704 | -72.621 | 1.042 +- 0.066 | +0.058 |

All four intervals contain 1. q(rows 16..21) = log2 P(rows 4..21), because P(rows 4..15) = 1 (SMC init acceptance 1.000000).
The staged gain at rows 19-20 (about +5 bits for b, +1 for a) is cancelled one or two rows later.

## Violators (classes in the c run, whole-process totals over 8 seeds)

| violates | reaches | proposals | survive | where it dies | 95% bound on survival |
|---|---|---|---|---|---|
| a only | row 21 | 4,193,024 | 0 | row 21, A21 and E21 cells fail together | < 7.2e-7 |
| b alone | row 20 | 4,055,052 | 0 | row 20, A20 and E20 cells fail together | < 7.4e-7 |
| a and b | row 20 | 4,054,004 | 0 | row 20, A20 and E20 | < 7.4e-7 |

Fraction of violators that reach the late event (equal outputs): 0. They never leave the prefix, so nothing reaches rows 22..36.
The single-drop runs give the same zeros (a: 4,191,232 reach row 21, 0 survive; b: 4,055,052 reach row 20, 0 survive).
Extra test with rows 20 and 21 removed from the prefix as well (droprow A,E,W 20 and 21; 1 seed, np 2048): 0 EXACT in 2.1M violator samples,
but also 0 in 37,888 class-0 samples, so that run cannot say whether a violator could collide by some other route. Not measured.

## The 2^-1.43 bias of E20[2]!=E20[16]: NOT reproduced; what it is

- In the model where E20 is a free coordinate (traillab edrive 16 21) the condition holds on half of E20: row-20 class counts in run a are
  4,194,957 (holds) vs 4,193,651 (violated), P = 0.50004 +- 0.0003. E20's non-cell bits are uniform and rows <= 19 do not depend on E20,
  so P = 1/2 by construction. 2^-1.43 = 0.371 therefore comes from Grok's sampler (its E20 is a function of sampled words and its conditioning),
  not from this model. We cannot say which part of its sampler.
- What holds exactly: the condition is implied by the next row. Of the E20 values that pass rows <= 20, every violator dies at row 21
  (0 of 4,193,024), so P(condition | rows <= 21) = 1. It is not an independent cost on top of row 21; dropping it removes nothing.
- Mechanism (checked numerically on 10^5 random words): E20 has cell u at bit 29 (x bit 1, y bit 0). Sigma1 = ROTR6^ROTR11^ROTR25 puts that
  difference on output bits 23, 18, 4. Output bit 23 of Sigma1(E20) is E20[29]^E20[2]^E20[16] = 1^E20[2]^E20[16]. If E20[2]!=E20[16] the x bit is 0 and the
  term is +2^23; if equal it is 1 and the term is -2^23. The 2^24 swing enters E21 and A21 through S1(E20) and W21's difference is fixed by the schedule,
  so A21 and E21 fail. Nothing in IF (CH) or in other carries is involved at row 21 for this condition.
- Why bits 2 and 16 might look equal-biased in a sampler that does not impose row 21: nothing in rows <= 20 explains it; no cause claimed.

## E19 mask 01848010 (Grok 2^-5.02): confirmed as 2^-5

Five value bits of E19 (24, 23, 15 = 0; 18, 4 = 1). Bit 29 is a sixth and is already relaxed in R1. In run b the share of E19 proposals that satisfy the mask is
8,220 of 262,144 on the first tally = 2^-4.99. Mechanism: these are the IF gates of step 20, CH(E19,E18,E17) = E19 ? E18 : E17.
E18 carries differences at bits 24, 23 (u) and 15 (n): they reach CH only where E19 = 1, hence E19[24] = E19[23] = E19[15] = 0.
E17 carries differences at bits 18 and 4 (u): they reach CH only where E19 = 0, hence E19[18] = E19[4] = 1.
Violating any bit makes dCH nonzero, dE20 leaves the printed pattern, and row 20 fails (A20 and E20 cells) every time (0 of 4.06M).

## Verdicts

| condition | verdict |
|---|---|
| (a) drop E20[2]!=E20[16] | NECESSARY at row 21 (sign of the Sigma1 bit-23 term). Ratio 0.96 +- 0.05, gain -0.07 +- 0.08 bit. Not a lever. |
| (b) drop E19 mask 01848010 | NECESSARY at row 20 (IF gates of CH). Ratio 1.05 +- 0.07, gain +0.07 +- 0.09 bit. Not a lever. |
| (c) drop both | NECESSARY. Ratio 1.04 +- 0.07. Not a lever. |

Limits: all statements hold for this characteristic with its printed XOR/difference pattern kept (`dropv` and `dropx2` keep the differences). A different
signing of rows 19..21 that tolerates the other values is a different path and was not tested (OPEN). Off-characteristic routes below about 2^-20 per
proposal are untested. The SMC prefix estimate has seed sd 0.02 to 0.10 bit.
