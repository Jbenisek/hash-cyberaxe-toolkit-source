counter_swing\opposite: the opposites and limits of the chunk-counter lever (55/63, t solved per trial).
Written 2026-10-08. Research only. No yukon, nothing filed, posted or cancelled; trace untouched; no credential
file opened. Nothing written outside this folder. Windows python 3.14 + numpy, always with -B. At most 2 processes
at a time, all finished. Tags: COMPUTED = run here; DERIVED = argued from code or a stated fact; GUESS = judgement.

FILES (run from this folder)
  blake3_ref.py         byte-identical copy of hash-smash\verifier\blake3.py (sha256 bf67aca2...0237): the referee
  blake3_toy.py         the referee ported line by line to word size W (toy W = 8 of counter\toy\toy.h);
                        python -B blake3_toy.py -> 24/24 equal to blake3_ref at W = 32 (multi-chunk, up to 8684 bytes)
  arr.py, b3own_copy.py the counter arrangement (copied from counter\structure\arrange_check.py / b3own.py)
  model_copy.py         counter\structure\model.py (word model, reverse peeling)

  item 1 constraints    constraint_check.py 1000 31 -> constraint_check.txt
                        B tail bytes 55..62 nonzero: half 0/2000; freeing w14/w15 opens no prescription
  item 2 replication    replicate_toy.py 12 20 7 -> replicate_toy.txt   (reads counter\toy\out\*.txt HIT lines)
                        240/240 random prefixes collide, 240 distinct digests; other t' 0/58; suffix 0/60
  item 3 round count    rounds_reach.py 18 4 400 17 -> rounds_reach.txt
                        17 chain words, all in round 1; 13 in the last step at 2 rounds, 0 at 2.5 and 3;
                        free half 400/400 at 2 rounds, 0/400 at 2.5 and 3
  item 4 reverse side   reverse_check.py 2000 23 -> reverse_check.txt
                        prefix content invisible 200/200; root parent: 16/16 state words differ after round 0
  limits: size cap      sizecap.py 64 29 -> sizecap.txt  (Part 1 table: only 64 outer steps, noisy for small k;
                        superseded by:) sizecap.py inv 20000 12 41 -> sizecap_inv12.txt,
                        sizecap.py inv 3000 16 43 -> sizecap_inv16.txt  (mean uniform, extreme clustering)
                        affine.py NOUTER K SEED [NBASE] -> affine_k*.txt  (affine-guided small-t enumeration)

The findings, with costs, concerns and next tests, are in the structured result returned to the orchestrator.
