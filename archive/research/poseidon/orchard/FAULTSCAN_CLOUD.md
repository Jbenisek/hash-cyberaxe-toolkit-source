# Fault scan: cloud box vs local PC (2026-10-15/16)

Question: is the random wrong result (SPEEDUP.md section 0) a property of the local machine or of the program?

## Method
- Sources: WSL `/tmp/scan/` (exec_r6mt sources plus checksum prints, `ck.h`, RR=1; the dir the speedup agent used; the original scan script was not saved, so it was rebuilt from the description). Copied to cloud `/root/hs/faultscan/` (`*.c`, `*.h`, `fs_scan.sh`).
- Build: `gcc -O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -w -DRR=1 -o a single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c`.
- Run per offset: `ulimit -s 64; env -i PAD=<p x-chars> nice setarch -R ./a 1 1` (one thread, ASLR off, one run at a time), p = 0, 16, ..., 496 (32 offsets). Checksum read: `CK t1 F` on stderr. Correct value: `ea2ea8d8e7a70221`.
- Cloud: AMD EPYC-Turin, 32 vCPU, load average about 38 (r6 counted run and other jobs untouched), nice 19, about 2 min per run. Cloud scan went on to 34 offsets (0..528) before I stopped my own scan; all 34 are in the cloud count below.
- Local: same sources rebuilt in `/tmp/faultscan_local` (the new binary differs from the old `/tmp/scan/a` in header bytes, same size; flags guessed from val_run.sh), nice 10, load average 12-15, first 32 offsets.

## Result
| side | runs | correct (`ea2ea8d8...`) | wrong |
|---|---:|---:|---:|
| cloud (Vultr), first 32 offsets | 32 | 32 | 0 |
| cloud, all 34 done | 34 | 34 | 0 |
| local, today, first 32 offsets | 32 | 28 | 4 (offsets 32, 368, 400, 432; 4 different wrong values) |
| local, earlier scan (SPEEDUP.md) | 64 | 47 | 17 |

Local today 4/32 (12.5 %) vs 17/64 (27 %) earlier; cloud 0/34. Chance that a 12.5-27 % fault rate gives 0 in 34 is below 1 %.

## Conclusion
The wrong results follow the local machine, not the program: the identical source and flags give the correct checksum in every cloud run, and the local box still faults today (at different offsets than before, so not stack layout).

## Not tested
- The cloud run used an identical source but a binary rebuilt on the cloud CPU (`-march=native`, so different instruction selection is possible); the exact local binary was not run on the cloud.
- Only 34 of 64 offsets on the cloud, 32 of 64 locally; the original scan script was reconstructed, not copied.
- Not tested which local component is at fault (CPU, RAM, settings): memtest86+ / prime95 still pending.
- Cloud load was high (about 38 on 32 vCPUs) but the cloud is a VM; a fault there could be hidden only if the host corrected it.

Files: cloud `/root/hs/faultscan/scan_out/summary.txt`; local WSL `/tmp/faultscan_local/scan_out/summary.txt`.
