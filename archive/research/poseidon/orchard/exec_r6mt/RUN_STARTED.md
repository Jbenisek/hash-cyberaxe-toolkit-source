# r6 counted run STARTED
- Start: 2026-10-15 18:53:11 UTC (owner go ~12:52 MDT). Dir /root/hs/mt/run_r6_T24 (run.tmp, mem.tmp, start.txt, end.txt); log /root/hs/mt/run_r6_T24.log.
- T = 24 (box shared with r5t 13 threads + swarm, load ~26; counted ops do not depend on T, only wall).
- Binary /root/hs/mt/final_r6/single sha256 8d8a442299337d4fa40db3874cbcbffca7e17464f8bdea4e6b9d1b5ac262bbb6 (size: text 402104, data 32, bss 36504851708; no warnings). SOURCES.sha256 file sha256 d721d1b2f1b5926605e5399af4819c8bd41c30215537ecb07fb97de28c12aa63 (per-file list in /root/hs/mt/final_r6/SOURCES.sha256).
- Expected wall per trial at T=24: about 40-55 h on an idle box (R6_PLAN table: T=16 50-59 h, T=30 40-49 h); longer while the box is loaded. 1 trial p=0.39; expect ~2.56 trials.
- First check (4 min in): PID 186166, 24 threads, 1053% CPU, RSS 8.4 GB growing, no crash.
- Progress: run.tmp is empty until the end. Use ssh to ps (RSS/CPU of `single 1 24`), /root/hs/mt/peek.py or thr.sh; memmeter writes mem.tmp at the end. At end check r=6 line=0 m=122070312, THREADS n=24, heap_peak ~31,046,103,6xx, COLLISION lines.
- If "out of memory" abort in stage C/D: raise ARENA to 38.0e9 then 40e9 (R6_PLAN).
