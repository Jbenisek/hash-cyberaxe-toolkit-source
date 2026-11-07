# Changes against orchard/exec_r6mt (copy in this folder; exec_r6mt untouched)

Files copied unchanged: common.c common.h hgcd.c hgcd.h lean.c ntt.c ntt_a3.h ntt_kern.h outbuf.h pallas.c pallas.h pallas_consts.h par.c par.h poly.c nolibc.c.
Added for testing: verify_collision.py, poseidon_ref.py (copies from exec_r5tt), build_all.sh, run_r3.sh, verify_r3.sh.

## attack.h
* declares `rnd_fp320` (the coin draw);
* declares `split_find_root_capped`;
* `DMAX` (default 16) and `ZCAP` (default 64) as compile-time defines (Z of the proof).

## line.c
* new `rnd_fp320(fp *a)`: centre/shift from five 64-bit coin words w0..w4 read from the program's word generator (xorshift64, `rnd64`), value `w4 2^256 + ... + w0` reduced mod p by Horner with B = 2^64 mod p (B = (2^32)^2). Charges as executed: 5 x 11 control (xorshift) + 5 random-word operations (`X.rnd`) + 12 loop control + 2 call entry; 5 conversions (counted multiplications), 1 conversion + 1 squaring for B, 4 multiplications, 4 additions (all through pallas.c counters). Total 15 field operations + 5 rnd + 71 control per draw. Statistical distance from uniform <= p / 2^320 < 2^-65.
* `rnd_fp254` kept (now unused).

## single.c
* `MAXTR`: `#ifndef MAXTR / #define MAXTR 2` (K, compile-time; was fixed 64).
* `AMAX` extended: RR 7 -> 29, RR 8 -> 31 (3 * 2^a >= 2m - 1); RR <= 6 values unchanged.
* single thread: the `nthr` parse of argv[2] and `par_init(nthr)` replaced by `par_init(1)` (no worker, `par_nt = 1`, so every thread-control charge, dispatch and `thr_*` counter is zero). par.c/par.h/the `par_nt>1` branches in ntt.c, lean.c, line.c are NOT deleted (see Not done).
* `rng_seed(1)` -> `rng_seed(COIN_SEED)`, `COIN_SEED` default 1 (compile-time; the test uses seeds 1, 2, 3).
* centre: `fp_from_u64(&c, i)` (c_i = i) -> `rnd_fp320(&c)`; stage name "A: centre from coins". `t_centre[]` still holds the trial index i (it is no longer the centre); the centre is printed in the final `COLLISION centre` line.
* failure exit: `if (trials > MAXTR) return 2;` tested at the start of each trial (no message, no output, nothing flushed; was a stderr message).
* `deg G > DMAX` ends the trial like `deg G = 0` (`if (dG < 1 || dG > DMAX)`), control charge `CTL(2)` -> `CTL(2 + 2)`.
* stage E calls `split_find_root_capped` instead of `split_find_root`.

## split.c
* new `split_find_root_capped(root, G, d)` (proof 4.1.2): while d >= 2, at most ZCAP rounds: draw `a` by `rnd_fp320`; `taylor_shift` by -a (roots r + a); `S = Z^((p-1)/2) mod G` (`pow_half`, schoolbook for d <= 40); `G+ = gcd(G, S - 1)`, `G- = gcd(G, S + 1)` by `gcd_cl`; keep the part of smaller nonzero degree (ties G+); both constant -> G = Z; after ZCAP rounds with d >= 2 return 0 (trial fails). d = 1: root = -G0 - (sum of shifts). Charges follow the style of the old function (LD/ST/loopc/CTL).
* old `split_find_root` kept in the file, unused (removed by --gc-sections).

## Not changed on purpose
All counters, stage table, RECONCILE, SUMMARY, THREADS/THREADMEM/PEAKLIVE/TYPES lines, stage I report charge (still the old constants, not the worst-case constant of README item 6), ARENA default (36.5e9, overridden on the command line for r3/r7/r8).

## Not done (README items outside this task)
* thread code is not deleted from par.c/par.h/ntt.c/lean.c/line.c: with `par_nt = 1` it is never executed and charges nothing, but it is still in the source (the proof says it is removed). par_tls_boot (TLS block) lives in par.c and is needed.
* stage I / report charge not turned into a worst-case constant; the report is printed in the old format.
* the word source is xorshift64 seeded at compile time, i.e. deterministic: for a run it stands in for the coin tape. Where real coin words come from (organizer tape, getrandom, a system call charge) is not decided here.
* stage-E root of `d = 1` skips the `Z^((p-1)/2)` stages as the proof says; d = 2 now goes through the same round loop (the old special-case quadratic formula is not used).
