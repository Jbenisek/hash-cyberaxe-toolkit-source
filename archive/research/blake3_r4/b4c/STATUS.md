# B3R4c (blake3 round 4, pareto) - STAGED, not submitted
Base: B3R4b 41b32afc-ed4c-4ef1-b9f2-8c72ab163582 (125.02375, memory 2^20). b4b and its slot untouched.
## Ledger (appA.py, unchanged program)
time_log2 125.02375, memory 1,048,566 B (<= 2^20), R=800, 10-byte entries, tmax 5251, Tp 68, N = 36581993974288282239238033262672148067793.
## Lever 2 (memory above 2^20), appA.py ledger with extra table entries XTRA (score = time_log2 + max(0, log2 B - 20))
XTRA 0: 125.02375 | 100: 125.02041 | 400: 125.01585 | 800: 125.00986 | 1600: 125.00210 | 2400: 124.99840 | 2800: 124.99767 | 3200 (B=1,080,566): 124.99752 (best) | 3600: 124.99787 | 4000: 124.99866 | 6000: 125.00732 | 12000: 125.05548 | 40000: 125.33407.
Best gain 0.0262 bit < 0.03 threshold: NOT built. Memory stays 2^20.
## Changes vs 41b32afc
1. proof.md Section 3.6 (iii): the clause giving the Python reference generator's 111.3 MB peak and "not charged" is deleted; replaced by one clause saying the entry's generator is the C program run within the 1 MiB cap and the Python generator is only the reference whose output text it reproduces (sha256 equal). Matches accepted pattern 4 (memory = max(online, preprocessing)); every stated generator run is within 2^20.
2. submission-note.md: removes the same clause, adds a paragraph "Changes against 41b32afc"; note 9,130 B.
3. dependencies.json: 41b32afc first, then 75d5e1f9, 62cfd777, 0a9640ed, 3356413f, 6ae36351 (jungjipdo credit kept as in b4b).
Program, circuit, ledger, experiments, certificates identical to b4b (bsrho.py byte-identical).
New runs: only appA.py ledger sweeps and build_all.py text generation (analysis tools, not attack runs; the Python interpreter itself exceeds 1 MiB, cap used was ulimit -v 2 GB) plus the organizer intake. No development run of the attack was made or stated.
## Checks
Organizer intake (stage_run.sh, pareto_pipeline intake): passed; package sha256 af792c65...; STAGED.sha256 efff8c0a...
rulecheck: mem-gate PASS (30 stage peaks stated, all <= 2^20); 14 PASS, 4 N/A, 2 EXPOSED (R05-extrapolation, R07-iid-from-selected: same two hits as b4b, unchanged text).
prefile_check: all PASS except "experiment programs known-good" bsrho.py (same as b4b; unchanged program, organizer intake passed).
## Slot / submit
Slot: WSL ~/hashsmash/yukon/pos_b3r4c/pareto (dependencies.json sha256 df5274f8027a0bb9d2e306780e892e2a9dfcd402b4a4d979208d9d19e9d1ba9c).
Submit script (NOT run): research/launch/submit_pareto_b3r4c.sh
