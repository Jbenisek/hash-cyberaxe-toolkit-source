# crossline-XF2 (Grok 52, job52_xf2_repgate): refutation attempt — RESULT

2026-10-09, about 20:10-20:30 MDT. One CPU process (numpy), every run under 12 minutes. No yukon, no submission,
nothing outside this folder written. Labels: COMPUTED = run here on the scored pkgCJ lines (frontline_full.py from
the Grok 52 folder, imported read-only); DERIVED = algebra; GUESS = estimate.

**Verdict on the refutation: NOT REFUTED.** The key number reproduces to 1e-6 and the one premise the claim called
unproved (opening rate 52/128) turns out to be exact per context, by a short lemma checked on every block sampled.

## 1. Key number, recomputed term by term (COMPUTED, reprice.py -> reprice_out.txt)

Own rebuild of N: N - U_OPEN (A_BUDGET+1) + U_OPEN (ceil(share * 16384 K) + 16384 s + 1) + guard_units * 16384 K.

| case | log2(N/430) | delta |
|---|---:|---:|
| today (pkgCJ) | 63.602640 | 0 |
| brief formula, p_g = 9/65536, 2 guard units (Grok's figure 63.51601560817674) | 63.516016 | -0.0866 |
| measured 0.40729, 2 guard units (the claim's alternative 63.518) | 63.517948 | -0.0847 |
| PROOF-GRADE share 52/128 + (38/64)(9/65536), 2 guard units, +20 units per context for the Hbad table | 63.516161 | -0.0865 |
| same, 3 guard units | 63.521240 | -0.0814 |
| break-even opening rate at 63.55 (2 guard units) | 0.42462 | |
| guard units per cluster that reach 63.55 at 52/128 | 9 | |

Both of the claim's figures reproduce. Op-count disputes cannot flip it: it takes 9 units per cluster of guard, or an
opening rate of 0.4246, to reach the 63.55 bar.

## 2. The opening rate is exact per context (DERIVED, then COMPUTED on every block)

Split the 16384 clusters of a context into 256 blocks of 64: g bits 6..13 fixed, g bits 0..5 free. g bits 0..5 are
e1 bits 2..7 (cmember: k bits 0..5 -> CLASS_FREE[0..5] = e1 bits 2..7); e1 bits 0,1 are the class value 1,1.

Lemma (DERIVED). In a block where Grok's straddle guard is off, the 64 representatives' omega mod 128 are the 64
residues of one parity class, so exactly 26 of them are in S7. Hence a context opens exactly
26 * (blocks with the guard off) + (old-gate opens in guard-on blocks) <= 6656 + 38 * (guard-on blocks).

Proof sketch.
- Low byte: y = e1 - Y3, Y3 low byte 0x81, e1[0..7] = 3 + 4u + 128v (u = g bits 0..4, v = g bit 5), so
  y[1..7] = z = 1 + 2u + 64(1 - v): the 64 odd values of Z/128, and 4u = 2z - 2 (mod 128).
- Everything else in omega mod 128 is fixed in the block: y8[0..7] = y[25..31], y[0] (g bits 8..13 only), so the
  borrow br8 into y12 bit 8 is fixed; with the guard off, the borrow br16 into x0 bit 16 is fixed for both h
  candidates (Grok's straddle condition; mid, H, d0 and A do not depend on g bits 0..5); L, SS, b, c, d, A are context words.
- omega mod 128 = e1[0..6] + P(z), P(z) = ((((z ^ b) - c - br8) ^ d) - A - br16) ^ L) - SS on 7-bit slices: a composition
  of xor/subtract by constants, i.e. an invertible T-function. So omega = 1 + 2z + P(z) =: Q(z) (mod 128). Q is again an
  invertible T-function (bit i = z_i xor a function of lower bits), its bit 0 is constant over odd z, so it maps the 64 odd
  z onto all 64 residues of one parity.
- S7 = [0x25, 0x3e] u [0x45, 0x5e] holds 13 odd and 13 even residues in each interval: 26 per parity class. So 26 of 64.

Checks.
- tlemma.py -> tlemma_out.txt (COMPUTED): the 7-bit algebra above for 200,002 random constant sets (b, c, d, A, L, SS,
  br8, br16): bad = 0.
- rate_np.py -> rate_np_out.txt (COMPUTED, real context lines): every guard-off block of every context sampled has
  exactly 26 opens and a full parity class; the guard is constant on every block; no context exceeds 6656 + fires.

Consequence. The claim's open premise ("omega mod 128 uniform, measured, not proved") holds exactly at the level the
run uses it (all 16384 clusters of every context are walked, REP_BATCHES = 2341). A proof-grade budget share is
52/128 + (38/64) p_g with Grok's proved p_g <= 9/65536, i.e. 0.40633154, and the price in section 1 uses it.
The measured rates 0.40908, 0.40676 and 0.40729 came from partial schedules (random g, or walk()'s g = 0..27 and
16380..16383, which cut blocks); they estimate the run rate only up to sampling noise and need not equal it.

## 3. Guard exactness and rates (COMPUTED, rate_np.py -> rate_np_out.txt)

Command: `python -B -W ignore rate_np.py 262144 1024 52052` (981.6 s, one process). Own numpy evaluator of the 39
context lines and the omega side; checked against the scored co_ctx and co_ref first (mismatches 0). Outer words
uniform random (numpy seed 52052). All 16384 clusters of each of 262,144 contexts.

| quantity | value |
|---|---:|
| clusters | 4,294,967,296 |
| new gate open rate (guard on -> old gate, off -> rep omega mod 128 in S7) | 0.40625275 = 52/128 + 2.75e-6 |
| extra opens from guard-on clusters | 11,826 (0.041 per fire) |
| old two-borrow gate rate | 0.44821 (uniform-key figure 0.44823) |
| guard fires (straddle, H from the rep's own y8) | 290,368, rate 6.76e-5 (ceiling 9/65536 = 1.37e-4) |
| Grok's 4-entry Hbad table vs reference H | 0 mismatches |
| guard not constant on a 64-block | 0 |
| guard-off blocks / with opens != 26 / not a full parity class | 67,104,327 / 0 / 0 |
| contexts with opens > 6656 + fires | 0 |
| clusters with Y0[8..15] == A[8..15], all 32 members evaluated | 16,752,384 |
| real 9-bit prefix splits among them / outside the guard | 107,814 / **0** |
| false closes (a member's omega mod 128 in S7, gate closed) | **0** |
| 1,024 whole contexts, every member: splits / outside guard / false closes | 320 / 0 / 0 |

A cluster with Y0[8..15] != A[8..15] cannot split (the borrow into x0 bit 16 is decided by that byte), so the
byte-equal set is the whole risk set; every split in it was inside the guard.

## 4. Score-rule check

- Preprocessing: none beyond a 4-entry table per context; charged at 20 units per context in the proof-grade row
  (GUESS of its op count; it moves the total by under 1e-5 bit).
- Success >= 0.39: no T2 hit can be dropped (shared omega mod 512 outside the guard: DERIVED by Grok, re-derived here,
  0 false closes COMPUTED). The A_BUDGET halt: the lemma of section 2 makes the per-context open count deterministic up to
  guard-on blocks, so a mean term at 52/128 + (38/64)(9/65536) is a proved upper bound and the existing 16384 s tail still
  covers the fluctuation. The brief's formula (52/128)(1 - p_g) + 0.459 p_g allows only 0.0528 p_g of extra opens where the
  proved bound is (38/64) p_g. It is enough in measurement (actual extras 2.75e-6 against its 3.6e-6 at the measured p_g),
  but it is not a proof. Filing should use the proof-grade row 63.516161 (-0.0865), which costs 0.00015 bit.
- Ops as executed: 2 units per cluster for the guard (byte compare and branch per lane; a packed 7-lane zero-byte test is
  cheaper) is plausible. U_REP is left unchanged, which is conservative, because the S7 bit test on the packed omega
  replaces the gate-table test. The old-gate key is needed only on guard fires. Even 9 units per cluster stays under 63.55.

## 5. What this does not establish, and notes for the main thread

- Grok's ceiling p_g <= 9/65536 (w2 low-16 histogram <= 2x flat, E[gap] = 9/2) was not re-proved here. The measured
  6.76e-5 is under it, and the price barely depends on it: p_g = 0.01 would still pass.
- The new gate was not run inside the scored walk() here (Grok's validate.py did: 100,000 clusters, walk_mismatches 0).
- Overlap with EBG: the same lemma proves the exact-borrow gate's opening rate (Astra 18's task). EBG opens on some
  prefix of W in S7, and W is the representative's single prefix outside straddle blocks, so EBG's share is also
  <= 52/128 + (38/64)(9/65536) = 0.40633. The measured 0.40731 is a partial-schedule sample and is not the run rate.
  If EBG is already in the front line, XF2 adds about 0 on top of it; the -0.0866 is relative to pkgCJ only.
- Process note: the large run went past my 12-minute estimate because the machine was shared. My call to stop my own
  PID 30180 was refused by the auto-mode classifier ("Interfere With Workloads"). I did not work around it. The run
  ended by itself at 981.6 s, under the 20-minute limit.

## Files

reprice.py / reprice_out.txt, rate_np.py / rate_np_out.txt, tlemma.py / tlemma_out.txt (this folder).
