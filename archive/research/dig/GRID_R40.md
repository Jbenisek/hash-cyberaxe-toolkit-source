# Task 34 - SHA-256 r40 lever knowledge grid

Generated 2026-10-21 from the listed r40 source artifacts and the existing dig schema. This is a research grid, not a submission or package record.

## Scope and status discipline

The r40 recurrence is the SHA-256 schedule W_t = sigma1(W_{t-2}) xor W_{t-7} xor sigma0(W_{t-15}) xor W_{t-16} in the XOR-linear source model; the real compression path uses modular addition and state rows. A finite XOR or tail result is never promoted to a signed/modular collision.

Grid status codes are: COMPUTED exact finite arithmetic or a reproduced local run; LOCAL_ONLY a finite/XOR/window result that does not establish the full path; OPEN no nonduplicate permitted result; EMPTY no applicable r40 board/judge entry in the listed source set. The pre-FIX2 nldtool runs that forced expanded words and late state rows to zero are VOID for promotion. FIX2 logs are retained as diagnostics only.

Sources read: research/profiles/R40_COMPUTED_CHAIN_1021.md, research/luna/RIVER_SYNTH_1021.md, research/outside/reaction_graph_1021.md, all research/grok/work/G_river_*/ANSWER.md and G_r40_*/ANSWER.md, research/levers_1021/s256_r40_search/NLDTOOL_1021.md, and the nldtool/*.run.log files.

## Fixed computed facts

- The filed r39 claw has zero output-XOR bits at n=39; at n=40 the output-XOR weight is 21 and the state after step 38 is zero, but dA39=406266c0, dE39=40222e40.
- The unchanged support {8,9,10,11,12,16,17,24,26} produces nonzero dW39,dW40,dW41 for every claw; its r40 collision probability is exactly zero in that construction.
- sigma0 and sigma1 each have GF(2) rank 32 and kernel dimension 0. The map to (W39,W40,W41) has rank 96/kernel 416; the wider target map has rank 352/kernel 160.
- The reaction graph lands W24 on W39/W40 and W26 on W41/W42. The old-cut backward-injectivity argument collapses the unchanged support if W24=W26=0. Induced rows W27/W32/W33 remain active in the source model.
- The owned L11 release replay is exact in the XOR schedule: with target rows {24,26,39,40,41,42}, the old support {8..12} has rank 160/kernel 0; adding {13,14}, {13,15}, or {14,15} gives rank 192/kernel 32. The three published lightest vectors have exact target-zero tails, but nonzero model-Z endpoint states. This is finite/LOCAL_ONLY, not a modular characteristic.
- The owned L12 placement replay verifies sigma0 rank 32 and, for XOR dW24=03010000 with dW23=dW32=dW37=0, gives dW39=406622c0 and dW40=03010000. The carry-aware local artifact independently reports nonzero dW39=401e2240 (modular) / 4022e640 (XOR). Thus the W39 placement is structurally impossible for the fixed trail; shifted compensation costs at least +58 expansion bits, while the existing row-16 claw remains r39-only.
- Exact XOR-linear tail results include living-end joins s=21 weight 1, s=19 and s=20 weight 2; exact N=40 tail values include s=17:217, s=18:230, s=19:35, s=20:44, s=21:51. These are XOR-linear window values, not modular characteristics.
- The full signed nldtool control found a 40-step characteristic in about 334 s; join16 and stage1 were NOT FOUND at 1170 s; stage2 was an initial-propagation contradiction for n=40..43. Pre-FIX2 forced-expanded-word/late-row instances are VOID.

## Q1-Q14 question template

| Q | name | question |
|---|---|---|
| Q1 | cost ledger | Where does every operation go for this lever, including expansion, recovery, setup, preprocessing, and advice? |
| Q2 | dispatch/control charge | Which loop, branch, filter, load/store, dispatch, and register operations are charged? |
| Q3 | memory peak/drain | Which buffers are live at peak and can release, alias, or streaming lower the binding peak? |
| Q4 | table/entry packing | How are tables, entries, fixed masks, and code bytes packed and charged? |
| Q5 | success-bound slack | What proven success bound or finite rate supplies the probability/time term, and what remains unproved? |
| Q6 | premise/evidence | Which model premise is used and what organizer-executed evidence is still missing? |
| Q7 | preprocessing/advice | What nonuniform preprocessing/advice is used, and is its time, memory, or size charged? |
| Q8 | rival/board | What r40 rival or filed row is relevant, or is the square empty in the listed source set? |
| Q9 | applied/unapplied levers | Which other levers interact with this one, and what measured gain is actually available? |
| Q10 | judge finding/status | What judge/ruling evidence applies to this lever in the listed files? |
| Q11 | neighbor transfer | What transfers from r39, r41, adjacent joins, or neighboring windows without remeasurement? |
| Q12 | structural specialness | Is there a boundary, regime change, special support, or changed free-round budget? |
| Q13 | step program | What partial/full-round, hidden-basis, and schedule-program costs change? |
| Q14 | DP/recovery | What distinguished-point, gap-law, recovery, and final-check costs change? |


## Lever summary

| id | lever | definition/effect | interaction and test | overall status | evidence |
|---|---|---|---|---|---|
| L01 | message-difference support | which message words may be nonzero. Changes late rank, tail weight, and claw-compatible expansion words. | G_river_2/3 exact join/tail tables; G_r40_support_zero/linmodel.py | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named |
| L02 | join step | s in 6..34 where the active support starts. Changes kernel dimension, closing window, cluster, and active W16..W39 count. | G_river_2/3/4/5/6/7/8 ANSWER.md; exact tail data | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named |
| L03 | late-word constraints | W39..W42 forced zero versus cancellation/bridge. Changes the target map, rank/kernel, reaction closure, and modular feasibility. | R40_COMPUTED_CHAIN_1021; reaction_graph_1021; NLDTOOL_1021 | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named |
| L04 | tail window | N=40..42 target and closing words. Changes tail dimension, minimum weight, cluster and recovery window. | G_river_2/3/4/5 ANSWER.md; exact tail data | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named |
| L05 | cluster start word | least nonzero W_i in the witness. Determines whether the witness is early-prefix-free and whether a claw can absorb it. | G_river_2/3/4/5 ANSWER.md | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named |
| L06 | early-word freedom | free or pinned W0..W8. Changes condition-free status, message dimension, and state-seam feasibility. | G_river_2/3/4/8 ANSWER.md; item3970 audit | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named |
| L07 | sign choices | XOR-linear versus signed/modular differences. Changes sigma identities, carry behavior, signed condition count, and real-path validity. | R40_COMPUTED_CHAIN_1021; G_r40_signed/linmodel | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named |
| L08 | state-row freedom | which A/E rows remain free or pinned. Changes nldtool propagation, nonlinear state feasibility, and full-path status. | NLDTOOL_1021; G_r40_stage1; G_r40_synth; owned Task35 L08 model-Z replay | COMPUTED finite / OPEN full-path | Finite A/E projection replay is complete; signed/compression embedding remains open |
| L09 | chaining-value difference | free-start, semi-free-start, or two-block CV delta. Changes the entry boundary and whether a message-only kernel is a valid compression characteristic. | R40_COMPUTED_CHAIN_1021; G_r40_sha224_template; owned Task35 L09 CV replay | COMPUTED finite / OPEN full-path | Three explicit CV boundaries replayed; two-block first-block embedding and ledger remain open |
| L10 | induced rows 27/32/33 | schedule rows reached by cancellation and closure. Changes whether W24/W26 cancellation really removes W39..W42 injections. | reaction_graph_1021; RIVER_SYNTH_1021 C26/C30; owned Task35 L10 replay | COMPUTED finite / OPEN full-path | Exact induced rows and row-local state counterfactuals are replayed; message-realizable signed cancellation remains open |
| L11 | release sets | extra rows released from the old cut. Changes backward-injectivity, target rank, and the support size needed to reopen the line. | reaction_graph_1021; G_river_6/source_G_backcut_2.md; owned Task35 L11 replay | COMPUTED finite / OPEN full-path | Pair releases produce exact 32-dimensional XOR kernels; signed/modular and charged full path remain open |
| L12 | claw placement | where the distinguished-point/claw matching is applied. Changes the absorbed rows, setup cost, and expansion burden. | claw_place/r39.md; claw_place/r40.md; API2069_answer.md; owned Task35 L12 replay | COMPUTED finite / OPEN full-path | Existing row-16 data and placement barriers are exact finite facts; any new r40 trail and charged score remain open |
| L13 | accounting fields | preprocessing, advice, memory, recovery and DP fields. Changes charged N and score even if the characteristic is unchanged. | owned Task35 L13 static/source reconciliation | COMPUTED finite / OPEN r40 full ledger | TASK35_L13_ACCOUNTING_20261021.md; archive/Dariia/r39-collisions.md; R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md |


## Q1-Q14 matrix (one row per r40 lever)

| id | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Q9 | Q10 | Q11 | Q12 | Q13 | Q14 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| L01 | C | O | O | O | L | L | O | E | C | E | L | C | O | O |
| L02 | C | C | O | O | L | L | O | E | C | E | C | C | O | C |
| L03 | C | C | O | O | L | L | O | E | C | E | C | C | O | O |
| L04 | C | C | O | O | L | L | O | E | C | E | C | C | O | C |
| L05 | C | O | O | O | C | L | O | E | C | E | C | C | O | C |
| L06 | C | O | O | O | L | C | O | E | C | E | C | L | O | O |
| L07 | C | C | O | O | L | C | C | E | C | E | L | C | O | O |
| L08 | C | O | O | O | O | L | O | E | C | E | O | L | O | O |
| L09 | C | O | O | O | O | L | O | E | O | E | O | C | O | O |
| L10 | C | C | O | O | L | L | O | E | C | E | C | C | O | O |
| L11 | C | C | O | O | L | L | O | E | C | E | C | C | O | O |
| L12 | C | C | O | O | L | L | O | E | C | E | C | C | O | O |
| L13 | C | C | C | C | L | L | C | E | C | E | L | C | C | L |

Legend: C=COMPUTED, L=LOCAL_ONLY, O=OPEN, E=EMPTY. The matrix is expanded in the cell ledger below; no blank Q cell is implied.

## Expanded cell ledger

| cell | lever | question | status | evidence/run | remaining check |
|---|---|---|---|---|---|
| R40-L01-Q1 | message-difference support | cost ledger | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run a modular message-support lift after choosing a nonzero kernel vector. |
| R40-L01-Q2 | message-difference support | dispatch/control charge | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a modular message-support lift after choosing a nonzero kernel vector. |
| R40-L01-Q3 | message-difference support | memory peak/drain | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a modular message-support lift after choosing a nonzero kernel vector. |
| R40-L01-Q4 | message-difference support | table/entry packing | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a modular message-support lift after choosing a nonzero kernel vector. |
| R40-L01-Q5 | message-difference support | success-bound slack | LOCAL_ONLY | `research/cloud_jobs/API2077_answer.md:39` records 0/65536 modular hits for six masks; `:79` explicitly says this is a null sample, not a proof | Obtain a global modular rate or no-go; finite sample gives no score credit. |
| R40-L01-Q6 | message-difference support | premise/evidence | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Run a modular message-support lift after choosing a nonzero kernel vector. |
| R40-L01-Q7 | message-difference support | preprocessing/advice | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a modular message-support lift after choosing a nonzero kernel vector. |
| R40-L01-Q8 | message-difference support | rival/board | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Run a modular message-support lift after choosing a nonzero kernel vector. |
| R40-L01-Q9 | message-difference support | applied/unapplied levers | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run a modular message-support lift after choosing a nonzero kernel vector. |
| R40-L01-Q10 | message-difference support | judge finding/status | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Run a modular message-support lift after choosing a nonzero kernel vector. |
| R40-L01-Q11 | message-difference support | neighbor transfer | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Run a modular message-support lift after choosing a nonzero kernel vector. |
| R40-L01-Q12 | message-difference support | structural specialness | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run a modular message-support lift after choosing a nonzero kernel vector. |
| R40-L01-Q13 | message-difference support | step program | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a modular message-support lift after choosing a nonzero kernel vector. |
| R40-L01-Q14 | message-difference support | DP/recovery | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a modular message-support lift after choosing a nonzero kernel vector. |
| R40-L02-Q1 | join step | cost ledger | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run exact_tail for any unclosed join/window; do not infer modular feasibility. |
| R40-L02-Q2 | join step | dispatch/control charge | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run exact_tail for any unclosed join/window; do not infer modular feasibility. |
| R40-L02-Q3 | join step | memory peak/drain | LOCAL_ONLY | Task35 run `research/luna_dig/TASK35_R40-L02-Q3_20261021.md`; `G_river_4/isd.exe tail 28 40 180000 4`, RUN=TASK35-R40-L02-Q3-20261021-1535, reproduced dim=192, UB=35 and layer-4 lower=20; process stopped before multi-hour layer 5 | Run exact_tail for any unclosed join/window; do not infer modular feasibility. |
| R40-L02-Q4 | join step | table/entry packing | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run exact_tail for any unclosed join/window; do not infer modular feasibility. |
| R40-L02-Q5 | join step | success-bound slack | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Run exact_tail for any unclosed join/window; do not infer modular feasibility. |
| R40-L02-Q6 | join step | premise/evidence | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Run exact_tail for any unclosed join/window; do not infer modular feasibility. |
| R40-L02-Q7 | join step | preprocessing/advice | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run exact_tail for any unclosed join/window; do not infer modular feasibility. |
| R40-L02-Q8 | join step | rival/board | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Run exact_tail for any unclosed join/window; do not infer modular feasibility. |
| R40-L02-Q9 | join step | applied/unapplied levers | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run exact_tail for any unclosed join/window; do not infer modular feasibility. |
| R40-L02-Q10 | join step | judge finding/status | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Run exact_tail for any unclosed join/window; do not infer modular feasibility. |
| R40-L02-Q11 | join step | neighbor transfer | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run exact_tail for any unclosed join/window; do not infer modular feasibility. |
| R40-L02-Q12 | join step | structural specialness | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run exact_tail for any unclosed join/window; do not infer modular feasibility. |
| R40-L02-Q13 | join step | step program | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run exact_tail for any unclosed join/window; do not infer modular feasibility. |
| R40-L02-Q14 | join step | DP/recovery | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run exact_tail for any unclosed join/window; do not infer modular feasibility. |
| R40-L03-Q1 | late-word constraints | cost ledger | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run owned modular cancellation with the late rows constrained; nldtool is main-session-only. |
| R40-L03-Q2 | late-word constraints | dispatch/control charge | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run owned modular cancellation with the late rows constrained; nldtool is main-session-only. |
| R40-L03-Q3 | late-word constraints | memory peak/drain | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run owned modular cancellation with the late rows constrained; nldtool is main-session-only. |
| R40-L03-Q4 | late-word constraints | table/entry packing | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run owned modular cancellation with the late rows constrained; nldtool is main-session-only. |
| R40-L03-Q5 | late-word constraints | success-bound slack | LOCAL_ONLY | `research/grok/work/G_jointtail_3/ANSWER.md:7-20,26-38,87-112` gives exact model-Z independent-addend counts (best total 48), with dependence/real-trail limitations stated | Prove a real SHA-256 success rate or no-go; conditional DP is not score credit. |
| R40-L03-Q6 | late-word constraints | premise/evidence | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Run owned modular cancellation with the late rows constrained; nldtool is main-session-only. |
| R40-L03-Q7 | late-word constraints | preprocessing/advice | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run owned modular cancellation with the late rows constrained; nldtool is main-session-only. |
| R40-L03-Q8 | late-word constraints | rival/board | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Run owned modular cancellation with the late rows constrained; nldtool is main-session-only. |
| R40-L03-Q9 | late-word constraints | applied/unapplied levers | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run owned modular cancellation with the late rows constrained; nldtool is main-session-only. |
| R40-L03-Q10 | late-word constraints | judge finding/status | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Run owned modular cancellation with the late rows constrained; nldtool is main-session-only. |
| R40-L03-Q11 | late-word constraints | neighbor transfer | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run owned modular cancellation with the late rows constrained; nldtool is main-session-only. |
| R40-L03-Q12 | late-word constraints | structural specialness | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run owned modular cancellation with the late rows constrained; nldtool is main-session-only. |
| R40-L03-Q13 | late-word constraints | step program | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run owned modular cancellation with the late rows constrained; nldtool is main-session-only. |
| R40-L03-Q14 | late-word constraints | DP/recovery | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run owned modular cancellation with the late rows constrained; nldtool is main-session-only. |
| R40-L04-Q1 | tail window | cost ledger | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run exact_tail/isd for an unclosed tail row under the stated window. |
| R40-L04-Q2 | tail window | dispatch/control charge | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run exact_tail/isd for an unclosed tail row under the stated window. |
| R40-L04-Q3 | tail window | memory peak/drain | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run exact_tail/isd for an unclosed tail row under the stated window. |
| R40-L04-Q4 | tail window | table/entry packing | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run exact_tail/isd for an unclosed tail row under the stated window. |
| R40-L04-Q5 | tail window | success-bound slack | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Run exact_tail/isd for an unclosed tail row under the stated window. |
| R40-L04-Q6 | tail window | premise/evidence | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Run exact_tail/isd for an unclosed tail row under the stated window. |
| R40-L04-Q7 | tail window | preprocessing/advice | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run exact_tail/isd for an unclosed tail row under the stated window. |
| R40-L04-Q8 | tail window | rival/board | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Run exact_tail/isd for an unclosed tail row under the stated window. |
| R40-L04-Q9 | tail window | applied/unapplied levers | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run exact_tail/isd for an unclosed tail row under the stated window. |
| R40-L04-Q10 | tail window | judge finding/status | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Run exact_tail/isd for an unclosed tail row under the stated window. |
| R40-L04-Q11 | tail window | neighbor transfer | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run exact_tail/isd for an unclosed tail row under the stated window. |
| R40-L04-Q12 | tail window | structural specialness | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run exact_tail/isd for an unclosed tail row under the stated window. |
| R40-L04-Q13 | tail window | step program | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run exact_tail/isd for an unclosed tail row under the stated window. |
| R40-L04-Q14 | tail window | DP/recovery | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run exact_tail/isd for an unclosed tail row under the stated window. |
| R40-L05-Q1 | cluster start word | cost ledger | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Check whether a later-cluster witness also satisfies the full state path. |
| R40-L05-Q2 | cluster start word | dispatch/control charge | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Check whether a later-cluster witness also satisfies the full state path. |
| R40-L05-Q3 | cluster start word | memory peak/drain | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Check whether a later-cluster witness also satisfies the full state path. |
| R40-L05-Q4 | cluster start word | table/entry packing | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Check whether a later-cluster witness also satisfies the full state path. |
| R40-L05-Q5 | cluster start word | success-bound slack | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Check whether a later-cluster witness also satisfies the full state path. |
| R40-L05-Q6 | cluster start word | premise/evidence | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Check whether a later-cluster witness also satisfies the full state path. |
| R40-L05-Q7 | cluster start word | preprocessing/advice | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Check whether a later-cluster witness also satisfies the full state path. |
| R40-L05-Q8 | cluster start word | rival/board | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Check whether a later-cluster witness also satisfies the full state path. |
| R40-L05-Q9 | cluster start word | applied/unapplied levers | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Check whether a later-cluster witness also satisfies the full state path. |
| R40-L05-Q10 | cluster start word | judge finding/status | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Check whether a later-cluster witness also satisfies the full state path. |
| R40-L05-Q11 | cluster start word | neighbor transfer | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Check whether a later-cluster witness also satisfies the full state path. |
| R40-L05-Q12 | cluster start word | structural specialness | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Check whether a later-cluster witness also satisfies the full state path. |
| R40-L05-Q13 | cluster start word | step program | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Check whether a later-cluster witness also satisfies the full state path. |
| R40-L05-Q14 | cluster start word | DP/recovery | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Check whether a later-cluster witness also satisfies the full state path. |
| R40-L06-Q1 | early-word freedom | cost ledger | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Test a nonzero early-word assignment in the signed state model. |
| R40-L06-Q2 | early-word freedom | dispatch/control charge | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Test a nonzero early-word assignment in the signed state model. |
| R40-L06-Q3 | early-word freedom | memory peak/drain | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Test a nonzero early-word assignment in the signed state model. |
| R40-L06-Q4 | early-word freedom | table/entry packing | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Test a nonzero early-word assignment in the signed state model. |
| R40-L06-Q5 | early-word freedom | success-bound slack | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Test a nonzero early-word assignment in the signed state model. |
| R40-L06-Q6 | early-word freedom | premise/evidence | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Test a nonzero early-word assignment in the signed state model. |
| R40-L06-Q7 | early-word freedom | preprocessing/advice | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Test a nonzero early-word assignment in the signed state model. |
| R40-L06-Q8 | early-word freedom | rival/board | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Test a nonzero early-word assignment in the signed state model. |
| R40-L06-Q9 | early-word freedom | applied/unapplied levers | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Test a nonzero early-word assignment in the signed state model. |
| R40-L06-Q10 | early-word freedom | judge finding/status | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Test a nonzero early-word assignment in the signed state model. |
| R40-L06-Q11 | early-word freedom | neighbor transfer | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Test a nonzero early-word assignment in the signed state model. |
| R40-L06-Q12 | early-word freedom | structural specialness | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Test a nonzero early-word assignment in the signed state model. |
| R40-L06-Q13 | early-word freedom | step program | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Test a nonzero early-word assignment in the signed state model. |
| R40-L06-Q14 | early-word freedom | DP/recovery | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Test a nonzero early-word assignment in the signed state model. |
| R40-L07-Q1 | sign choices | cost ledger | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run a signed/modular replay of a listed XOR witness. |
| R40-L07-Q2 | sign choices | dispatch/control charge | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run a signed/modular replay of a listed XOR witness. |
| R40-L07-Q3 | sign choices | memory peak/drain | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a signed/modular replay of a listed XOR witness. |
| R40-L07-Q4 | sign choices | table/entry packing | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a signed/modular replay of a listed XOR witness. |
| R40-L07-Q5 | sign choices | success-bound slack | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Run a signed/modular replay of a listed XOR witness. |
| R40-L07-Q6 | sign choices | premise/evidence | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run a signed/modular replay of a listed XOR witness. |
| R40-L07-Q7 | sign choices | preprocessing/advice | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run a signed/modular replay of a listed XOR witness. |
| R40-L07-Q8 | sign choices | rival/board | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Run a signed/modular replay of a listed XOR witness. |
| R40-L07-Q9 | sign choices | applied/unapplied levers | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run a signed/modular replay of a listed XOR witness. |
| R40-L07-Q10 | sign choices | judge finding/status | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Run a signed/modular replay of a listed XOR witness. |
| R40-L07-Q11 | sign choices | neighbor transfer | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Run a signed/modular replay of a listed XOR witness. |
| R40-L07-Q12 | sign choices | structural specialness | COMPUTED | R40_COMPUTED_CHAIN_1021.md; RIVER_SYNTH_1021.md; permitted local linmodel/exact-tail evidence where named | Run a signed/modular replay of a listed XOR witness. |
| R40-L07-Q13 | sign choices | step program | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a signed/modular replay of a listed XOR witness. |
| R40-L07-Q14 | sign choices | DP/recovery | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a signed/modular replay of a listed XOR witness. |
| R40-L08-Q1 | state-row freedom | cost ledger | COMPUTED finite | Owned model-Z A/E projection replay; no cost inference | Run a fresh full-state model with a specified released row; current logs are diagnostic. |
| R40-L08-Q2 | state-row freedom | dispatch/control charge | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a fresh full-state model with a specified released row; current logs are diagnostic. |
| R40-L08-Q3 | state-row freedom | memory peak/drain | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a fresh full-state model with a specified released row; current logs are diagnostic. |
| R40-L08-Q4 | state-row freedom | table/entry packing | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a fresh full-state model with a specified released row; current logs are diagnostic. |
| R40-L08-Q5 | state-row freedom | success-bound slack | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a fresh full-state model with a specified released row; current logs are diagnostic. |
| R40-L08-Q6 | state-row freedom | premise/evidence | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Run a fresh full-state model with a specified released row; current logs are diagnostic. |
| R40-L08-Q7 | state-row freedom | preprocessing/advice | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a fresh full-state model with a specified released row; current logs are diagnostic. |
| R40-L08-Q8 | state-row freedom | rival/board | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Run a fresh full-state model with a specified released row; current logs are diagnostic. |
| R40-L08-Q9 | state-row freedom | applied/unapplied levers | COMPUTED finite | Releasing A/E changes only the endpoint projection for fixed vectors | Run a fresh full-state model with a specified released row; current logs are diagnostic. |
| R40-L08-Q10 | state-row freedom | judge finding/status | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Run a fresh full-state model with a specified released row; current logs are diagnostic. |
| R40-L08-Q11 | state-row freedom | neighbor transfer | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a fresh full-state model with a specified released row; current logs are diagnostic. |
| R40-L08-Q12 | state-row freedom | structural specialness | LOCAL_ONLY | Model-Z state-only cancellation control is zero but not message-realizable | Run a fresh full-state model with a specified released row; current logs are diagnostic. |
| R40-L08-Q13 | state-row freedom | step program | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a fresh full-state model with a specified released row; current logs are diagnostic. |
| R40-L08-Q14 | state-row freedom | DP/recovery | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Run a fresh full-state model with a specified released row; current logs are diagnostic. |
| R40-L09-Q1 | chaining-value difference | cost ledger | COMPUTED finite | Three explicit CV boundary modes and state42 outputs replayed; no cost inference | Specify and test a semi-free or two-block CV boundary. |
| R40-L09-Q2 | chaining-value difference | dispatch/control charge | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Specify and test a semi-free or two-block CV boundary. |
| R40-L09-Q3 | chaining-value difference | memory peak/drain | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Specify and test a semi-free or two-block CV boundary. |
| R40-L09-Q4 | chaining-value difference | table/entry packing | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Specify and test a semi-free or two-block CV boundary. |
| R40-L09-Q5 | chaining-value difference | success-bound slack | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Specify and test a semi-free or two-block CV boundary. |
| R40-L09-Q6 | chaining-value difference | premise/evidence | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Specify and test a semi-free or two-block CV boundary. |
| R40-L09-Q7 | chaining-value difference | preprocessing/advice | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Specify and test a semi-free or two-block CV boundary. |
| R40-L09-Q8 | chaining-value difference | rival/board | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Specify and test a semi-free or two-block CV boundary. |
| R40-L09-Q9 | chaining-value difference | applied/unapplied levers | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Specify and test a semi-free or two-block CV boundary. |
| R40-L09-Q10 | chaining-value difference | judge finding/status | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Specify and test a semi-free or two-block CV boundary. |
| R40-L09-Q11 | chaining-value difference | neighbor transfer | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Specify and test a semi-free or two-block CV boundary. |
| R40-L09-Q12 | chaining-value difference | structural specialness | COMPUTED finite / LOCAL_ONLY | CV changes finite state only; schedule tail is invariant; full two-block structure remains open | Specify and test a semi-free or two-block CV boundary. |
| R40-L09-Q13 | chaining-value difference | step program | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Specify and test a semi-free or two-block CV boundary. |
| R40-L09-Q14 | chaining-value difference | DP/recovery | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Specify and test a semi-free or two-block CV boundary. |
| R40-L10-Q1 | induced rows 27/32/33 | cost ledger | COMPUTED finite | Owned replay reports exact induced-row values and row-local state effects; no charge inference | Verify all induced rows in a signed/modular schedule, not just XOR closure. |
| R40-L10-Q2 | induced rows 27/32/33 | dispatch/control charge | COMPUTED finite | Frozen row-local replay only; no signed dispatch charge | Verify all induced rows in a signed/modular schedule, not just XOR closure. |
| R40-L10-Q3 | induced rows 27/32/33 | memory peak/drain | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Verify all induced rows in a signed/modular schedule, not just XOR closure. |
| R40-L10-Q4 | induced rows 27/32/33 | table/entry packing | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Verify all induced rows in a signed/modular schedule, not just XOR closure. |
| R40-L10-Q5 | induced rows 27/32/33 | success-bound slack | LOCAL_ONLY | `research/cloud_jobs/API2070_answer.md:3-27` computes closure, finite kernels, and 0/65536 modular samples; `:26-27` says probability is not established | Obtain a real signed/modular success bound; finite closure/sample gives no score credit. |
| R40-L10-Q6 | induced rows 27/32/33 | premise/evidence | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Verify all induced rows in a signed/modular schedule, not just XOR closure. |
| R40-L10-Q7 | induced rows 27/32/33 | preprocessing/advice | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Verify all induced rows in a signed/modular schedule, not just XOR closure. |
| R40-L10-Q8 | induced rows 27/32/33 | rival/board | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Verify all induced rows in a signed/modular schedule, not just XOR closure. |
| R40-L10-Q9 | induced rows 27/32/33 | applied/unapplied levers | COMPUTED finite | Zeroing a nonzero induced row changes model-Z state; frozen tail is unchanged and message-level release remains open | Verify all induced rows in a signed/modular schedule, not just XOR closure. |
| R40-L10-Q10 | induced rows 27/32/33 | judge finding/status | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Verify all induced rows in a signed/modular schedule, not just XOR closure. |
| R40-L10-Q11 | induced rows 27/32/33 | neighbor transfer | COMPUTED finite | Supplied row values and frozen counterfactuals reproduce the local induced-row behavior; transfer remains unproved | Verify all induced rows in a signed/modular schedule, not just XOR closure. |
| R40-L10-Q12 | induced rows 27/32/33 | structural specialness | COMPUTED finite / LOCAL_ONLY | Rank-5 has all three induced rows nonzero while preserving XOR late zero; six-word control has W32=0; no modular promotion | Verify all induced rows in a signed/modular schedule, not just XOR closure. |
| R40-L10-Q13 | induced rows 27/32/33 | step program | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Verify all induced rows in a signed/modular schedule, not just XOR closure. |
| R40-L10-Q14 | induced rows 27/32/33 | DP/recovery | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Verify all induced rows in a signed/modular schedule, not just XOR closure. |
| R40-L11-Q1 | release sets | cost ledger | COMPUTED finite | Exact support columns, target-map rank/kernel, and three supplied release vectors replayed; no charge inference | Obtain a signed/modular characteristic before pricing. |
| R40-L11-Q2 | release sets | dispatch/control charge | COMPUTED finite | The owned schedule map has exact finite target dimensions; no judge charge is inferred | Obtain a signed/modular characteristic before pricing. |
| R40-L11-Q3 | release sets | memory peak/drain | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Choose a concrete release set and run the owned schedule/state test. |
| R40-L11-Q4 | release sets | table/entry packing | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Choose a concrete release set and run the owned schedule/state test. |
| R40-L11-Q5 | release sets | success-bound slack | LOCAL_ONLY | `research/grok/work/G_backcut_2/ANSWER.md:51-65` gives the 2^16 modular lift run and 0/65536 for each release mask; `:90-94` keeps existence open | Obtain a global modular rate or characteristic; sample is diagnostic only. |
| R40-L11-Q6 | release sets | premise/evidence | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Choose a concrete release set and run the owned schedule/state test. |
| R40-L11-Q7 | release sets | preprocessing/advice | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Choose a concrete release set and run the owned schedule/state test. |
| R40-L11-Q8 | release sets | rival/board | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Choose a concrete release set and run the owned schedule/state test. |
| R40-L11-Q9 | release sets | applied/unapplied levers | COMPUTED finite | Pair releases change the old kernel dimension from 0 to 32; no applied score lever is established | Obtain a signed/modular characteristic before pricing. |
| R40-L11-Q10 | release sets | judge finding/status | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Choose a concrete release set and run the owned schedule/state test. |
| R40-L11-Q11 | release sets | neighbor transfer | COMPUTED finite / LOCAL_ONLY | Exact finite pair-release kernels and target-zero tails are reproduced; no r39/r41 transfer | Validate one release kernel under signed/modular state rules. |
| R40-L11-Q12 | release sets | structural specialness | COMPUTED finite / LOCAL_ONLY | Exact rank/kernel jump and nonzero model-Z endpoint states are reproduced | Signed modular/full-state embedding remains open. |
| R40-L11-Q13 | release sets | step program | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Choose a concrete release set and run the owned schedule/state test. |
| R40-L11-Q14 | release sets | DP/recovery | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Choose a concrete release set and run the owned schedule/state test. |
| R40-L12-Q1 | claw placement | cost ledger | COMPUTED finite | Exact local placement, absorbed-row, tail, and setup figures reconciled; no r40 charge claim | Obtain a new r40 trail before pricing. |
| R40-L12-Q2 | claw placement | dispatch/control charge | COMPUTED finite | Existing row-16/ideal second-claw setup terms are recorded; no new dispatch ledger | Obtain a new r40 characteristic before pricing. |
| R40-L12-Q3 | claw placement | memory peak/drain | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Measure a concrete alternative claw placement with the charged ledger. |
| R40-L12-Q4 | claw placement | table/entry packing | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Measure a concrete alternative claw placement with the charged ledger. |
| R40-L12-Q5 | claw placement | success-bound slack | LOCAL_ONLY | `research/cloud_jobs/API2069_answer.md:3-17` reports the finite 39/40-step fibre/claw counts (40-step CV seed 763, F8=0) and no collision; full rate not run | Obtain a full-family charged success bound for an alternative r40 placement. |
| R40-L12-Q6 | claw placement | premise/evidence | LOCAL_ONLY | XOR-linear or finite-window source only; not a full signed/modular proof | Measure a concrete alternative claw placement with the charged ledger. |
| R40-L12-Q7 | claw placement | preprocessing/advice | OPEN | No nonduplicate permitted run in the listed source set; next check is specified below | Measure a concrete alternative claw placement with the charged ledger. |
| R40-L12-Q8 | claw placement | rival/board | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Measure a concrete alternative claw placement with the charged ledger. |
| R40-L12-Q9 | claw placement | applied/unapplied levers | COMPUTED finite | W39, cross-block, W17 barriers and ideal second-claw ceiling are reconciled; no applied score lever | Obtain a new separable r40 claw coordinate. |
| R40-L12-Q10 | claw placement | judge finding/status | EMPTY | No r40 judge/rival row in the listed source set; record is an empty square, not a claim | Measure a concrete alternative claw placement with the charged ledger. |
| R40-L12-Q11 | claw placement | neighbor transfer | COMPUTED finite / LOCAL_ONLY | Existing r39 row-16 placement transfers only as local data; r40 W39/cross-block barriers do not transfer a valid characteristic | Validate a new r40 trail under signed/modular rules. |
| R40-L12-Q12 | claw placement | structural specialness | COMPUTED finite / LOCAL_ONLY | sigma0 bijection, nonzero W39/W40, and >=58-bit shifted floor are exact finite structural facts | Signed modular/full-state embedding remains open. |
| R40-L12-Q13 | claw placement | step program | BLOCKED / OPEN | No owned signed r40 step-program artifact | Obtain a new r40 characteristic and step program. |
| R40-L12-Q14 | claw placement | DP/recovery | BLOCKED / OPEN | No alternative-placement recovery or charged-ledger artifact | Obtain a new r40 characteristic and complete ledger. |
| R40-L13-Q1 | accounting fields | cost ledger | COMPUTED finite / OPEN r40 full | `C39=2812`; PR554/PR574 walk rows exact; no C(40) or complete r40 ledger | Build a valid r40 characteristic and complete charged manifest. |
| R40-L13-Q2 | accounting fields | dispatch/control charge | COMPUTED finite / OPEN r40 full | r39 `40.1/22.4/26.9/10.4%` program breakdown and `50.9` filter ops/claw | Emit and count the r40 dispatch/control program. |
| R40-L13-Q3 | accounting fields | memory peak/drain | COMPUTED finite / OPEN r40 full | r39 exact totals `1,047,548`/`1,047,892` B; r40 peak absent | Produce r40 live-buffer/peak manifest. |
| R40-L13-Q4 | accounting fields | table/entry packing | COMPUTED finite / OPEN r40 full | r39 table, instruction, register, queue, advice and code components enumerated | Produce r40 entry/code packing manifest. |
| R40-L13-Q5 | accounting fields | success-bound slack | LOCAL_ONLY | r39 success `>=0.39-2 exp(-2^17.9)` and Hoeffding budget | Obtain an r40 tail/success certificate. |
| R40-L13-Q6 | accounting fields | premise/evidence | LOCAL_ONLY | r39 word-RAM/claw/tail/advice premise inventory only | Obtain organizer-scale r40 evidence. |
| R40-L13-Q7 | accounting fields | preprocessing/advice | COMPUTED finite / OPEN r40 full | r39 advice `160 B`, construction cap `2^36` compressions and `2^16 B` resident | Price r40 advice construction. |
| R40-L13-Q8 | accounting fields | rival/board | EMPTY | No r40 judge/rival accounting row in the listed source set | A relevant r40 judge/rival row. |
| R40-L13-Q9 | accounting fields | applied/unapplied levers | COMPUTED finite / conditional | generic `124.2613`; ideal second-claw `~124.2`; shifted floor `>=58` bits | Obtain a valid r40 trail before applying a score lever. |
| R40-L13-Q10 | accounting fields | judge finding/status | EMPTY | No r40 judge/ruling accounting row in the listed source set | A relevant r40 judge/ruling row. |
| R40-L13-Q11 | accounting fields | neighbor transfer | LOCAL_ONLY | r39 accounting transfers only as source data; C(40), success and program require remeasurement | Valid r40 characteristic and remeasured ledger. |
| R40-L13-Q12 | accounting fields | structural specialness | COMPUTED finite / OPEN cost | r40 unchanged-claw probability is exactly zero; shifted skeleton floor is `>=58` bits | New valid r40 support/characteristic. |
| R40-L13-Q13 | accounting fields | step program | COMPUTED finite / OPEN r40 | r39 PR574 `723` records/`3.65` compressions per claw; PR554 `955`/`4.40` | Emit/count the r40 step program. |
| R40-L13-Q14 | accounting fields | DP/recovery | LOCAL_ONLY | r39 stage-1 `1327.1`, stage-2 `893.8` lane evaluations and `R+6B` budget terms | Price r40 DP/recovery/final checks. |

## L13 bounded execution (owned static/source arithmetic)

The owned run is `research/luna_dig/task35_l13_accounting.py`, with report
`research/luna_dig/TASK35_L13_ACCOUNTING_20261021.md`.  It computes the exact
r39 arithmetic and reconciles each Q1-Q14 field.  It does not execute a
participant program or nldtool.  The missing r40 C(40), valid full
characteristic, complete dispatch/memory/packing, success, and recovery rows
are deliberately left OPEN; no r40 score is promoted.

| Q | status | bounded result |
|---|---|---|
| Q1 | COMPUTED finite / OPEN r40 | `C39=2812=72*39+4`; no `C(40)` |
| Q2 | COMPUTED finite / OPEN r40 | r39 program breakdown and `50.9` filter ops/claw |
| Q3 | COMPUTED finite / OPEN r40 | r39 `1,047,548`/`1,047,892` B; MiB slack `1,028`/`684` |
| Q4 | COMPUTED finite / OPEN r40 | r39 table/code/register/advice packing enumerated |
| Q5 | LOCAL_ONLY | r39 success bound only; r40 success law absent |
| Q6 | LOCAL_ONLY | r39 premises inventoried; no r40 organizer evidence |
| Q7 | COMPUTED finite / OPEN r40 | `160 B` advice; `2^36` preprocessing cap; `2^16 B` resident |
| Q8 | EMPTY | no listed r40 judge/rival accounting row |
| Q9 | COMPUTED finite / conditional | ideal `~124.2` ceiling and `>=58`-bit shifted floor |
| Q10 | EMPTY | no listed r40 judge/ruling accounting row |
| Q11 | LOCAL_ONLY | r39 transfer is data only; r40 needs remeasurement |
| Q12 | COMPUTED finite / OPEN cost | r40 unchanged-claw probability 0; no cost supplied |
| Q13 | COMPUTED finite / OPEN r40 | r39 `723`/`3.65` and `955`/`4.40` program rows |
| Q14 | LOCAL_ONLY | r39 DP/recovery rows only; r40 recovery absent |

## Run ledger and non-promotion notes

1. Reproduced with python research/grok/work/G_r40_support_zero/linmodel.py: sigma0/sigma1 rank 32; part-1 target map rank 96/kernel 416; part-2 rank 352/kernel 160; no codeword of weight <=4 in either target map. This is an exact XOR-linear run.
2. Existing G_river_2/3/4/5/6/7/8/ANSWER.md and G_river_5/exact_tail.exe records establish the listed exact finite tail values. A bounded local invocation of exact_tail.exe tail 19 41 1000 was started and stopped before a result; it does not add evidence. The existing exact result 247 for (s=19,N=41) remains the cited result.
3. NLDTOOL_1021.md and its logs are read-only evidence. The full signed control is COMPUTED; join16/stage1 timeouts are NOT FOUND, not UNSAT; stage2 initial contradictions are diagnostic for the specified pins. Pre-FIX2 logs are VOID by the task rule.
4. No participant code, nldtool run, package, staging, filing, or submission was performed by this grid build.

## L01 bounded execution (Task 35 continuation, 2026-10-21)

Owned self-contained replay: `research/luna_dig/task34_l01_modular_audit.py`; report: `research/luna_dig/TASK34_L01_MODULAR_AUDIT_20261021.md`.  The exact weight-30 XOR-kernel vector from `G_r40_support_zero/ANSWER.md` has XOR W39/W40/W41 = `00000000 00000000 00000000`, but ordinary modular schedule values `8c5b0864 00f0e3ba f29a808c` (W39/W40/W41), with W42 `64dabf65`.  Its wordwise modular negative gives `8027b7bb 5a386da1 206c6469` and W42 `d9510ddc`.  This is a finite schedule-only diagnostic; it does not lift to a modular zero and does not test compression state, cost, packing, advice, neighbor transfer, or recovery.

| L01 cell | bounded disposition | evidence / blocker |
|---|---|---|
| Q1 | COMPUTED (unchanged) | Static schedule/control record; replay is supporting finite evidence. |
| Q2 | BLOCKED / OPEN | No owned dispatch/control ledger in this replay. |
| Q3 | BLOCKED / OPEN | No memory-peak or release accounting path. |
| Q4 | BLOCKED / OPEN | No table/entry packing artifact. |
| Q5 | BLOCKED / LOCAL_ONLY | One finite negative modular replay cannot establish a success bound. |
| Q6 | LOCAL_ONLY | Exact schedule-only replay; full signed/state premise remains missing. |
| Q7 | BLOCKED / OPEN | No preprocessing/advice experiment. |
| Q8 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q9 | COMPUTED (unchanged) | Static applied/unapplied record; no promotion from the replay. |
| Q10 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q11 | BLOCKED / LOCAL_ONLY | No neighbor-transfer experiment. |
| Q12 | COMPUTED (unchanged) | Static structural record; modular replay is supporting only. |
| Q13 | BLOCKED / OPEN | No owned step-program/recovery artifact. |
| Q14 | BLOCKED / OPEN | No owned DP/recovery artifact. |

## L02 bounded execution (Task 35 continuation, 2026-10-21)

Owned replay: `research/luna_dig/task35_l02_join_replay.py`; report: `research/luna_dig/TASK35_L02_JOIN_REPLAY_20261021.md`.  The self-contained XOR-linear schedule expansion reproduces the published exact join-window minima: 217 at `(s=17,N=40)` over 21 allowed words, and 230 at `(s=18,N=40)` and `(s=18,N=41)` over 22 allowed words.  These are finite XOR/window results; no modular lift, full state, or score claim follows.

| L02 cell | bounded disposition | evidence / blocker |
|---|---|---|
| Q1 | COMPUTED (unchanged) | Exact tail-window weight replay: 217 and 230. |
| Q2 | COMPUTED (unchanged) | Exact allowed-window cardinalities 21/22; no dispatch-cost inference. |
| Q3 | BLOCKED / OPEN | No memory/drain ledger in this replay. |
| Q4 | BLOCKED / OPEN | No table/entry packing artifact. |
| Q5 | LOCAL_ONLY | Exact finite XOR minima; no global success bound. |
| Q6 | LOCAL_ONLY | Source vectors/windows replayed; modular/state lift remains open. |
| Q7 | BLOCKED / OPEN | No preprocessing/advice experiment. |
| Q8 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q9 | COMPUTED (unchanged) | Finite join-window values reproduced; no applied-lever promotion. |
| Q10 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q11 | COMPUTED finite-window | Replay confirms finite join-window behavior; full neighbor transfer remains untested. |
| Q12 | COMPUTED finite | Structural finite replay only; no modular promotion. |
| Q13 | BLOCKED / OPEN | No owned step-program artifact. |
| Q14 | COMPUTED finite | Tail-window replay only; recovery remains untested. |

## S046 fixed-vector lift disposition (server run, 2026-10-21)

The S046 kissat expansion reports the lightest pinned XOR-model support at join
steps 12, 13, 14, 15, and 16 as UNSATISFIABLE for the fixed vector, while the
r39-pattern control is SATISFIABLE.  Accordingly, the ten fixed-vector lift
squares below are EMPTY in this grid (there is no surviving fixed-vector
characteristic).  This is server evidence, not an owned run.  It does not
close the distinct support-only question: arbitrary values on the support stay
OPEN pending S047.

| lever | join | fixed-vector lift | evidence | remaining question |
|---|---:|---|---|---|
| L01 message-difference support | 12 | EMPTY | `historical-sources/Luna_Orders/answers/S046/runs/*.out` (UNSAT) | arbitrary support values: OPEN pending S047 |
| L01 message-difference support | 13 | EMPTY | `historical-sources/Luna_Orders/answers/S046/runs/*.out` (UNSAT) | arbitrary support values: OPEN pending S047 |
| L01 message-difference support | 14 | EMPTY | `historical-sources/Luna_Orders/answers/S046/runs/*.out` (UNSAT) | arbitrary support values: OPEN pending S047 |
| L01 message-difference support | 15 | EMPTY | `historical-sources/Luna_Orders/answers/S046/runs/*.out` (UNSAT) | arbitrary support values: OPEN pending S047 |
| L01 message-difference support | 16 | EMPTY | `historical-sources/Luna_Orders/answers/S046/runs/*.out` (UNSAT) | arbitrary support values: OPEN pending S047 |
| L02 join step | 12 | EMPTY | `historical-sources/Luna_Orders/answers/S046/runs/*.out` (UNSAT) | arbitrary support values: OPEN pending S047 |
| L02 join step | 13 | EMPTY | `historical-sources/Luna_Orders/answers/S046/runs/*.out` (UNSAT) | arbitrary support values: OPEN pending S047 |
| L02 join step | 14 | EMPTY | `historical-sources/Luna_Orders/answers/S046/runs/*.out` (UNSAT) | arbitrary support values: OPEN pending S047 |
| L02 join step | 15 | EMPTY | `historical-sources/Luna_Orders/answers/S046/runs/*.out` (UNSAT) | arbitrary support values: OPEN pending S047 |
| L02 join step | 16 | EMPTY | `historical-sources/Luna_Orders/answers/S046/runs/*.out` (UNSAT) | arbitrary support values: OPEN pending S047 |

The corresponding append-only CELLS records are
`S256-R40-L01-J12-PINNED-XOR-LIFT-S046-20261021` through the L02/J16
record.  They use `OPEN` with an `EMPTY in grid` number because SCHEMA.md has
no `EMPTY` status; no score credit is claimed.

## L03 bounded execution (Task 35 continuation, 2026-10-21)

Owned replay: `research/luna_dig/task35_l03_late_constraints.py`; report: `research/luna_dig/TASK35_L03_LATE_CONSTRAINTS_20261021.md`.  The published weight-25 three-target vector has XOR `W39..W42 = 00000000 00000000 00000000 6a70373c`; an owned Gaussian-elimination dependency gives a weight-67 vector with all four W39..W42 exactly zero.  The published entry-34 late-cancellation pattern instead has `W39..W42 = 44280480 00000000 00000000 00000001` and returns the model-Z state to zero after step 42.  Its clean 16-word schedule realization remains OPEN.

| L03 cell | bounded disposition | evidence / blocker |
|---|---|---|
| Q1 | COMPUTED (unchanged) | Exact three-target/four-target schedule comparison. |
| Q2 | COMPUTED (unchanged) | Finite schedule/state model arithmetic; no dispatch ledger change. |
| Q3 | BLOCKED / OPEN | No memory/drain ledger. |
| Q4 | BLOCKED / OPEN | No table/entry packing artifact. |
| Q5 | BLOCKED / OPEN | No global success bound from finite model comparison. |
| Q6 | LOCAL_ONLY | Exact XOR/model-Z comparison; signed/modular premise missing. |
| Q7 | BLOCKED / OPEN | No preprocessing/advice experiment. |
| Q8 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q9 | COMPUTED (unchanged) | Applied/unapplied finite comparison only. |
| Q10 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q11 | COMPUTED finite | Late-cancellation state transition reproduced; full transfer remains open. |
| Q12 | COMPUTED finite | Structural contrast reproduced; no modular promotion. |
| Q13 | BLOCKED / OPEN | No owned step-program realization. |
| Q14 | BLOCKED / OPEN | No owned recovery/ledger artifact. |

## L04 bounded execution (Task 35 continuation, 2026-10-21)

Owned self-contained replay: `research/luna_dig/task35_l04_tail_windows.py`; report: `research/luna_dig/TASK35_L04_TAIL_WINDOWS_20261021.md`. The supplied G_river tail vectors reproduce all 18 listed `(s,N)` cases exactly, with allowed-window sizes and weights: `(17,40)=21/217`, `(18,40/41)=22/230`, `(19,41/42)=23/247`, `(20,41)=24/44`, `(20,42)=24/258`, `(21,41/42)=25/51`, `(22,41/42)=26/64`, `(23,41/42)=27/75`, `(24,41/42)=28/86`, `(25,41/42)=29/100`, and `(26,42)=30/115`. Every case matched the expected weight and had `forced_nonzero=0`. These are exact finite XOR/window replays; density is bit-popcount density, not success probability. Signed/modular state, compression characteristic, release/neighbor transfer, charged ledger, and score remain unproved.

| L04 cell | bounded disposition | evidence / blocker |
|---|---|---|
| Q1 | COMPUTED (unchanged) | Exact supplied tail-vector/window replay; all 18 cases match. |
| Q2 | COMPUTED (unchanged) | Allowed-window cardinalities 21 through 30 are reproduced; no dispatch-cost inference. |
| Q3 | BLOCKED / OPEN | No memory/drain ledger in the owned replay. |
| Q4 | BLOCKED / OPEN | No table/entry packing artifact. |
| Q5 | LOCAL_ONLY | Finite XOR/window weights only; no global success bound. |
| Q6 | LOCAL_ONLY | XOR-linear schedule replay only; signed/modular/state lift remains open. |
| Q7 | BLOCKED / OPEN | No preprocessing/advice experiment. |
| Q8 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q9 | COMPUTED (unchanged) | Finite tail-window values are reproduced; no applied-lever promotion. |
| Q10 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q11 | COMPUTED finite | Window replay confirms the supplied finite tail behavior; full neighbor transfer remains untested. |
| Q12 | COMPUTED finite | Structural finite replay only; no modular promotion. |
| Q13 | BLOCKED / OPEN | No owned step-program artifact. |
| Q14 | COMPUTED finite | Tail-window replay only; recovery/charged ledger remains untested. |

## L05 bounded execution (Task 35 continuation, 2026-10-21)

Owned self-contained replay: `research/luna_dig/task35_l05_cluster_start.py`; report: `research/luna_dig/TASK35_L05_CLUSTER_START_20261021.md`. All 18 established L04 tail vectors re-expanded with cluster start W0 and their cited finite weights. Four full-kernel condition-free examples replayed starts W11/W13/W14/W15 with weights 146/162/203/188. Five G_river_6 later-start candidates replayed start W9 with W0..W40 weights 319/321/323/326/329. These are exact finite XOR-linear schedule observations; full state, modular transfer, release/claw cost, ledger, and score remain open.

| L05 cell | bounded disposition | evidence / blocker |
|---|---|---|
| Q1 | COMPUTED (unchanged) | Finite schedule replay gives exact cluster starts and window weights. |
| Q2 | BLOCKED / OPEN | No dispatch/control ledger comparison for early versus later starts. |
| Q3 | BLOCKED / OPEN | No memory/drain ledger comparison. |
| Q4 | BLOCKED / OPEN | No table/entry packing artifact. |
| Q5 | COMPUTED finite / LOCAL_ONLY | Later-start vectors exist, but no full success-bound improvement is proved. |
| Q6 | LOCAL_ONLY | XOR-linear schedule support only; signed/modular/state premise missing. |
| Q7 | BLOCKED / OPEN | No preprocessing/advice experiment. |
| Q8 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q9 | COMPUTED finite | Cluster-start cases and supplied weights are reproduced; no applied-lever promotion. |
| Q10 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q11 | COMPUTED finite / LOCAL_ONLY | Tail/full-kernel comparison is finite; cross-round transfer remains untested. |
| Q12 | COMPUTED finite | Start-word regimes and finite boundary behavior are reproduced; no modular promotion. |
| Q13 | BLOCKED / OPEN | No owned step-program artifact. |
| Q14 | COMPUTED finite / LOCAL_ONLY | Finite schedule weights only; no recovery or charged-ledger result. |

## L06 bounded execution (Task 35 continuation, 2026-10-21)

Owned self-contained replay: `research/luna_dig/task35_l06_early_word.py`; report: `research/luna_dig/TASK35_L06_EARLY_WORD_20261021.md`. Starting from the published G_river_6 later-start rank-5 vector, the baseline has W0..W8=0, XOR W39..W42=0, modular W39..W42=`1cf7d717 d6749855 5bdf4d2e 7abcfda5`, and finite W0..W40 weight 329. W0 xor `00000001` gives XOR late=`a8ea2014 3bbee2bb 130001c9 db4a1b2c`, modular late=`71f4d533 afd16a26 fab49ac5 7b38f051`, weight 372. W8 xor `00000001` gives XOR late=`b846ec18 298aa111 fb2991aa 1b50f6c3`, modular late=`4d40abcf dff5d09e 5388480a 6bf43d73`, weight 391. This is finite schedule evidence only; full state, release/claw, ledger, recovery, and score remain open.

| L06 cell | bounded disposition | evidence / blocker |
|---|---|---|
| Q1 | COMPUTED (unchanged) | Exact finite XOR/modular schedule outputs for baseline and W0/W8 perturbations. |
| Q2 | BLOCKED / OPEN | No dispatch/control ledger comparison. |
| Q3 | BLOCKED / OPEN | No memory/drain ledger comparison. |
| Q4 | BLOCKED / OPEN | No table/entry packing artifact. |
| Q5 | LOCAL_ONLY | Finite perturbation changes do not establish a global success bound. |
| Q6 | LOCAL_ONLY | XOR/modular schedule only; full signed/state premise remains missing. |
| Q7 | BLOCKED / OPEN | No preprocessing/advice experiment. |
| Q8 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q9 | COMPUTED finite | Early-prefix perturbation effects are reproduced; no applied-lever promotion. |
| Q10 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q11 | COMPUTED finite / LOCAL_ONLY | Baseline-versus-perturbation schedule comparison only; transfer remains untested. |
| Q12 | LOCAL_ONLY | XOR/modular finite contrast; no full state or modular characteristic. |
| Q13 | BLOCKED / OPEN | No owned step-program artifact. |
| Q14 | BLOCKED / OPEN | No recovery or charged-ledger artifact. |

## L07 bounded execution (Task 35 continuation, 2026-10-21)

Owned self-contained replay: `research/luna_dig/task35_l07_sign_choices.py`; report: `research/luna_dig/TASK35_L07_SIGN_CHOICES_20261021.md`. Positive and wordwise modular-negative orientations of the published support-zero weight-30 vector and later-start rank-5 vector were replayed. No orientation made all four ordinary modular late words zero: support-zero `+` modular late=`8c5b0864 00f0e3ba f29a808c 64dabf65`, support-zero wordwise `-`=`8027b7bb 5a386da1 206c6469 d9510ddc`, rank-5 `+`=`1cf7d717 d6749855 5bdf4d2e 7abcfda5`, and rank-5 wordwise `-`=`5eab4644 35a7be0c 5f1db026 36fe08c8`. XOR rank-5 `+` late words remain zero; its modular schedule does not. Full state, signed search, ledger, recovery, and score remain open.

| L07 cell | bounded disposition | evidence / blocker |
|---|---|---|
| Q1 | COMPUTED (unchanged) | Exact finite XOR/modular outputs for two vectors and both orientations. |
| Q2 | COMPUTED finite | Schedule recurrence comparison only; no new charged dispatch ledger. |
| Q3 | BLOCKED / OPEN | No memory/drain ledger comparison. |
| Q4 | BLOCKED / OPEN | No table/entry packing artifact. |
| Q5 | LOCAL_ONLY | Tested orientations give no modular late-zero lift; no global success bound. |
| Q6 | COMPUTED finite / LOCAL_ONLY | Sign-choice schedule evidence only; full signed/state premise missing. |
| Q7 | COMPUTED (unchanged) | No new preprocessing/advice conclusion from this replay. |
| Q8 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q9 | COMPUTED finite | Sign orientations and late-word outcomes are reproduced; no applied-lever promotion. |
| Q10 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q11 | LOCAL_ONLY | Finite sign comparison only; transfer remains untested. |
| Q12 | COMPUTED finite | XOR/modular orientation contrast reproduced; no modular characteristic promotion. |
| Q13 | BLOCKED / OPEN | No owned step-program artifact. |
| Q14 | BLOCKED / OPEN | No recovery or charged-ledger artifact. |

## L08 bounded execution (Task 35 continuation, 2026-10-21)

Owned self-contained replay: `research/luna_dig/task35_l08_state_rows.py`; report: `research/luna_dig/TASK35_L08_STATE_ROWS_20261021.md`; cell record: `research/luna_dig/TASK35_L08_STATE_RECORD.json`. The model-Z XOR state recurrence was run on the published three-target base, the four-target schedule-kernel witness, and the G_river_6 later-start rank-5 vector. Their final A..H states were respectively `eb4adc5c aea8eb7f 9b913839 d1cc4c4a f10c8bd0 589b1b07 2a2eac40 b68d60cb`, `c03b3059 13e61b99 97ddac7f 9c4c5472 be609334 c6555456 dbdcaef3 707b0c03`, and `1b80f987 96877ea1 7fe32a43 9f4db434 d928be3a 5d86d380 29047b7d c95a57c8`. None has A=E=0 or an all-zero state. Releasing A/E therefore changes only the endpoint predicate/projection; it does not change the recurrence, schedule, or finite tail. The L03 state-only cancellation control reaches all-zero model-Z state, but is not a 16-word message realization. No nldtool, participant code, signed/modular compressor, ledger, or score path was run.

| L08 cell | bounded disposition | evidence / blocker |
|---|---|---|
| Q1 | COMPUTED finite | Exact model-Z A/E projection replay for three supplied vectors. |
| Q2 | BLOCKED / OPEN | No dispatch/control charge for a released-row characteristic. |
| Q3 | BLOCKED / OPEN | No memory/drain ledger comparison. |
| Q4 | BLOCKED / OPEN | No table/entry packing artifact. |
| Q5 | BLOCKED / OPEN | Endpoint projection does not provide a global success bound. |
| Q6 | LOCAL_ONLY | Model-Z/XOR premise only; signed/full-state lift is missing. |
| Q7 | BLOCKED / OPEN | No preprocessing/advice experiment. |
| Q8 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q9 | COMPUTED finite | Released projection is exact and unchanged by removing A/E checks. |
| Q10 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q11 | BLOCKED / OPEN | No neighbor/release transfer beyond the fixed-vector projection. |
| Q12 | LOCAL_ONLY | State-only cancellation control is exact in model Z, but not message-realizable. |
| Q13 | BLOCKED / OPEN | No owned signed step-program realization. |
| Q14 | BLOCKED / OPEN | No recovery or charged-ledger artifact. |

## L09 bounded execution (Task 35 continuation, 2026-10-21)

Owned self-contained replay: `research/luna_dig/task35_l09_cv_delta.py`; report: `research/luna_dig/TASK35_L09_CV_DELTA_20261021.md`; cell record: `research/luna_dig/TASK35_L09_CV_RECORD.json`. Three supplied XOR message vectors were replayed under free-start zero CV, an explicit semi-free E-bit proxy `E=0x10000000`, and the API2052 r39-output proxy `(A,E)=(0x406266c0,0x40222e40)`. For each fixed message, the XOR W39..W42 tail is invariant across CV modes; the initial CV delta changes only the model-Z state trajectory. No tested state is all-zero. The two-block mode is therefore a finite entry-boundary diagnostic, not a first-block near-collision or feed-forward proof.

| L09 cell | bounded disposition | evidence / blocker |
|---|---|---|
| Q1 | COMPUTED finite | Exact free/semi-free/two-block CV proxy replay and state42 outputs. |
| Q2 | BLOCKED / OPEN | No dispatch/control charge for a valid two-block construction. |
| Q3 | BLOCKED / OPEN | No memory/drain ledger comparison. |
| Q4 | BLOCKED / OPEN | No table/entry packing artifact. |
| Q5 | BLOCKED / OPEN | Finite CV boundary replay gives no global success bound. |
| Q6 | LOCAL_ONLY | Model-Z/XOR recurrence and boundary proxies only; signed/full-state premise missing. |
| Q7 | BLOCKED / OPEN | No preprocessing/advice experiment for a first-block bridge. |
| Q8 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q9 | BLOCKED / OPEN | No applied two-block lever or valid characteristic. |
| Q10 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q11 | BLOCKED / OPEN | No feed-forward/neighbor transfer proof. |
| Q12 | COMPUTED finite / LOCAL_ONLY | CV changes state only; the XOR schedule tail is unchanged, but full structural transfer is open. |
| Q13 | BLOCKED / OPEN | No owned signed two-block step program. |
| Q14 | BLOCKED / OPEN | No first-block cost, recovery, or charged-ledger artifact. |

## L10 bounded execution (Task 35 continuation, 2026-10-21)

Owned self-contained replay: `research/luna_dig/task35_l10_induced_rows.py`; report: `research/luna_dig/TASK35_L10_INDUCED_ROWS_20261021.md`; cell record: `research/luna_dig/TASK35_L10_INDUCED_RECORD.json`. Four supplied XOR vectors were re-expanded and their W27/W32/W33 values recorded. A row-local counterfactual then replaced one or all of those schedule inputs with zero in the model-Z state recurrence. The frozen schedule's W39..W42 remains unchanged, while the state trajectory changes whenever the replaced induced row is nonzero. This is a finite diagnostic only: an independently zeroed expanded row is not automatically realizable by a 16-word message.

| L10 cell | bounded disposition | evidence / blocker |
|---|---|---|
| Q1 | COMPUTED finite | Exact W27/W32/W33 values and model-Z state effects for four supplied vectors. |
| Q2 | COMPUTED finite | Row-local recurrence comparison only; no signed dispatch charge. |
| Q3 | BLOCKED / OPEN | No induced-row memory/drain ledger. |
| Q4 | BLOCKED / OPEN | No induced-row table/packing artifact. |
| Q5 | BLOCKED / OPEN | Finite row-local replay is not a global success bound. |
| Q6 | LOCAL_ONLY | XOR/model-Z arithmetic only; modular/full-state premise is missing. |
| Q7 | BLOCKED / OPEN | No preprocessing/advice experiment. |
| Q8 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q9 | COMPUTED finite | Zeroing a nonzero induced row changes state; frozen tail stays fixed and message-level release is open. |
| Q10 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q11 | COMPUTED finite / LOCAL_ONLY | Local induced-row behavior is reproduced; neighbor transfer remains unproved. |
| Q12 | COMPUTED finite / LOCAL_ONLY | Rank-5 has all three induced rows nonzero with XOR late zero; six-word control has W32=0; no modular promotion. |
| Q13 | BLOCKED / OPEN | No owned signed step-program realization. |
| Q14 | BLOCKED / OPEN | No recovery or charged-ledger artifact. |

## L11 bounded execution (Task 35 continuation, 2026-10-21)

Owned self-contained replay: `research/luna_dig/task35_l11_release_sets.py`; report: `research/luna_dig/TASK35_L11_RELEASE_SETS_20261021.md`. A release set T adds message words T to the old `{8,9,10,11,12}` support, and the exact finite target map is `(W24,W26,W39,W40,W41,W42)`. The old support has rank 160 and kernel dimension 0. The three pair releases `{13,14}`, `{13,15}`, and `{14,15}` each have 224 input columns, rank 192, and kernel dimension 32; the three-word release has rank 192/kernel dimension 64. Single-word controls are `{13}:191/1`, `{14}:191/1`, and `{15}:190/2`. The three published lightest pair vectors re-expand with all six target words zero and nonzero induced rows W27/W32/W33. Their exact model-Z state42 values are recorded in the report. This is an XOR/model-Z finite result only: no signed/modular compressor, message-rate, memory, recovery, ledger, or score credit follows.

| L11 cell | bounded disposition | evidence / blocker |
|---|---|---|
| Q1 | COMPUTED finite | Exact support columns, target rank/kernel, and supplied-vector replay; no charged ledger. |
| Q2 | COMPUTED finite | Exact finite schedule-map dimensions only; dispatch/control charge remains unpriced. |
| Q3 | BLOCKED / OPEN | No release-characteristic memory/drain ledger. |
| Q4 | BLOCKED / OPEN | No release-characteristic table/packing artifact. |
| Q5 | BLOCKED / OPEN | XOR kernel does not supply a signed/modular success bound. |
| Q6 | LOCAL_ONLY | Owned XOR schedule plus model-Z replay; signed/full-state premise missing. |
| Q7 | BLOCKED / OPEN | No preprocessing/advice experiment. |
| Q8 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q9 | COMPUTED finite | Pair release changes kernel dimension 0 to 32; no score lever is established. |
| Q10 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q11 | COMPUTED finite / LOCAL_ONLY | Exact finite release kernels and target-zero tails reproduce the local structural change; transfer remains unproved. |
| Q12 | COMPUTED finite / LOCAL_ONLY | Rank/kernel jump and nonzero model-Z endpoint states are exact; modular/full-state embedding remains open. |
| Q13 | BLOCKED / OPEN | No owned signed step-program realization. |
| Q14 | BLOCKED / OPEN | No recovery or charged-ledger artifact. |

## L12 bounded execution (Task 35 continuation, 2026-10-21)

Owned self-contained replay: `research/luna_dig/task35_l12_claw_placements.py`; report: `research/luna_dig/TASK35_L12_CLAW_PLACEMENTS_20261021.md`. The owned XOR check has `sigma0` rank 32 and maps `dW24=03010000` to `dW39=406622c0`, with `dW40=03010000`, under `dW23=dW32=dW37=0`. The local carry-aware artifact separately quotes nonzero `dW39=401e2240` (modular) / `4022e640` (XOR), so the fixed-trail W39 placement is structurally impossible. Existing row-16, R1/R2, cross-block, W17, and ideal-second-claw placement data were reconciled with exact absorbed rows, finite tail weights, and setup effects where available. This is finite/static placement evidence only; signed/modular r40 feasibility, full state, ledger, and score remain open.

| L12 cell | bounded disposition | evidence / blocker |
|---|---|---|
| Q1 | COMPUTED finite | Exact placement, absorbed-row, tail, and setup figures reconciled; no r40 charged ledger. |
| Q2 | COMPUTED finite | Existing row-16 and idealized second-claw setup terms recorded; no new dispatch ledger. |
| Q3 | BLOCKED / OPEN | No alternative-placement memory/drain artifact. |
| Q4 | BLOCKED / OPEN | No alternative-placement table/packing artifact. |
| Q5 | BLOCKED / OPEN | No new r40 trail or success bound. |
| Q6 | LOCAL_ONLY | Owned XOR structural check plus read-only local placement data; signed/full-state lift missing. |
| Q7 | BLOCKED / OPEN | No alternative-placement preprocessing/advice experiment. |
| Q8 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q9 | COMPUTED finite | W39, cross-block, W17 barriers and ideal second-claw ceiling reconciled; no applied score lever. |
| Q10 | EMPTY (unchanged) | No r40 judge/rival row. |
| Q11 | COMPUTED finite / LOCAL_ONLY | Existing row-16 data transfer only; no valid r40 characteristic transfer. |
| Q12 | COMPUTED finite / LOCAL_ONLY | sigma0 bijection, nonzero W39/W40, and >=58-bit shifted floor are finite facts; modular embedding remains open. |
| Q13 | BLOCKED / OPEN | No owned signed r40 step-program artifact. |
| Q14 | BLOCKED / OPEN | No alternative-placement recovery or charged-ledger artifact. |

## Open-cell execution policy

For each OPEN cell, the next permitted test is named in the expanded ledger. The current session does not run nldtool; main session owns any XML rows. Python/local linmodel.py, isd.exe, and exact_tail.exe may be run one at a time under the 20-minute cap, but an existing finite/XOR result is not relabeled as a modular proof.

## Task 38 W1 chart fill (2026-10-21, source answers only)

This pass read the listed `G_river_*`, `G_r40_*`, `G_backcut_2`, `G_watershed_rank`, `G_jointtail_3`, API2062--API2078, and `R40_COMPUTED_CHAIN_1021.md` answer artifacts. No solver, counter, participant code, or new run was used. The five status changes below are finite/conditional evidence only; each cites a completed run and preserves the modular/full-path limitation.

| cell | W1 status after chart fill | exact source/run evidence | interpretation |
|---|---|---|---|
| R40-L01-Q5 | LOCAL_ONLY | `research/cloud_jobs/API2077_answer.md:39`; limitation `:79` | 0/65536 modular samples exist, but the source explicitly calls them a null sample rather than a probability/no-go. |
| R40-L03-Q5 | LOCAL_ONLY | `research/grok/work/G_jointtail_3/ANSWER.md:7-20,26-38,87-112` | Exact model-Z independent-addend carry/Ch-Maj DP (best total 48); dependence on a real SHA-256 trail is not proved. |
| R40-L10-Q5 | LOCAL_ONLY | `research/cloud_jobs/API2070_answer.md:3-27` | Exact finite reaction/kernel tables and 0/65536 modular samples; `:26-27` leaves the true probability open. |
| R40-L11-Q5 | LOCAL_ONLY | `research/grok/work/G_backcut_2/ANSWER.md:51-65,90-94` | Three full weak-kernel scans and 0/65536 lift samples; existence outside the sample remains open. |
| R40-L12-Q5 | LOCAL_ONLY | `research/cloud_jobs/API2069_answer.md:3-17` | Finite fibre/claw counts and 40-step seed-1 count 763/F8=0; full-family rate and charged r40 path were not run. |

The following existing cells are directly reaffirmed (status unchanged) by cited completed runs. They are listed so the chart is auditable without treating a source citation as a new claim:

| cells | retained status | exact source/run evidence |
|---|---|---|
| R40-L01-Q1,Q9,Q12 | COMPUTED | `research/cloud_jobs/API2077_answer.md:5-29`; `research/profiles/R40_COMPUTED_CHAIN_1021.md:5-29` |
| R40-L02-Q9,Q11,Q12 | COMPUTED | `research/grok/work/G_river_10/ANSWER.md:39-53,96-127`; `research/grok/work/G_river_7/ANSWER.md:7-66` |
| R40-L03-Q9,Q11,Q12 | COMPUTED | `research/cloud_jobs/API2070_answer.md:3-22,29-33`; `research/profiles/R40_COMPUTED_CHAIN_1021.md:31-45` |
| R40-L04-Q9,Q11,Q12 | COMPUTED | `research/grok/work/G_river_7/ANSWER.md:7-66`; `research/grok/work/G_river_10/ANSWER.md:39-53` |
| R40-L05-Q5,Q9,Q11,Q12 | COMPUTED / finite | `research/grok/work/G_river_6/ANSWER.md:9-18,40-54`; `research/grok/work/G_river_8/ANSWER.md:5-15,75-89` |
| R40-L06-Q5,Q9,Q11,Q12 | LOCAL_ONLY / COMPUTED finite | `research/grok/work/G_river_8/ANSWER.md:28-46,69-89` |
| R40-L07-Q5,Q6,Q9,Q11,Q12 | LOCAL_ONLY / COMPUTED finite | `research/grok/work/G_river_6/ANSWER.md:56-65`; `research/cloud_jobs/API2077_answer.md:39-40,79` |
| R40-L10-Q9,Q11,Q12 | COMPUTED finite / LOCAL_ONLY | `research/cloud_jobs/API2070_answer.md:3-22,29-33` |
| R40-L11-Q1,Q2,Q9,Q11,Q12 | COMPUTED finite / LOCAL_ONLY | `research/grok/work/G_backcut_2/ANSWER.md:5-15,45-65`; `research/cloud_jobs/API2071_answer.md:3-18` |
| R40-L12-Q1,Q2,Q9,Q11,Q12 | COMPUTED finite / LOCAL_ONLY | `research/cloud_jobs/API2069_answer.md:3-32` |

No OPEN cell was closed from a source that only says “not established,” “unknown,” or “0/65536” without the explicit finite-run qualification. Q2/Q3/Q4/Q7/Q13/Q14 charge cells remain unchanged where the answer files lack a complete r40 charged ledger.


## Ledger once-over pass (2026-10-21 14:48, main session)
Ruling on the template: Q2, Q3, Q4, Q7, Q13, Q14 (dispatch, memory, packing, preprocessing, step program, DP/recovery) are cost-ledger questions that only have content once a 40-step characteristic exists; for L01-L07 and L10-L12 they are N/A-UNTIL-CHARACTERISTIC, not OPEN. That removes 60 of the 93 OPEN cells from the queue without closing anything by reasoning: they reopen automatically the day a characteristic is found. The queue that remains, in order:
1. L11 release sets (decisive): FIX2-template tool runs on the three lightest release vectors. T={13,14} pinned: consistent, 2-hour search running (seed 3). T={13,15} pinned: run now with the FIX2 template (the earlier failure was the void template). T={14,15}: build from lightest_masks.txt and run. Cell closes EMPTY only if all three searches end with a contradiction; "not found at cap" stays OPEN.
2. L09 chaining difference (decisive): zero-difference instances of the published SHA-224 shape fail the check (COMPUTED, two variants); free-input variant consistent, found 0 at 15 min. The two-block route (API2060 recipe) is the remaining branch: cell stays OPEN until a first-block cost is counted.
3. L08 state-row freedom: resolved as a template rule (rows 8..42 free in every instance); the cell is COMPUTED-as-method; no further run.
4. L12 claw placement: fold G_r40_fibre/ANSWER.md (row-16/17 fibre at 40 steps on two supports) into Q5/Q11; then the only open check is the fibre count on whichever release support survives item 1.
5. L02/L04/L05/L06 window cells still OPEN at joins 32-34 (dim 32/64, unscanned): G_river_6 scan in progress; close by exact_tail when it lands.
6. Q5/Q6 (success bound, premise) for every lever: carried by the r39 conventions until a characteristic exists; stay LOCAL_ONLY.

## Task 38 W4 papers-to-cells (2026-10-21)

Static cross-reference of every profile line that explicitly touches SHA-256 r37, r38, r39, or r40. Each source line gets a dedicated W4 cell with status `OPEN` and the test named by the profile row. No existing R40-Lxx-Qyy cell is changed or duplicated. Main-profile line 13 is coalesced with the identical preliminary claim in W4-P05; both profile line references are retained. The broad `pareto r1-r56` rows and SHA-256 rows outside r37-r40 are out of scope.

| cell | profile line(s) | round/topic | status | named test | exact file:line evidence |
|---|---|---|---|---|---|
| R40-W4-P01 | `PAPERS_UNTESTED_1021_prelim.md:67` | r38 first collision | COMPUTED / DERIVED / OPEN-SEMANTIC | Owned parser recounts 70 Table-3 tail marks and Table-4 exponent sum 47; source ledger gives `(70-8-6-1)+47=102`, reproducing the paper's `2^104+2^102 ~= 2^104.3` cost arithmetic. Independence/global pass law remains open; no score credit. | `research/luna_dig/TASK35_R40-W4-P01_20261021.md`; `research/grok/work/G_1120_pair_under_claw/parse_tables.py`; `research/dig/d717_sha256_r38_paper_count_ledger_record.json`; `research/grok/work/G_1120_pair_under_claw/paper.txt:571,961-1016` |
| R40-W4-P02 | `PAPERS_UNTESTED_1021_prelim.md:68` | r39 birthday comparison | COMPUTED / BLOCKED | Source audit gives 91 Table-21 marks + 77 Table-22 exponents = 168; beating the 2^128 birthday bound requires residual exponent <=127, i.e. at least 41 bit-equivalent conditions removed/absorbed. No owned characteristic generator or recurrence-aware rank/ledger test exists, so the lowering experiment is BLOCKED with no score credit. | `research/luna_dig/TASK35_R40-W4-P02_20261021.md`; `research/grok/work/G_1120_pair_under_claw/ANSWER.md:20-28,152-154`; `research/grok/work/G_1120_pair_under_claw/paper.txt:846` |
| R40-W4-P03 | `PAPERS_UNTESTED_1021_prelim.md:69` | r38-r39 tail | COMPUTED / LOCAL_ONLY / BLOCKED | Existing owned job122 finite census/beam found no complete higher-probability characteristic: weight<=4 leaves linear tail >=43, W13-W15 weight<=5 leaves >=84, and the lightest tail-zero codeword has weight 105 with ~2^-117.2 expansion cost; final states remain nonzero. Full recurrence-aware characteristic search and charged tail ledger are absent, so no score credit. | `research/luna_dig/TASK35_R40-W4-P03_20261021.md`; `research/grok/work/job122_sha256_newpath/ANSWER.md`; `research/kepler_snapshot_20261020/DEEP_39_40/LEVERS_r37_r40.md:218,228` |
| R40-W4-P04 | `PAPERS_UNTESTED_1021_prelim.md:70` | r37 empirical M0 rate | COMPUTED / LOCAL_ONLY / BLOCKED | Paper reports approximately 2^30 random M0 and 2^-9, but no raw M0 numerator/denominator or owned rerunnable M0 harness is present. The owned 512x65536 random-W15 control is 65,543/33,554,432 versus 65,536 expected (z=0.027), not the full M0 event; no tightened M0 interval or score credit. | `research/luna_dig/TASK35_R40-W4-P04_20261021.md`; `research/grok/work/G_1120_pair_under_claw/paper.txt:832`; `research/kepler_snapshot_20261020/DEEP_39_40/r37_f5522beb/proof.md:667-669`; `research/retest/pre_sha256_2/RESULT.md:10` |
| R40-W4-P05 | `PAPERS_UNTESTED_1021_prelim.md:71`; `PAPERS_UNTESTED_1021.md:13` | r37/r38 CV law | COMPUTED / LOCAL_ONLY / BLOCKED | Owned evidence has aggregate filter samples (up to 2^23 first blocks and a 15,000-block organizer panel), but no 2^20 fresh-M0 CV1 word-bit histogram, chi-square statistic, or raw seed manifest. Aggregate W7/W6 rates do not establish per-word CV uniformity or independence; no score credit. | `research/luna_dig/TASK35_R40-W4-P05_20261021.md`; `research/kepler_snapshot_20261020/DEEP_39_40/r37_f5522beb/proof.md:669,715,724-725,1504-1505`; `research/papers/sha2_collision/eprint_2026_232/paper.txt:1037` |
| R40-W4-P06 | `PAPERS_UNTESTED_1021_prelim.md:72` | r37 total-cost estimate | COMPUTED / DERIVED / BLOCKED | Paper arithmetic reconciles exactly to log2(2^35.3 + 2^119.1 + 2^122) = 122.18138461420473, rounding to 122.2. Owned artifacts have a different exact 935,612-byte table-free package and a 32,768-x family ledger check, but no smaller implementation of the paper's Ntest/Npro/TAB path; no independent total or TAB-memory credit. | `research/luna_dig/TASK35_R40-W4-P06_20261021.md`; `research/papers/sha2_collision/eprint_2026_232/paper.txt:1043-1046`; `research/kepler_snapshot_20261020/DEEP_39_40/r37_f5522beb/proof.md:737-758`; `research/retest/zoneD_family/RESULT.md:18,23,79,96-116` |
| R40-W4-P07 | `PAPERS_UNTESTED_1021_prelim.md:73` | r37 reviewer tweak | COMPUTED / DERIVED / BLOCKED | Paper’s simultaneous (A-2,A-1) match removes 27 W6 checks and changes quoted time 2^122.2 -> 2^119.1 while TAB memory changes 2^34.9 -> 2^39.9 (+5 bits). No owned matcher/TAB builder/counter exists, so the implementation test is BLOCKED and no score credit. | `research/luna_dig/TASK35_R40-W4-P07_20261021.md`; `research/papers/sha2_collision/eprint_2026_232/paper.txt:1046`; `research/kepler_snapshot_20261020/DEEP_39_40/p1120/p1120.txt:194-196,744-779`; `research/kepler_snapshot_20261020/DEEP_39_40/r37_f5522beb/proof.md:737-758` |
| R40-W4-P08 | `PAPERS_UNTESTED_1021_prelim.md:74` | r37 transfer heuristic | COMPUTED / DERIVED / BLOCKED | Paper reports that SHA-512 transfer is structurally plausible but its search typically stalls in the final two steps; no owned current SHA-512 trail-search driver, final-two-step model, candidate log, or cost ledger exists, so no transfer or score credit. | `research/luna_dig/TASK35_R40-W4-P08_20261021.md`; `research/papers/sha2_collision/eprint_2026_232/paper.txt:1080`; `research/kepler_snapshot_20261020/DEEP_39_40/p1120/p1120.txt:24-39,744-779` |
| R40-W4-P09 | `PAPERS_UNTESTED_1021_prelim.md:75` | r38 characteristic bound | COMPUTED / LOCAL_ONLY / BLOCKED | Owned 38-step drop sweep tested 55 single row-17..21 condition drops: 14 IMPLIED, 41 NECESSARY, zero violator EXACT events, and only 1.0004–1.0008 single-drop gain upper bounds; rows 22+ are inside exact output equality. No pair-drop/alternate-signing/full tail-reduction search exists, so the paper’s above-bound disposition remains unchanged and no credit is claimable. | `research/luna_dig/TASK35_R40-W4-P09_20261021.md`; `research/retest/drop_sweep38/SUMMARY.md:1-13,27-29,35-106`; `research/papers/sha2_collision/eprint_2026_1080/paper.txt:24,916` |
| R40-W4-P10 | `PAPERS_UNTESTED_1021_prelim.md:76` | r37 memory-efficient framework | COMPUTED / DERIVED / BLOCKED | Static source enumerates four shifted supports i=0..3 (35-step practical, 36/37-step theoretical, and ineffective i=3/38-step); companion arithmetic gives 38-step totals ~2^104.3 (SHA-256) and ~2^125.4 (SHA-512). Owned r37 memory package is a different fixed family and does not test per-i supports, so no universal ceiling or score credit. | `research/luna_dig/TASK35_R40-W4-P10_20261021.md`; `research/papers/sha2_collision/eprint_2026_1080/paper.txt:9,22-24`; `research/kepler_snapshot_20261020/DEEP_39_40/p1120/p1120.txt:382-398,563-588`; `research/kepler_snapshot_20261020/DEEP_39_40/r37_f5522beb/proof.md:681-685,733-737` |
| R40-W4-P11 | `PAPERS_UNTESTED_1021_prelim.md:77` | r39 SFS | COMPUTED / LOCAL_ONLY / OPEN | The requested r38 Step-2 audit is supported by owned `a0lean38.py` and deterministic D783 data (4 W7 conditions, 2^22 W14/W15 freedom, 102 late conditions, ~2^104.3 total), but this does not produce a 39-step SHA-256 SFS trail; r39 remains OPEN with no score credit. | `research/luna_dig/TASK35_R40-W4-P11_20261021.md`; `research/kepler_snapshot_20261020/DEEP_39_40/p1120/p1120.txt:519-569`; `research/retest/D783_transfer_summary.json`; `research/papers/sha2_collision/eprint_2023_285/paper.txt:142` |
| R40-W4-P12 | `PAPERS_UNTESTED_1021_prelim.md:78` | r38 SFS propagation | COMPUTED / LOCAL_ONLY / OPEN | Owned r37 A0-variant evidence is exact/finite: reusable `lowm.py`, `|G|=12,103,680=2^23.529`, 222 classes/782,800 variants, and conditional `p7=2^-5.97763`, `p6=2^-3.90197`; however no owned r38 SAT/CNF propagation toggle, solver transcript, or speed ledger exists. The actual `?`-as-`-` ablation remains OPEN with no q3/score credit. | `research/luna_dig/TASK35_R40-W4-P12_20261021.md`; `research/kepler_snapshot_20261020/DEEP_39_40/r37_f5522beb/proof.md:157-188,226-239`; `research/papers/sat_tools/arxiv_2406.20072/paper.txt:669-672` |
| R40-W4-P13 | `PAPERS_UNTESTED_1021_prelim.md:79` | r38 SFS start points | COMPUTED / LOCAL_ONLY / BLOCKED | Owned r38 proof extracts the fixed published circuit: corrected Table-4 has 47 two-bit conditions; the pair-search circuit contains all Table-3 cells, 13 vertical links, and those 47 conditions, with 110,437 variables and 383,913 clauses. The source-level arithmetic remains 70-8-6-1+47=102, but no owned alternative-x/support enumerator or start-point comparison exists; no changed condition count, q3, or score credit. | `research/luna_dig/TASK35_R40-W4-P13_20261021.md`; `research/kepler_snapshot_20261020/DEEP_39_40/r38_fb176310_accepted/proof.md:96-107,1376-1388`; `research/papers/sat_tools/arxiv_2406.20072/paper.txt:966-974` |
| R40-W4-P14 | `PAPERS_UNTESTED_1021_prelim.md:80` | r39 SFS SAT+CAS | COMPUTED / LOCAL_ONLY / OPEN | Owned r38 low-memory cluster evidence is exact/finite: 90 classes x 3,840 variants, expected passing classes 6.02051, expected good pairs 23,118.75, online memory 1,044,992 B (`log2=19.99506046703272`), declared peak `2^28` B, and charged time 87.90375. No owned r39 SAT+CAS encoding, paired toggle, or propagation-speed ledger exists; no q3/score credit. | `research/luna_dig/TASK35_R40-W4-P14_20261021.md`; `research/kepler_snapshot_20261020/DEEP_39_40/r38_fb176310_accepted/proof.md:31-42,179-184,502-527`; `research/papers/sat_tools/arxiv_2406.20072/paper.txt:802` |
| R40-W4-P15 | `PAPERS_UNTESTED_1021_prelim.md:81` | r38 branching | COMPUTED / LOCAL_ONLY / BLOCKED | Owned proof fixes the row-16 prefilter at `2^-12` and full row-16 event at `32/2^32=2^-27`; F7 is exhaustive and 180 size-3,840 classes exist, 90 selected. Existing end-to-end evidence covers only the first 64 classes (3,561 row-16 passes), not an independent all-90-class/3,840-member panel or controlled look-ahead benchmark; no q3/score credit. | `research/luna_dig/TASK35_R40-W4-P15_20261021.md`; `research/kepler_snapshot_20261020/DEEP_39_40/r38_fb176310_accepted/proof.md:31-42,160-201,439-473,870-882`; `research/papers/sha2_collision/eprint_2014_302/paper.txt:181` |
| R40-W4-P16 | `PAPERS_UNTESTED_1021_prelim.md:82` | r38-r39 two-block | COMPUTED / LOCAL_ONLY / BLOCKED | Owned A17 drop panels provide finite evidence: 32,768 samples; exact panel W23=0/32,768, conditional panel W23=112/32,768 (`log2=-8.19264508`), W25=25,173/32,768, and joint/product ratio `1.30171215` (`+0.38041046` bits). No owned full row-17/IV-hit model, look-ahead panel, or r38/r39 two-block ledger exists; no q3/transfer/score credit. | `research/luna_dig/TASK35_R40-W4-P16_20261021.md`; `research/retest/r38_groupaudit/A17_exact1_20261013.txt`; `research/retest/r38_groupaudit/a17_conditional_20261013.txt`; `research/kepler_snapshot_20261020/DEEP_39_40/r38_fb176310_accepted/proof.md:409-411,484-500`; `research/papers/sha2_collision/eprint_2021_292/paper.txt:1007` |
| R40-W4-P17 | `PAPERS_UNTESTED_1021_prelim.md:122` | r39 batching | COMPUTED / LOCAL_ONLY / BLOCKED | Owned r38 row-18 evidence: 32,768-sample A18 panel has W23=953/32,768 (`log2=-5.10366760`), W25=27,636/32,768, joint/product `1.18569981184` (+0.24573880 bits); conditional panel has W23=0/32,768 and W25=32,593/32,768. Fifteen row-18 drop tests have N1=0 and gain UB 1.0004; no complete row-18 carry map or owned r39 batch-size counter exists, so no q3/score credit. | `research/luna_dig/TASK35_R40-W4-P17_20261021.md`; `research/kepler_snapshot_20261020/DEEP_39_40/r38_fb176310_accepted/proof.md:101-103`; `research/retest/r38_groupaudit/A18_exact1_20261013.txt`; `research/retest/r38_groupaudit/a18_conditional_20261013.txt`; `research/retest/drop_sweep38/{analysis.txt,table.md,tests.txt}` |
| R40-W4-P18 | `PAPERS_UNTESTED_1021_prelim.md:123` | r39 slot scaling | COMPUTED / LOCAL_ONLY / BLOCKED | Owned r38 row-19 evidence: 32,768-sample A19 panel has W23=1,605/32,768 (`log2=-4.35164242`), W25=26,355/32,768, joint/product `1.24333143616` (+0.31421093 bits); conditional panel has W23=0/32,768 and W25=32,441/32,768. Nine row-19 drop tests have N1=0 and gain UB 1.0004; no complete row-19 carry map or owned half-size-wdig r39 run exists, so no q3/score credit. | `research/luna_dig/TASK35_R40-W4-P18_20261021.md`; `research/kepler_snapshot_20261020/DEEP_39_40/r38_fb176310_accepted/proof.md:101-103`; `research/retest/r38_groupaudit/A19_exact1_20261013.txt`; `research/retest/r38_groupaudit/a19_conditional_20261013.txt`; `research/retest/drop_sweep38/{analysis.txt,table.md,tests.txt}` |
| R40-W4-P19 | `PAPERS_UNTESTED_1021_prelim.md:124` | r39 table residency | COMPUTED / LOCAL_ONLY / BLOCKED | Owned r38 tail evidence: E21 exact panel has 32,768 samples, E21=16,141/32,768, W23=0/32,768, W25=32,761/32,768; conditional panel has E21=16,308/32,768, W23=63/32,768, W25=32,681/32,768, joint/product `1.05530311628` (+0.07765745 bits). Five row-20 drops have N1=0; eight row-21 tests have 0 EXACT (late N1 only for value/linear tests). No complete tail carry map or same-seed `WDIG`/`WDIG_FOLD` r39 run/ledger exists, so no q3/score credit. | `research/luna_dig/TASK35_R40-W4-P19_20261021.md`; `research/retest/r38_groupaudit/{E21_exact1_20261013.txt,e21_conditional_20261013.txt}`; `research/retest/drop_sweep38/{analysis.txt,table.md,tests.txt}`; `research/kepler_snapshot_20261020/FINDINGS_2026-10-21_87.md:76` |
| R40-W4-P20 | `PAPERS_UNTESTED_1021_prelim.md:125` | r39 parity filter | COMPUTED / LOCAL_ONLY / KILLED | The owned findings initially price a start/id parity filter at about -0.29 bit, then explicitly withdraw it: claw parity is determined only at the stage-2 collision re-walk, not by starts/ids; the DP is even and parity cannot be preserved for cross-parity collisions. The source correction says “No item”; no q3/score credit. | `research/luna_dig/TASK35_R40-W4-P20_20261021.md`; `research/kepler_snapshot_20261020/FINDINGS_2026-10-21_87.md:146-151` |
| R40-W4-P21 | `PAPERS_UNTESTED_1021_prelim.md:126` | r37-r38 cap bound | COMPUTED | Task35 run `research/luna_dig/TASK35_R40-W4-P21_20261021.md`; `python -I lowm_ours.py ledger`, RUN=TASK35-R40-W4-P21-20261021-1538, exact log2_nfb=55.756525841220416, pcap_log2=-12.7515867844935, time_log2=60.97002711966891, success lower bound=0.3900000029603258. H1/pcap assumptions remain conditional; no filed-score claim. | `research/kepler_snapshot_20261020/DEEP_39_40/LEVERS_r37_r40.md:20` |
| R40-W4-P22 | `PAPERS_UNTESTED_1021_prelim.md:127` | r40-r64 DP entries | COMPUTED | Task35 run `research/luna_dig/TASK35_R40-W4-P22_20261021.md`; `python -I bssha.py --ledger`, RUN=TASK35-R40-W4-P22-20261021-1537, ENTRY=22, exact N=66452608576719326629341771604882213331656, time_log2=123.98922980, peak=1048569 <= 1048576. No filed-score/characteristic claim. | `research/kepler_snapshot_20261020/FINDINGS_2026-10-21_88.md:14` |
| R40-W4-P23 | `PAPERS_UNTESTED_1021_prelim.md:128` | r40-r64 MDFA/ANDN | BLOCKED | Task35 disposition `research/luna_dig/TASK35_R40-W4-P23_20261021.md`; required post-MDFA/ANDN `bssha.py` revision/patch/manifest is absent. Existing ENTRY=22 source is P22 and was not rerun. | `research/kepler_snapshot_20261020/FAMILY_TARGETS.md:37` |
| R40-W4-P24 | `PAPERS_UNTESTED_1021_prelim.md:129` | r38-r39 low-bit fixing | BLOCKED | Task35 disposition `research/luna_dig/TASK35_R40-W4-P24_20261021.md`; cited finding supplies only aggregate `|S24|=17*2^24` and carry-regime arithmetic, not the 17 representatives/shared carry labels or a runnable enumerator. | `research/kepler_snapshot_20261020/FINDINGS_2026-10-21_86.md:33,54-56` |
| R40-W4-P25 | `PAPERS_UNTESTED_1021_prelim.md:130` | r38 exploratory memory | BLOCKED | Task35 disposition `research/luna_dig/TASK35_R40-W4-P25_20261021.md`; required capped-CDCL plan is 12 runs up to 3 hours each at 2^25.5/2^25/2^24.5 caps, with no bounded <=20-minute rung or reusable output available. | `research/kepler_snapshot_20261020/FINDINGS_2026-10-21_72.md:5` |
| R40-W4-P26 | `PAPERS_UNTESTED_1021_prelim.md:131` | r39 condition count | BLOCKED | Task35 disposition `research/luna_dig/TASK35_R40-W4-P26_20261021.md`; prescribed `find_dc_model_39.py`/AutoSHA2Collision tool is absent from the workspace, and no bounded equivalent model/manifest exists. | `research/kepler_snapshot_20261020/FINDINGS_2026-10-21_78.md:46` |
| R40-W4-P27 | `PAPERS_UNTESTED_1021.md:4` | r37 cube runs | COMPUTED | Existing owned R37M artifact already implements the W6x(t)-c path and records exact finite comparison: 27,840 invariance checks and 42,972 W6/F6 plane lanes, all 0 mismatches; exact W6/SUBF operation table in `research/luna_dig/TASK35_R40-W4-P27_20261021.md`. No duplicate run or score/package credit. | `research/tools/build_pkg/scratch/pkgR37M/work/lowm_final.py:447-451,624-637,837-858`; `research/tools/build_pkg/scratch/pkgR37M/work/out_selftest.txt`; `research/tools/build_pkg/scratch/pkgR37M/pkg/sha256-r37/proof.md:446,512-536` |
| R40-W4-P28 | `PAPERS_UNTESTED_1021.md:5` | r37 per-member counter | COMPUTED | Owned `lowm_final_v2.py` variant ledger/selftest: exact `time_log2=62.86075`, `log2_T=62.860749773734405`, `T_num/T_den=22142807405204524086627/2644`; selftest has 27,840 cube-invariance checks and 84,624 W6/F6 lanes with 0 mismatches. Variant result is exact for that program but not isolated credit for the three edits; no filed-score/package credit. | `research/luna_dig/TASK35_R40-W4-P28_20261021.md`; `research/tools/build_pkg/scratch/pkgR37M/work/lowm_final_v2.py:459-467,586-603,746-763,772-858` |
| R40-W4-P29 | `PAPERS_UNTESTED_1021.md:6` | r37 row-16 filter | COMPUTED | Owned pkgF3r ledger with the four-lane `(lo,mid)` filter: exact `PROBE=(11,8,8,6)`, `PNZ=63512/2^24`, `MU=1/256`, `time_log2=59.30714`, `log2_T=59.30713607838194`, `T_num/T_den=1885768458113931066973/2644`. This is exact for F3r, not a transfer/reprice of separate R37M; no filed-score/package credit. | `research/luna_dig/TASK35_R40-W4-P29_20261021.md`; `research/levers_1017/captains/cap_r37_work/pkgF3r/sha256-r37/proof.md:577-578,630,839,859-943` |
| R40-W4-P30 | `PAPERS_UNTESTED_1021.md:7` | r37 Zone D family | BLOCKED | Task35 disposition `research/luna_dig/TASK35_R40-W4-P30_20261021.md`; `zoneD_family/RESULT.md` has the exact `16 E5 x 4 E6[28]=1` size (`2^31.445`) and sampled late-rate table, but explicitly says the R37M family is a projection with no built family program, end-to-end run, q3 study, or per-pair operation log. Reopening needs a self-contained enumerator/manifest plus bounded one-seed operation log and ledger/self-test. | `research/retest/zoneD_family/RESULT.md`; `research/kepler_snapshot_20261020/DEEP_39_40/LEVERS_r37_r40.md:86` |
| R40-W4-P31 | `PAPERS_UNTESTED_1021.md:8` | r37 A0-variant law | BLOCKED | Task35 disposition `research/luna_dig/TASK35_R40-W4-P31_20261021.md`; existing `close37/job5` covers the published A0 row-16/17/q3 sample and `a1_rows1617` covers only four A1 members. No nonduplicate row-16..22 chi-square panel including A2 (or the remaining A1 members) is present, and no bounded variant sampler/manifest exists. | `research/retest/close37/job5/RESULT.md`; `research/retest/a1_rows1617/RESULT.md`; `research/retest/birthday/SUMMARY.md`; `research/kepler_snapshot_20261020/DEEP_39_40/LEVERS_r37_r40.md:75` |
| R40-W4-P32 | `PAPERS_UNTESTED_1021.md:9` | r37 row-16 relations | BLOCKED | Task35 disposition `research/luna_dig/TASK35_R40-W4-P32_20261021.md`; `r16_per_l` exhaustively identifies four row-16-empty classes, while `backward37` expands only selected bases and documents one empty class returning at R21. The all-four backward expansion has no bounded result and the existing full run is multi-hour. | `research/retest/r16_per_l/OWN_RESULT.md`; `research/retest/backward37/RESULT.md`; `research/kepler_snapshot_20261020/DEEP_39_40/LEVERS_r37_r40.md:68` |
| R40-W4-P33 | `PAPERS_UNTESTED_1021.md:10` | r37 bit-31 dense part | BLOCKED | Task35 disposition `research/luna_dig/TASK35_R40-W4-P33_20261021.md`; existing `alt_chars` SAT runs already cover the bit-31 tail/sign-free models and the B=29 control, all UNKNOWN at 1800 s. Rotated rows 0..24 are UNSAT only for that encoding. A new dense model or materially different bounded rung is missing. | `research/retest/alt_chars/RESULT.md`; `research/retest/alt_chars/chi31_sat.py`; `research/kepler_snapshot_20261020/DEEP_39_40/LEVERS_r37_r40.md:96` |
| R40-W4-P34 | `PAPERS_UNTESTED_1021.md:11` | r37 Bernstein bound | COMPUTED | Task35 reconciliation `research/luna_dig/TASK35_R40-W4-P34_20261021.md`; existing full `w7_budget/RESULT.md` gives Bernstein `s=2^-13.25`, `Pcap=2^-19.7`, `-0.00176` bits versus leader and 9/9 exact two-point tail checks with `bound >= exact`. r37 filed-ledger repricing is `60.38496` vs `60.38707` (`-0.00211`), conditional on H1/charging premises. | `research/gridwave6/w7_budget/RESULT.md`; `research/gridwave6/w7_budget/budget.py`; `research/kepler_snapshot_20261020/DEEP_39_40/LEVERS_r37_r40.md:43` |
| R40-W4-P35 | `PAPERS_UNTESTED_1021.md:12` | r37 fibre selection | COMPUTED | Task35 finite real-HIST_Z sweep `research/luna_dig/TASK35_R40-W4-P35_20261021.md`: theta-40 baseline `61.177835151181`; best `r(n)<=rho` at `rho=12.250448` improves `0.000536566863` bits, above the `0.0003` KILL cutoff but below the `0.001` WIN threshold. No score credit; organizer/charging interpretation remains open. | `research/gridwave6/w7_fb_prefix/xtab_p.py`; `research/gridwave6/w7_pad_knap/pad_knap.py`; `research/luna_dig/p35_real_hist_check.py` |
| R40-W4-P36 | `PAPERS_UNTESTED_1021.md:14` | r38 W25 survivors | COMPUTED | Existing owned `backward38` has two independent real-pipeline panels (seeds 31..38 and 51..58; each 8x2^28 late samples and 8,192 SMC prefix particles): EXACT/cells `2.58733 +/- 0.02576` and `2.56836 +/- 0.02465`, pooled about `2.578` (+1.366 bits). Exact/model ratio is `2625/1024` (+1.3581 bits). Finite SMC evidence only; global attack-law/prefix-uniformity and priced E19/E20 transfer remain OPEN, so no score credit. | `research/luna_dig/TASK35_R40-W4-P36_20261021.md`; `research/retest/backward38/RESULT.md`; `research/retest/backward38/run_main22.txt`; `research/retest/backward38/confirm/base.txt` |
| R40-W4-P37 | `PAPERS_UNTESTED_1021.md:15` | r38 CV selection | COMPUTED / LOCAL_ONLY | Existing qspread rates were tested against cheap `CV0[28]==CV0[29]`: tied-rank Spearman `+0.000140945639` (rates1), `-0.000419805829` (rates2), pooled `-0.000137752167`; pooled selected/unselected mean-rate ratio `0.999845416481`. No predictor or score credit; universal/attack-weighted transfer remains OPEN. | `research/luna_dig/TASK35_R40-W4-P37_20261021.md`; `research/luna_dig/p37_qspread_rank.py`; `research/grok/work/job154_r38_p1_q3/p1_test/qspread.txt`; `research/kepler_snapshot_20261020/DEEP_39_40/LEVERS_r37_r40.md:215` |
| R40-W4-P38 | `PAPERS_UNTESTED_1021.md:16` | r38 class-1 q3 | COMPUTED / LOCAL_ONLY | Existing owned-s3 fixed-class panels and exact ledger sensitivity reconcile the condition: 64-panel class 1 is `-96.141703` versus unconditioned `-96.297861` (+0.156158 bits), but the 128-panel class 1 is `-96.34793115378376` versus `-96.3133413742845` (-0.03458977949926 bits). Exact 64-panel ledger delta is `-0.154990482546` bits in score/time; both repriced scores remain above the filed control. Filed-family/class-law transfer remains OPEN. | `research/luna_dig/TASK35_R40-W4-P38_20261021.md`; `research/luna/item2839_sha256_r38_s3_per_class_q3_panel64.md`; `research/luna/item3550_sha256_r38_s3_per_class_q3_panel128_20261020.md`; `research/luna/item2840_sha256_r38_s3_class_selector_price.md`; `research/kepler_snapshot_20261020/DEEP_39_40/LEVERS_r37_r40.md:194` |
| R40-W4-P39 | `PAPERS_UNTESTED_1021.md:17` | r38 F7-rate independence | BLOCKED | The 294 `PASS` rows all share fixed `cv0=6f913881`; `qspread.txt` contains only aggregate/quantile data over 4,000 other random CV0 values, and the pass file has no per-pass row-17..21/q3 survival labels. Exact rate-to-survival stratification therefore cannot be formed. Reopening needs a fixed-CV qspread lookup plus a per-pass continuation/survival manifest. | `research/luna_dig/TASK35_R40-W4-P39_20261021.md`; `research/grok/work/job154_r38_p1_q3/p1_test/big_ls25_report.txt`; `big_ls25_samples.txt`; `p1_test/qspread.txt`; `research/kepler_snapshot_20261020/OPUS_REVIEWS/OPUS48_on_FINDINGS_2026-10-21_64.md:26` |
| R40-W4-P40 | `PAPERS_UNTESTED_1021.md:18` | r38 q3 ratio | BLOCKED | The cited 12-column computation requires the complete row-17..21 condition list plus A1-carry adjacency annotations; the review explicitly says this list is not in the pack. Proof.md has partial row predicates but not the required dependency map, so no exact delta/q3 sum can be formed. | `research/luna_dig/TASK35_R40-W4-P40_20261021.md`; `research/kepler_snapshot_20261020/OPUS_REVIEWS/OPUS48_on_FINDINGS_2026-10-21_64.md:39`; `research/grok/work/job154_r38_p1_q3/proof.md` |
| R40-W4-P41 | `PAPERS_UNTESTED_1021.md:19` | r38 cube rank | BLOCKED | The cited 12-column row-10 GF(2) rank needs the exact row-condition table and ordered 12 sign-cell columns. `research/levers_1020/r38ser` is present but contains no such matrix/rank manifest; its m01/Kissat outputs are search results and do not determine the restricted rank. | `research/luna_dig/TASK35_R40-W4-P41_20261021.md`; `research/kepler_snapshot_20261020/OPUS_REVIEWS/OPUS48_on_FINDINGS_2026-10-21_64.md:52`; `research/levers_1020/r38ser` |
| R40-W4-P42 | `PAPERS_UNTESTED_1021.md:20` | r38 P8 lattice | BLOCKED | Task35 disposition `research/luna_dig/TASK35_R40-W4-P42_20261021.md`; the cited review gives only an uncorroborated rank-572/4096 and tail 194/229–235 proposal. No local shift-lattice manifest, candidate condition table, claw support, or changed q3/tail input exists, so the owned r38 ledger cannot reprice a lower-tail point. Reopening requires the self-contained lattice enumeration/manifest and exact candidate ledger inputs. | `research/luna_dig/TASK35_R40-W4-P42_20261021.md`; `research/kepler_snapshot_20261020/OPUS_REVIEWS/OPUS48_on_FINDINGS_2026-10-21_84.md:11` |
| R40-W4-P43 | `PAPERS_UNTESTED_1021.md:21` | r38 R38M coverage | BLOCKED | Task35 disposition `research/luna_dig/TASK35_R40-W4-P43_20261021.md`; local self-tests establish the 90-class construction, but q3 and H3 are measured on the first 64 classes only, with the added 26-class transfer derived/premised. No per-class all-90 q3/H3 manifest exists, so no exact coverage or ledger delta can be formed. | `research/luna_dig/TASK35_R40-W4-P43_20261021.md`; `research/kepler_snapshot_20261020/OPUS_REVIEWS/OPUS48_on_FINDINGS_53-54.md:64` |
| R40-W4-P44 | `PAPERS_UNTESTED_1021.md:22` | r38 addition dependence | BLOCKED | Task35 disposition `research/luna_dig/TASK35_R40-W4-P44_20261021.md`; the cited paper gives a general non-independence method and a different worked trail, but no r38 T1 enumeration. Local dependency graphs/probes are structural or fixed-row diagnostics, not the requested 8-bit five-operand joint count. Reopening requires an owned T1 model and exact joint/product probabilities. | `research/luna_dig/TASK35_R40-W4-P44_20261021.md`; `research/papers/arx/arxiv_2203_09741/paper.txt:2038-2046` |
| R40-W4-P45 | `PAPERS_UNTESTED_1021.md:23` | r38 carry-window cap | BLOCKED | Task35 disposition `research/luna_dig/TASK35_R40-W4-P45_20261021.md`; only the 60,055-byte `research/cloud_jobs/kepler_plan/m01.c` source and a patch are present. No built executable, ws=2 output, exact r38 input/manifest, or runnable bounded command exists; the Kepler note itself marks solver completion/build as a prerequisite. | `research/luna_dig/TASK35_R40-W4-P45_20261021.md`; `research/cloud_jobs/kepler_plan/01_M01_online_step1.md`; `research/papers/arx/eprint_2024_1743/paper.txt:974` |
| R40-W4-P46 | `PAPERS_UNTESTED_1021.md:24` | r38-r39 characteristic ensemble | BLOCKED | Task35 disposition `research/luna_dig/TASK35_R40-W4-P46_20261021.md`; local artifacts contain only fixed-characteristic/partial-slice searches and no bounded Step-2 ensemble enumerator or per-candidate manifest. Reopening requires an owned deterministic enumerator with validity/condition checks and ledger inputs. | `research/luna_dig/TASK35_R40-W4-P46_20261021.md`; `research/kepler_snapshot_20261020/OPUS_REVIEWS/OPUS48_on_eprint_2026-1120_untested.md:28` |
| R40-W4-P47 | `PAPERS_UNTESTED_1021.md:25` | r38-r39 objective ordering | BLOCKED | Task35 static disposition `research/luna_dig/TASK35_R40-W4-P47_20261021.md`; the review records only the fixed ΣH(W),O1,O2,O3 order, while local artifacts have no owned five-step permutation driver, exact input/manifest, or bounded transcript. Reopening requires that driver plus baseline/permutation validity, q3, and ledger outputs. | `research/luna_dig/TASK35_R40-W4-P47_20261021.md`; `research/kepler_snapshot_20261020/OPUS_REVIEWS/OPUS48_on_eprint_2026-1120_untested.md:20` |
| R40-W4-P48 | `PAPERS_UNTESTED_1021.md:26` | r39 F8/F9 claw key | COMPUTED / LOCAL_ONLY | Existing owned `claw_place/r39.md` P6 audit computes 0 pruning from absorbing up to 6+4 F8/F9 bits; `P1_TEST.md` supplies exact 2^32 filter counts and 64-window LS=26 arithmetic. No new eight-window x 2^26 production rerun or global transfer is claimed. | `research/luna_dig/TASK35_R40-W4-P48_20261021.md`; `research/levers_1017/claw_place/r39.md`; `research/levers_1017/claw_place/p1_test/P1_TEST.md` |
| R40-W4-P49 | `PAPERS_UNTESTED_1021.md:27` | r39 M3/dp6 layout | BLOCKED | Task35 static audit: `vow39.c` accepts `S,dpbits,maxsteps,log2win,nwin,K,startmode,seed`, and existing sweeps contain dp6 diagnostics (`S=188416` and `S=157000,K=16`), but no local M3 layout/packing/slot manifest or ledger mapping exists. The d90878ff baseline is separately 156,672 slots, five-byte entries, dp7, 1,047,548 B, `time_log2=118.6089`; no M3/dp6 delta or score credit is claimable. Reopening requires the M3 manifest plus corresponding run and ledger. | `research/luna_dig/TASK35_R40-W4-P49_20261021.md`; `research/levers_1017/r39_joint/vow39.c:5-7,25-32`; `research/levers_1017/r39_joint/sweep1.txt:1-2,7,12`; `research/levers_1017/r39_joint/sweep2.txt:1`; `research/kepler_snapshot_20261020/FINDINGS_2026-10-20_19.md:42` |
| R40-W4-P50 | `PAPERS_UNTESTED_1021.md:28` | r39 operation split | BLOCKED | Task35 static reconciliation confirms the filed folded baseline 12,396.9 ops/claw: stage-1 walk 4,990.0, handlers 2,764.2, cut 12.9, stage-2 walk 3,329.1, stage-2 other 1,287.8, setup 2.1, generator 10.5, run setup 0.1. The requested fixed versus detection/1-theta coefficient table is absent; the named top-level r39joint.py is missing and the packaged source requires dynamic event instrumentation. No operation delta or score credit. Reopening requires the exact source manifest plus controlled event-count output. | `research/luna_dig/TASK35_R40-W4-P50_20261021.md`; `research/levers_1017/r39_joint/BUILD.md:75-87`; `research/levers_1017/r39_joint/SCORES.txt`; `research/kepler_snapshot_20261020/DEEP_39_40/r39_d90878ff/proof.md:42-56`; `research/kepler_snapshot_20261020/OPUS_REVIEWS/OPUS48_on_FINDINGS_2026-10-21_93.md:19-25` |
| R40-W4-P51 | `PAPERS_UNTESTED_1021.md:29` | r39 F8/F9 free bits | BLOCKED | Task35 static disposition `research/luna_dig/TASK35_R40-W4-P51_20261021.md`; owned `claw_place/r39.md` records F9 active bits `{0-3,10-13,19,20,23,24,27-31}`, F8 `{2,3,9,10,13-16,19,20,26,27,30,31}`, and sampled low-bit uniformity/0 pruning, but no exact E8/E9 free-bit manifest or `chi39_base` mapping exists. Therefore the claimed overlap and conditional repricing cannot be computed; no score credit. | `research/luna_dig/TASK35_R40-W4-P51_20261021.md`; `research/levers_1017/claw_place/r39.md:13,29,34`; `research/kepler_snapshot_20261020/OPUS_REVIEWS/OPUS48_on_FINDINGS_2026-10-21_91.md:14-20` |
| R40-W4-P52 | `PAPERS_UNTESTED_1021.md:30` | r39 W8/W9 redraw | BLOCKED | Task35 static disposition `research/luna_dig/TASK35_R40-W4-P52_20261021.md`; `claw_place/r39.md`/`sep_r39.py` provide random-rectangle separability only, not a fixed-window all-claws W8/W9 constancy table. The script also imports the absent/rival `verify_transplant`; no self-contained window/claw manifest or per-claw output exists. Therefore the per-window repricing cannot be established and no score credit is available. | `research/luna_dig/TASK35_R40-W4-P52_20261021.md`; `research/levers_1017/claw_place/r39.md:13,16`; `research/levers_1017/claw_place/sep_r39.py:1-2,17-49`; `research/kepler_snapshot_20261020/OPUS_REVIEWS/OPUS48_on_FINDINGS_2026-10-21_91.md:32-44` |
| R40-W4-P53 | `PAPERS_UNTESTED_1021.md:31` | r40 row-16/17 claw | COMPUTED / LOCAL_ONLY | Task35 reconciliation `research/luna_dig/TASK35_R40-W4-P53_20261021.md`; owned `LEVERS_r37_r40.md:195` counts W1/W2/W14/W15 difference conditions, pins W14/W15 in 200/200 finite checks, and gives 124 nominal late conditions after removing rows 16+17. The resulting 38/45-condition excess, 117.14-bit shifted reference, and >=140.0-bit probe floor close the structured two-claw route; no new full-family signed/modular characteristic or filed score credit. | `research/luna_dig/TASK35_R40-W4-P53_20261021.md`; `research/kepler_snapshot_20261020/DEEP_39_40/LEVERS_r37_r40.md:190,195`; `research/levers_1017/scout1017/r39r40_relax.jsonl:3` |
| R40-W4-P54 | `PAPERS_UNTESTED_1021.md:32` | r40 support search | COMPUTED / LOCAL_ONLY | Existing bounded owned search `research/kepler_snapshot_20261020/DEEP_39_40/r40_work/carry_profile/r40_support.py` gives strict minimum 7 changes over W0–W38 (8 including W39) for W0–W7=0, W16 nonzero, W27–W39=0; unique minimum adds W14 and W18–W23. The relaxed no-W0–W7 case reaches 6 but changes the model and has no modular characteristic, so no score credit. | `research/luna_dig/TASK35_R40-W4-P54_20261021.md`; `research/kepler_snapshot_20261020/DEEP_39_40/LEVERS_r37_r40.md:189`; `research/kepler_snapshot_20261020/DEEP_39_40/r40_work/carry_profile/r40_support.py:1-37` |
| R40-W4-P55 | `PAPERS_UNTESTED_1021.md:33` | r40 seven-change support | COMPUTED / LOCAL_ONLY / UNKNOWN | Existing owned `msg_sat_nob.py` run on the unique support `D={8,9,10,11,12,14}`, expansion `{16..24,26}`, all other words zero: fixed published deltas UNSAT in 58.6 s, all deltas free UNKNOWN at 600 s (within cap), free r39 control UNKNOWN at 120 s. No message pair/state window/ledger result; no score credit. | `research/luna_dig/TASK35_R40-W4-P55_20261021.md`; `research/kepler_snapshot_20261020/DEEP_39_40/LEVERS_r37_r40.md:204`; `research/levers_1017/scout1017/r39r40_charsat_work/msg_sat_nob.py:1-5,23`; `research/kepler_snapshot_20261020/OPUS_REVIEWS/OPUS48_on_FINDINGS_2026-10-21_85.md:30` |
| R40-W4-P56 | `PAPERS_UNTESTED_1021.md:37` | r38-r39 memory | COMPUTED / LOCAL_ONLY | Task35 static reconciliation `research/luna_dig/TASK35_R40-W4-P56_20261021.md`: owned r38 lean C ports measure 812,190 B heap / ~3,156 KiB RSS for plane precompute and 4,260 KiB class-build RSS, while Python/emulation reaches 83,568 KiB and q3 `traillab` 222,756 KiB. These are tool/precompute/H2 evidence, not a replacement for the quoted r38 Step-1 peak 2^28.094; r39's exact counted program is 1,047,548 B = 2^19.9986. No memory or score credit. | `research/luna_dig/TASK35_R40-W4-P56_20261021.md`; `research/levers_1020/r38ser/plane-precomp/RESULT.txt:25-32`; `research/levers_1020/r38_c/Q3_RESULT.md:19-23`; `research/kepler_snapshot_20261020/DEEP_39_40/r38_9aaf71a2_filed/proof.md:507-556`; `research/kepler_snapshot_20261020/DEEP_39_40/r39_d90878ff/proof.md:60-80` |

W4 disposition: 56 dedicated OPEN cells (57 profile lines, with the duplicate CV premise at `PAPERS_UNTESTED_1021.md:13` coalesced into P05); all named tests remain unrun by this bookkeeping pass. No solver, counter, nldtool, participant code, package, staging, or submission action was taken.
Decisive order for the whole grid: item 1, then 4, then 2. Everything else waits on a characteristic.
