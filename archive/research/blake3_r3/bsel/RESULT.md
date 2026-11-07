# blake3 r3 u5b (B3R3u5b) - RESULT 2026-10-17 02:2x MDT

STAGED, NOT SUBMITTED. Slot ~/hashsmash/yukon/pos_b3r3u5b (WSL), mechanically_valid, intake passed. Submit script (NOT run): research/launch/submit_pareto_pos_b3r3u5b.sh (bash -n ok; refuses if STAGED.sha256 or dependencies.json changed; deps guard).

- time_log2 **124.76596** vs best r3 62cfd777 124.8123: **-0.0464 bit** (beats it; v2 rebuild 42a0c301 was 124.83986). Memory 1,048,509 B <= 2^20 (setup phase 223,351 B), claim memory_log2_bytes 20, success >= 0.39 (certificate in Appendix A), preprocessing_log2 14.9.
- Program: 62cfd777 at 17,238 gates/step (17,275 ops/batch), 771 registers (800 declared), recovery circuit 603 gates; gates 5 B each: code 132,935 B (687,060 before); table 87,359 entries x 10 B (12,494 x 25 B before); Tp 1328; N = 23073571264435560847886065804406703968283.
- Trail field: 17-bit trail number + 63-bit key. Exact bound 256 + 87,359 + 1 + 1 = 87,617 < 2^17 (> 2^16); asserted in bsrho._plan; proof 3.1/3.8 and note answer a0398a27 F1-trail-index-overflow / F1-trail-id-overflow. rulecheck R21 names all 16 ids of 41b32afc + a0398a27.
- Cloud bit-exact vs organizer blake3(M,3) (root@cloud, nice 19, 2 procs; research/blake3_r3/compact_u5b/cloud_chk/*.out): program digest 2000 msgs at 3/4/7 rounds 0 diff; one step 8,192 lanes 0 diff; 3 chained steps 4,096 lanes 0 diff; packed recovery 448 and scalar 300 0 diff; 5-byte records from the C generator, 8,192 lanes 0 diff; selftest True.
- Generator: C port compiled to wasm 1,445 instr (same as r4), identical program (sha256 fa959a2e...) in the 1 MiB VM (fuel 15.2M) and native under prlimit --data 2^20; ref program 17,238 instr / 771 regs / 70,680 calls.
- Organizer intake (Docker): bsrho-n18 167/256 pairs, proj-k0-w256 165/256, judge-evidence under limit. rulecheck: 15 PASS, 4 N/A, 3 EXPOSED (R05, R07, R19: same wording as the accepted r3 entries). prefile_check: all PASS except "experiment programs known-good" (hash list has no bsrho.py; experiments run 2.7 s / 4.4 s).
- Dependencies (11, first 62cfd777): 62cfd777, eaef120f, 0ecdfe35, a6ee439c, 9f69f1cc, 41b32afc, 75d5e1f9, 0a9640ed, 3356413f, 6ae36351, 616120b2.
- Not tested: Python tooling not run under the 1 MiB cap (only the generator); H1 at width 256 declared, not proved; 5-byte word is a declared convention (36-byte fallback priced in proof 3.8: table 31,946 entries, 124.77707).
- Levers tried (cells in research/dig/new/edge_b3r3_u5b.jsonl): entry 9 B / 8 B -> 124.76640 / 124.76663 (KILLED, worse); regs 771 (+92 entries, < 1e-5 bit, not built).
- Rebuild: patch3.py + patch4.py (retarget r4 -> r3), embed_gen.py, gen_c/make_cport.py, tm_run.sh, run_appA.sh, build_all.py, restage.sh, cloud_push.sh.
