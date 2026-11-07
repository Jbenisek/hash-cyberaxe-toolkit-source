# exec_r2 progress (Poseidon r=2, PARETO)

Dates in this file come from the machine clock, 2026-10-13. No compute is running. No GPU used. No yukon commands run. Nothing staged or submitted.

## State: owner decision 10-13: odd-part executed variant, centres c_i = i (i = 1, 2, 3, ...) in order, every executed centre charged, p = 1, no heuristics (same form as r1 filing 8e9fc034). Code ready; full-size run waits for the owner's go.
Owner pause received: no runs over ~1 minute, 1 process, nice 19, no GPU. Only one tiny profile build was run (seconds).

## What exists
- `src/` : copy of `lean_r2` sources (tested Pallas field, NTT with 4-layer register blocks and Good-Thomas radix 3, lean powering `lean.c`, stored-spectrum powering `loop.c`, half-gcd `hgcd.c`, line/`build_g` `line.c`, driver `lean_attack.c`). Nothing edited yet except two new files, `prof3.c` and `b_prof3.sh`.
- `rivals_text/pr37.patch`, `pr37_proof.txt` : tanctl PR 37 proof read as TEXT only (fetched with curl; never run). The ledger rules below come from it (sections 4.1-4.6, 5.2) and from note_186052af.md.

## Rival ledger rules (the accepted level) that we adopt
- Unit = one field add/sub/mul, one 256-bit load/store, comparison, branch, shift. C(2)=258.
- Radix-2 butterfly: 4.5 = 2 mul (running-product twiddle) + add + sub + 1/2 loop/address. Radix-3 butterfly 8.5. Memory: 2/3 load+store per element per radix-2 level (3-level register passes). T(N) = N(35k/12+29/6) for N=3*2^k; T(393216)=21,397,504, T(786432)=45,088,768.
- Every other per-element loop (pointwise, pad, copy, fold, shift, remainder) is unrolled 8x: 1/2 unit per element. Pointwise square 4.5, pointwise product with cached transform 5.5, zero pad 3/2, copy 5/2.
- Classical product 4*m1*m2 + m1*m2/2 + 2(m1+m2-1); classical division L(4(m+1)+2)+L(m+1)/2+...
- Charge only the EXECUTED run (one fixed start, p=1, deg g=1 found); failed trials are charged.
- Rival squaring (cached q transform): 241,785,063 (uncached 264,163,016). Half-gcd executed 6,563,144,944 at deg 390,624. PR 37 total 64,990,446,343.5, peak 2,359,296 words.

## Measurement of OUR current engine (lean_r2 charges, N=393216, m=195312)
conv_sq: arith 21.16M, ld 7.26M, st 4.32M, ctl 27.32M (total 60.06M). Forward transform alone: arith 10.09M, ctl 13.22M, total 29.4M versus rival T(N)=21.4M. Conclusion: our ARITHMETIC is already lower than rival (3 arith per butterfly with table twiddles, fused pointwise, scaling carried in state); the excess is control (about 4 ctl per butterfly: block loops, strided addresses, twiddle pointers, Good-Thomas mask/rot logic) and loopc = 8 per element. Re-charging to the rival rules should put one transform near 19M (about 10% under rival).

## Key finding for the plan (needs owner/main-session decision)
Two modes share one engine (powering X^E mod g, then gcd):
- Mode A (what the brief names): full degree 5^8 line, q=(f-y)/(X-s0), E=p, modulus degree 390,624. Expected about the rival level (~34.0-34.1) with our engine; matches PR 37 at best. Not clearly below 34.1.
- Mode B (odd part about a fixed centre, our lean_r2 identity): g(S) of degree 195,312, E=(p-1)/2, gcd(g, S^h-1) gives square roots S, collision W=c+-sqrt(S). Same line, half degree, half transform lengths (2m-1=390,623 fits N=393,216; m fits 196,608). The old entries were rejected because they claimed p=0.4 with heuristics (random centres). The rival-accepted device is "deterministic executed outcome": fixed centre sequence c_n = n+1 (the board's start convention), run in order, charge every executed centre, claim p=1, no heuristics. Precedent: 1096f6b9 charged failed trials 0,1 and was judge-valid.
  Estimate with rival-level loop rules: powering ~236 x 100M = 23.6G, gcd ~3-5G, build g ~0.1G, per centre ~28-30G ops = 2^26.8 units; memory about 1.2-1.3M words (about 42 MB incl. 1 MiB) = 2^25.35 bytes. Score about 32.1 for 1 centre, 33.1 for 2, 33.7 for 3, 34.1 for 4. Each centre succeeds with probability about 0.39 (root exists and is a square). All below 34.1 up to 3 centres. These are ESTIMATES (INFERRED), not measured under the new rules.
  Risks: the judge has not ruled on an executed-outcome odd-part claim; the centre convention must be fixed BEFORE running (no cherry picking among conventions; state in the note that no other centre was run).

## Plan / steps
1. Engine and field at degree 390625 (and 195312): re-charge copy of lean_r2 per the rules above.
   - common.h: add half-unit counter `hc`; `loopc(n)` = n half units; snap_total in half units; HC macro.
   - gen_kern.py/ntt_kern.h: butterfly macros add 1 half unit each; drop per-twiddle and per-block CTL (keep explicit twiddle LD); `ntt.c`: strided load/store CTL removed, Good-Thomas stage rewritten as 3-phase unrolled loops charged ~2 per triple (loop 3 + switch 3 per 3 triples), constant per-call CTLs kept.
   - Verify: test_ntt.c (evaluation + roundtrip), new test comparing counted totals against hand closed forms.
2. Counted powering step: new `powx_cached` (stored spectra CM at N, CG at N'; Y(N), fold buffer(N'); memory 2N+2N'), windowed X^d multiplies (d<=15, needs only top 14 coefficients of g plus a short forward/inverse transform at N'), restore g from CG before gcd. Report ops per squaring vs 264,163,016 (and vs 241,785,063 cached) at m=390,624; same at m=195,312.
3. Half-gcd executed: reuse `hgcd.c` with the rival cost rules (classical product/division as dot-product form, 4.5 per pair; recharge loops). Then reduce transform count: shared-transform 2x2 matrix products (12 transforms instead of our 20) and wrapped matrix-vector steps (8 instead of 10). Target about 6.56G at deg 390,624 / about 3.3G at 195,312.
4. Full run + collision: mode B centres c_n=n+1 in order (and mode A start s0=1 as the comparison/fallback), verify with `verify_collision.py` against the reference hash. Periodic invariant check against the transient hardware fault seen on long r=2 gcd runs: re-check a known value (x^2 test vector and a repeated small NTT round trip) every ~10 squarings and at the end of the gcd; record any fault.
5. Package like single_r1_fb: proof.md with full source, claim.json, note >= 5 KiB, certificates; run prefile_check until ALL PASS. Do not stage or submit.

