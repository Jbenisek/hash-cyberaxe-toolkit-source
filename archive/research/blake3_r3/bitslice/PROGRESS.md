# BLAKE3 r3 bit-sliced 256-lane chain: progress

2026-10-13. Files: `bitslice.py` (generator, analysis, validation), `driver.py` (256-lane search). Both import the filed
`b3r3s/pkg/blake3/experiments/rho.py` read-only (scalar chain, packed 595-op circuit, is_dp/dp_key/recover). Python 3.14,
1 process, nice 19, no GPU. Labels: COMPUTED = run here.

## Item 1: run-time generator (DONE)
`bitslice.Step(n)` traces the 3-round digest of 0^32 || x on planes (256-bit ints), hash-consed, constants folded, dead gates
removed, polarity-tracked, emitted as a straight line `tK=a^b` (rho.py Tracer style) and compiled with exec. Generator source is
about 14 KB; the emitted line count is 19k (452 KB of text, produced at run time, not shipped).
- Ops per 256-lane step, n = 256 (COMPUTED): **19,022** = 18,897 gates (15,807 XOR, 2,396 AND, 694 OR) + 125 NOT fixes (xor with
  all-ones). The chain feed is renaming; the 125 fixes are the output planes whose polarity differs from the input plane they
  feed. A hill climb on the input polarity vector (`find_pin`, vector cached as PIN256) did not reach zero fixes: the best
  gates + fixes is 19,022, the same total as bs.py's 19,022 (+129 fixes bound 19,151 is beaten by 129 ops). The mix differs from
  bs.py (XOR 15,932 incl. fixes, AND 2,518, OR 572 there; here XOR 15,932 incl. 125 fixes, AND 2,396, OR 694).
- Peak live planes (inputs live at start, results reuse a dying operand's register, creation order): **771** (bs.py said 871 with
  another counting).
- spill_ops(R), Belady over this program order (loads + stores per step): R=1024: **0**; 1000: 0; 900: 0; 512: 862; 256: 3,424;
  128: 5,642; 64: 9,288. So a declared 1,024-plane register file needs no spills at all (the earlier 512 at R=1024 came from a
  worse order). R=512 gives 19,884 ops/step (+4.5%); the earlier 20,978 was an upper bound.
- Reduced width n = 22 (same generator, planes >= 22 constant 0): 10,254 ops (10,248 gates + 6 fixes), peak live 537.

## Item 2: 256-lane driver (DONE)
`driver.py`: per batch one step; stage 1 = OR/AND of the s1 low digest planes of word 0 into a 256-bit lane mask (cost counted
from the polarities, `stage1`); per flagged lane stage 2 = extract the lane (`lane_value`), test the window with rho.is_dp;
finished trails go to a table (rho.pack_entry 25-byte entries, dp_key); new starts inserted by `set_lane` (polarity aware);
trails older than c = ceil(kappa L) batches are cut every Sb = 8 batches and restarted; a key match calls `rho.recover` (the
packed 595-op circuit, 2 lanes, call-counted via a wrapper). Pairs are checked with the scalar `rho.digest_words` (distinct,
complete digests agree on the low n bits).
Validation (COMPUTED):
- n = 256, full 256-bit digest of 10,240 random lanes vs `rho.digest_words`: **all equal**.
- n = 256 chain step vs `rho.f_scalar`: 10,240 random lanes one step, and 2,560 lanes chained 4 steps: all equal.
- n = 22 chain: 10,240 lanes one step, 2,560 lanes chained 6 steps: all equal.
Reduced instance (n = 22, the rho-n22 chain, 256 lanes; 20 trials each, up to 60 attempts; budget B batches = ceil((ureq +
2*256*L)/256), ureq = isqrt(2 N lambda)+2, lambda 0.497):
- s1=2, W=1, Tp=1 (L=8, B=24, Q=6144): 20/20 trials return a verified distinct pair; 24 attempts in all (3 halts "recovery
  found no pair" = one trail starting on another's path, same halt as rho.py); 23 recoveries on the packed circuit (134 packed
  batches); 10,837 trails finished, 21,602 stage-2 checks.
- s1=3, W=2, Tp=2 (L=16, B=40): 20/20 verified pairs, 24 attempts, 24 recoveries (209 packed batches), 4 halts.
- cut path (same plan, kappa 1.5, c=12): 6/6 verified pairs, 57 cuts and restarts.
Over-provisioned: the in-flight allowance 2*256*L makes Q about 3x the needed 2042, so P per attempt is about 0.9, not 0.39. Not a
claim about the real width.

## What remains
- Item 3: restated Lemma 2 and ledger for 256 trails per body (in-flight 256 L points, density 2^-114.8, table size and d
  refit, code 36 B/op = 19,022 ops x 36 = 685 KB + packed recovery 23 KB, stage-2 and event charges from the counters above:
  insert/extract are about 3n / 4n plane operations per event, charged 2,000 in the estimate).
- Item 4: the proof/claim with the declared register file premise (1,024 plane words = 32 KiB counted as memory; peak live 771,
  spill_ops(1024) = 0). Open: whether a 1,024-word file is declarable (rule text), and the n = 256 stage-1 form: s1 = 32 means
  31 ORs + complement + compare + branch = about 35 ops per 256 lanes (driver's `stage1` reports the exact count from the polarity).
- Not done: a smarter scheduler than creation order (would lower peak live and the R=512 and below spill rows); a polarity
  assignment with fewer than 125 fixes; the n = 256 run itself (not runnable).

## Items 3 and 4 (DONE, 2026-10-13 evening)
- Shipped program: pkg/blake3/experiments/bsrho.py (41 KB; scalar digest, packed recovery circuit, bit-sliced generator, register allocation, plan/ledger/loss, search, two organizer experiments, --selftest --ledger --loss --sweep --stats). Package built by make_pkg.py + make_claim.py (proof, claim, manifest, note, dependencies); appA.py is the ledger appendix.
- Ledger (36 B/instruction, 1,024 registers counted as 32,768 B): body 19,060 ops per 256-lane batch, Tp 138, tmax 9,938, kappa 11, M 350 in-flight, N = 26546193039929391864594513070574453234113, time_log2 124.96822, success lower bound 0.39122. R=512 (862 spill ops): 125.03562; R=256: 125.25384.
- Stage: slot ~/hashsmash/yukon/b3r3bs_pkg, prefile_check ALL PASS, pareto_pipeline intake mechanically_valid, both organizer experiments 256 trials (bsrho-n18 165 pairs, proj-k0-w256 162 pairs), evidence 110,169 B. Submit script research/launch/submit_pareto_b3r3bs.sh written, NOT run.
