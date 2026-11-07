# POSR5M tighter-arena rerun (final_r5t) - started 2026-10-15 16:48:36Z, NOT submitted

## 1. Why ARENA 5.6e9, not <= 5.0e9
- Live payload peak = 4,759,669,952 B (stage C and D tie). The allocator (large blocks first-fit from the bottom, small from the top) wastes space to fragmentation; the filed run's measured RSS peak (memmeter, touched pages) was 5,401,976,832 B = 13.5 % over live. The extent printed (6.4e9) is just ARENA, the high-water mark was not printed.
- r3 lesson (exec_r3t21): ARENA 215M for a 202.8M live peak failed in stage D; 250M (+23 %) worked. memcomp/poseidon_r345 ANATOMY s5: shipped policy minimum at r3 was +15.8 % over live (replay of the exact r3 alloc/free sequence); r5 replay is not available (needs the hours-long stage D), so no r5 dry run was made.
- So with the shipped allocator the arena cannot go below roughly the touched peak 5.40e9 (>= 5.0e9 would likely abort in D, hours in). Reaching ~4.8e9 needs an allocator change (SMALL_BLOCK 4 MiB made the r3 extent equal the live peak) - a source change, not done here.
- Chosen: ARENA 5,600,000,000 (3.7 % above the touched peak, 17.7 % over live). Layout is identical to the filed run until the free gap closes, so the same sequence that fit in 5.40e9 touched pages fits; residual risk: extent could exceed touched pages if some block parts were never written (not measured). If it aborts, fallback is ARENA 6.0e9.

## 2. Build (cloud /root/hs/mt/final_r5t, sources /root/hs/mt/src_final_r5t)
Only change: common.h line 57, ARENA 6400000000ULL -> 5600000000ULL (diff -r vs src_final_r5 shows only that line). Same gcc command and flags as cycle.sh (-O3 -march=native -mcmodel=medium -static -nostdlib ...), SRCS single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c.
- binary sha256 423d554f68c0dba5e296a7bdecfbd5caa05909fb990c890e3d7acb0fe9df782f (filed: 4ca18cf9...); size text 402104 data 32 bss 5603721212 (image 5,604,123,348 + 65,536 stack = 5,604,188,884 B)
- source sha256: /root/hs/mt/final_r5t/SOURCES.sha256 (21 lines; all equal to the filed set except common.h = 5700c00120bccc4f2293...).

## 3. Run
- /root/hs/mt/run_r5t.sh (same as run_r5.sh; folder /root/hs/mt/run_r5t; memmeter wraps `ulimit -s 64; ./single 1 13`; outputs run.tmp, mem.tmp, start.txt, end.txt).
- Threads: queue had 17 jobs running (load 17.2 of 32) -> free 15 -> T = 13. Started directly with nohup setsid at 16:48:36Z (not via queue.txt, no job stopped); pids 181821.. alive. Load afterwards ~21-30, so the queue runner will start nothing more that does not fit.
- Collect: run.tmp (RESULT/COLLISION, SUMMARY heap_peak, THREADS n=13 line), mem.tmp, end.txt. The ledger will state 13 threads and its own thread_control charge, so the package must be rebuilt for n=13 (cycle.sh NTHREADS=13 --import).

## 4. Expected
- Wall: filed run 21,946 s at 16 threads; at 13 threads about 27,000 s = 7.5 h (range 7-8.5 h) -> finish ~00:20Z 10-16.
- Memory claim = max(arena+image+stack = 5,604,188,884 B, measured peak RSS ~5.40e9) = 5,604,188,884 B, log2 32.384 (was 32.577: -0.193 bit).
- Score = time 34.7397 (+-: thread_control differs for 13 threads, algorithmic 9,171,678,989,504 unchanged; ~0.001 bit) + 12.384 = about 47.124 (filed 47.3167).
- Not tested: mt==single at RR=5 (as before); extent-vs-touched risk above; package/proof/note for n=13 not rebuilt.
