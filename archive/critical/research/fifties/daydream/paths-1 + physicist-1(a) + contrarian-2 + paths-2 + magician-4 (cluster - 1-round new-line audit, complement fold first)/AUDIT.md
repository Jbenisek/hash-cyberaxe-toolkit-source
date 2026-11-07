# 1-round new-line audit (2026-10-09, about 21:00-21:10 MDT)

Folder name: the brief's path had "cluster: ..." ; ':' is illegal in Windows paths, so it is "cluster - ...".

| Mechanism | Our filed line? | Verdict |
| --- | --- | --- |
| Complement fold, 2 words (m9/m13 via m8/m12 c1=0; or m11/m15) | none (O3 "partial", never filed) | NEW LINE for us; common on the board (rickmanelius 7e29738c "two-word complement", Subflatus3, pratikgx). STAGED as pkgR1K, 2.5477. |
| Complement fold, all 4 diagonals | same mechanism | not a separate line (one filing per line) |
| shape_pair: 64-byte root (flags 11) vs parent root (flags 12), counter 0, m6/m7 | R1F 31acfdbb is exactly this (1,088 vs 64 bytes, flags 12 vs 11, m6/m7 by Lemma 1) | DUPLICATE, drop. R1F's XOR solve needs no 3-bit condition; shape_pair's +1/-1 is a weaker variant. |
| R1C "counter needed, flag alone fails" | - | no conflict: R1C's pair is a non-root right child, chunk index 2 (counter 2) vs a parent (counter 0); the counter difference is forced there. Root pairs at counter 0 are R1F. Wording scope only. |
| Inversion (O2, Path B), 64/64 pairs | not filed as its own line; R1V uses it only to build block 0 | CANDIDATE line for the owner to decide; on the board from jvr0x, AArnott, jungjipdo. Not costed. |
| CV difference (evolution-1) | R1V 6b039da2 | DUPLICATE |

COMPUTED: complementfold1r.py 200/200 per variant (m11/m15, m9/m13, all four) at rounds=1, 2-round
equal False; daydream_1r_tests.py complement 20/20, shape_pair 20/20 (mean 10 tries for the 3-bit condition).
pkgR1K pair: organizer blake3.py 1-round digests equal, 2 compressions, 2-round differ, final-state
complemented words exactly {0,2,5,7,8,10,13,15}; op count 154 data ops (counting harness on the producing
program); organizer `verifier certificates` = passed, `verifier intake` = mechanically_valid.

Caveat on the organizer run (COMPUTED, disclosed): run under Windows Python with one shim, because Windows
os.scandir gives st_ino = 0 and intake's own re-open check then fails every file; under WSL the mounted research volume copy
shows mode 0777 and fails "executable". NOT RUN: the R1V-style WSL sandbox clone (scripts/local_tracks.py check,
hashsmash_pipeline.py intake), because it writes outside this folder. Run that (copy check_r1.sh from
pkgR1V, point P at pkgR1K/pkg/blake3-r1) before filing.

DERIVED: time 2 + 854/222 = 1,298/222, log2 2.54766 -> 2.5477; memory < 2^18.
GUESS: rivals score the same mechanism at 1.5 by not charging verification/memory traffic as we do;
the filing will not move the board, it adds a line.

Files: pkgR1K/work/complpair.py (generator), check_pair.py (+ .out), make_claim.py, organizer_check_win.py
(+ organizer_verifier.out.txt, intake_out/), pkgR1K/pkg/ (blake3-r1/{claim.json, proof.md, certificates/},
submission-note-r1.md). claim.json submission_state = draft. No yukon run; owner's go needed to file.