## Remaining to run at full size (after the pause is lifted)
- Step 2 per-squaring measurement at m=390,624 (a few minutes, one process).
- Step 3 half-gcd executed at 390,624 and 195,312 (about 10-20 min each).
- Step 4 full runs: mode B about 20-40 min per centre; mode A about 1-1.5 h. Cross-check the collision with `research\poseidon\certb_fast` only after the main session OKs GPU use.

## Measured so far
- Ops per squaring: not yet measured under the new rules (current lean_r2 figure 229,902,037 at m=195,312 is under the old heavy control charges).
- Executed N, peak, score: none yet.
- Gap to 34.1: undetermined; estimates above.


## Update after the decision (code edits and seconds-long tests only)
Done in exec_r2\src:
- Ledger re-charge (rule quoted from tanctl PR 37 proof, 4.1/5.2): loop and address work is 1/2 unit per butterfly and per element of every unrolled loop. Implemented as a half-unit counter (HC); old per-block CTL charges removed from ntt.c and the kernels; only per-call constants stay. Fold test charge in lean.c removed. All other charges (loads, stores, arithmetic, bounded-division, hgcd control constants) unchanged, so we still charge every load/store.
- Measured at N=393216 (m=195312): forward transform 18.04M (was 29.40M; rival T(N)=21.40M), inverse 18.83M (was 31.50M), conv_sq 36.68M (was 60.06M). test_ntt: PASSED (evaluation, roundtrip, convolution).
- Centres c_i = i (field element i, charged 1 unit), line j=0 fixed, root-splitting shifts a = 1, 2, 3 (deterministic, no random words), budget halts disarmed (an executed outcome has no halt), runs until the first verified collision.
- Uncounted fault probe every 32 squarings (known product, small NTT round trip; counters and peak restored). FAULTS count printed in the log.
- run_full.sh: one command (builds, runs under ulimit -s 64 at nice 10, tees logsull_r2.txt, then verify_collision.py with R=2). verify_collision.py and poseidon_ref.py copied with paths fixed.
- Small-degree end to end test (r=0, m=7812, 25 s): centre c=1 had degG 0, centre c=2 found the collision; verified against the reference and the organizer verifier (log logs\small_r0.txt). Per squaring 5.74M total (3.15M arithmetic).
- Stored-spectrum powering not adopted: it would save about 18% time (0.29 bit) but cost +0.58 bit memory.
Estimate for r=2 (INFERRED, not measured): about 150-165M per squaring, about 40G per centre, memory about 40 MB => about 32.4 for one centre, 33.4 for two, about 34.0 for three. Which centre succeeds is unknown until the run.

Not done yet: packaging (proof.md with full source, claim.json, note, certificates, prefile_check) and the ledger closed forms; the half-gcd has not been given the shared-transform / wrapped-step savings (current hgcd.c). To do after the full run.
Command when released: wsl -d Ubuntu -- bash "./research/poseidon/orchard/exec_r2/src/run_full.sh" 8

## Provenance update after the completed run (13:12, 2026-10-13)

The full-size run subsequently completed before packaging. `logs/full_r2.txt` records one executed centre (`c=1`), a verified collision, `N_run=35,867,769,181`, heap peak `40,741,792`, and 331.2 seconds; the added self-check bound gives `N=35,867,804,181`. `logs/run_full.out` and a fresh `R=2` verifier invocation both report reference and organizer verification success. `pkg_stage/` and `pkg_check/poseidon-orchard-r2/` are identical. The earlier state paragraph above was written before this run and is retained as history; the remaining work is judge-premise review, not execution.
