# Other tracks: distinct paths we could file (scout, 2026-10-09; read-only, no yukon)
Sources: hash-smash docs/FRONTIER_LANES.md, docs/NEW_LANE_BASELINES.md, benchmark.json, lanes/*/candidates/*/claim.json,
research/night/boards.txt (2026-10-06 18:19; the newest saved board for any track but blake3-r2), research/night/scout/
REPORT_agent.md (the earlier scout; REPORT.md was never written) with its others/ and lit/ folders, research/r1_new/PATHS_R1.md.

## Live tracks (benchmark.json lists six, all exploratory)
| Track | Board best 10-06 (review) | Baseline expl/rig | What transfers |
|---|---|---|---|
| blake3-r1 | 0 (winglock, Th0rgal); ours 2, promoted (f0dab7bd) | 149/149 | length cancellation (filed); chunk counter and flags (untested); SAT (path C unsolved) |
| sha256-r31 | 40.4 Th0rgal; published AC2024 2^40.5 | 136/148 | carry counting yes; GPU yes (2^40.5 = ~32 min on the 3090); SAT for message modification; length cancellation no |
| sha256-r32 | 47.275 Th0rgal; all 4 saved entries cut the CRYPTO 2026 35-step attack | 136/148 | as r31; GPU 2^45.7 = ~20 h |
| sha3-256-r5 | 42.19 Th0rgal, 42.4 newjordan; all 4 saved entries use GLL+20 (2-round connector + 3-round trail) | 137.785/149 | SAT connectors (2-round only), GPU trail phase, exact op count; no carries, no length input |
| sha3-256-r6 | 124.295 Th0rgal; bit-sliced birthday searches | 137.4/150 | exact packed count, member loop (shared first-round work); GPU useless at 2^124 |
| blake3-r2 | home track, out of scope | 149 | - |
Not live: keccak800-r5/r6 (149, qualified 09-13, "No Yukon import has been submitted"), md5-s63/s64 (79/82),
sha1-r79/r80 (94/94); boards "no data" on 10-06; all rigorous lanes excluded from import. None can be filed today.

## Ranked: (chance of a distinct, defensible entry) x (cost)
1. sha3-256-r5, internal differential (Zhang-Hou-Liu EUROCRYPT 2023, Sec 6.3: 2^105; full paper on disk, lit/ec2023_zhang_hou_liu.pdf).
   None of the 4 saved r5 entries uses it. Self-contained write-up plus an exact count of its phases, ~105-110 (estimate). 2-4 days.
   Check first, not done: the paper's padding and round numbering against the prefix-v1 target.
2. blake3-r1, domain-flag cancellation: a one-block root (flags 11) against a 2-chunk parent root (flags 12). It cancels v15 in the
   column-3 call through m6/m7, as Path A cancels v14 through m4/m5. Reuses r1_new/pathA code. About 1 day; ~5 (~35 compressions).
   Risk: the child CVs need round inversion (Path B, already on the track), so the judge may call it a variant. Untested.
3. sha256-r31, the older Li-Liu-Wang route (EUROCRYPT 2024: 2^49.8 time, 2^48 memory; memory is free here). It differs from the
   AC2024-based entries, and carry counting checks its conditions. Only slides on disk (ePrint returned 403), and the proof needs
   the characteristic tables. 3-6 days; ~50.
4. sha3-256-r6, accounting only: fold the first round (10 nonzero lanes) and compute only 4 output lanes in the last round.
   Maybe 0.2-0.5 bit under 124.295 (unmeasured). Same birthday path, not distinct; our load charging loses ground. 1-2 days.
5. sha256-r32, a different 2026 paper (EC2026 37-step trail search, or ePrint 2026/1120 at 36 steps 2^57) cut to 32 steps.
   It differs from the 35-step cuts, but the papers are not on disk. 5-10 days; low.
6. sha3-256-r5 with a SAT 3-round connector: AC2022 (on disk) says these are infeasible for SHA3-256. Rerunning GLL+20 to get our
   own witness is not distinct. Skip.
7. Non-live lanes: put one line in the organizer-notes batch asking whether keccak800-r5/r6 will be imported (selected and
   qualified 09-13). If they open, the first entries there are distinct by default. Public MD5/SHA-1 tools land far below 79-94
   (not counted here).

Not established: boards after 10-06 for these five tracks; whether a distinct path that does not beat the best counts toward the
path tally; what the 10-06 top entries contain.
