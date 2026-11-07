import json
W='research/dig/incoming/blake3-r2-U04/work/'
base=dict(hash='blake3-r2',row_i=None,row_j=None,source='our workflow: scan-once',own_test=True,date='2026-10-12',lever=False,gain_bits=0.0,gain_basis='count')
recs={}
recs['blake3-r2|E1.q1|step|Q2']=dict(object='E1 q1 (a1,d1) zero-difference requirement, necessity',
 question='Is the equal (a1,d1) of E1 needed by the XOR event, and what does relaxing it activate?',
 labels=['0','Z'],status='LOCAL_ONLY',
 number='baseline: 0/300 constructed pairs have nonzero diff at E1 q1; to get nonzero diff, inject 1-bit diff in a round-2-start word: v1/v6/v12 path needs a diff in one of the 12 non-C3 words, activating 6 round-2 calls vs 3 baseline (+C0|C1|C2, +E0, +E2), words 0,2,5,7 stay equal in 0/1920 injections',
 evidence=W+'q1relax.py; '+W+'q1relax_out.txt',
 topic='b3.r2.E1.q1.relax',
 notes='Universe cell blake3-r2|E1.q1|step|Q2. Not needed by the event (E1 outputs only enter o1,o3,o4,o6 = residual R), but Delta(a1,d1) = f(v1,v6,v12) and those come from C1.a,C2.b,C0.d, each depending on all 4 of its inputs (16/16 dependence checked). The only difference sources in the pair are message words w4 (enters C3) and w5/length (cancelled in round 1: state after round 1 has 0 differing words in the sample), so a nonzero E1 q1 diff means breaking the round-1 cancellation or pinned D outputs. Window test only: single-bit injections on B state at round-2 start, 40 contexts x 16 words x 3 bits; no compensated multi-word search. Same relaxation as E0; no gain.')
recs['blake3-r2|E1.q1|step|Q4']=dict(object='E1 q1 (a1,d1) alternatives to equality',
 question='Which alternative (nonzero) a1,d1 differences exist and what do they cost in activated calls?',
 labels=['0','Z'],status='LOCAL_ONLY',
 number='alternatives by injection word: v0/v4/v8/v12 -> C0 active, 6 calls; v1/v5/v9/v13 -> C1, 6 calls; v2/v6/v10/v14 -> C2, 6 calls; v3/v7/v11/v15 -> no E1 q1 effect (C3 inputs), 5 calls; baseline 3 calls (C3,E1,E3); E0 and E2 become active in every alternative; 0/120 per word keep CV words 0,2,5,7 equal',
 evidence=W+'q1relax.py; '+W+'q1relax_out.txt',
 topic='b3.r2.E1.q1.alt',
 notes='Universe cell blake3-r2|E1.q1|step|Q4. Every alternative to equal (a1,d1) activates C0/C1/C2 plus E0 and E2 (the calls whose outputs the event needs equal), i.e. costs about 128 bits of equality on words 0,2,5,7 instead of 0; no alternative found cheaper than the construction. One-bit differences only (window), generic A/B pair from frontline CO/CT/CS; not a proof that a compensated multi-word difference is impossible. No gain.')
recs['blake3-r2|E1.q2|step|Q3']=dict(object='E1 q2 cube Q* dimension',
 question='What is the exact dimension of the set of c1 giving beta* (and beta2), counted over all carries?',
 labels=['I','E'],status='COMPUTED',
 number='|Q*| = |Q_2| = 2^21 exactly of 2^32 c1 (11 fixed bits, affine cube dimension 21), rate x2^11; beta values over all 2^32 c1: 162,507 distinct, 187 with cube dimension 21',
 evidence=W+'cube.c; '+W+'cube_out.txt; '+W+'q2cube.py; '+W+'q2cube_out.txt',
 topic='b3.r2.E1.q2.cube_dim',
 notes='Universe cell blake3-r2|E1.q2|step|Q3. Two independent exact counts: C brute force over all 2^32 c1 (count 2097152 each, 0 mismatches against the cube masks 0e09818b/02008000 and 0e09818d/02008001) and a carry-path DP (sum of cubes = 2^32 check). Real pairs from frontline step_ct: c1 in Q* gives E1 b1 diff beta* 40/40, c1 in Q_2 gives beta2 40/40. Confirms the proof statement; no gain.')
recs['blake3-r2|E1.q2|step|Q2']=dict(object='E1 q2 cube bits necessity and effect on beta',
 question='Is each of the 11 fixed bits of c1 in Q* necessary, and which beta does flipping it give?',
 labels=['I','E'],status='COMPUTED',
 number='all 11 fixed bits (c1 positions 0,1,3,7,8,15,16,19,25,26,27) individually necessary: flipping any one gives 0/2^21 beta*; flip of bit 0 gives beta2 18d0e098 for half the half-cube; flips of bits 15 and 25 give a single beta each (18b0e088, 18b0a098); other bits give 4-11 betas; no 10-bit subset suffices (count over 2^32 is exactly 2^21)',
 evidence=W+'q2cube.py; '+W+'q2cube_out.txt; '+W+'cube_out.txt',
 topic='b3.r2.E1.q2.cube_necessity',
 notes='Universe cell blake3-r2|E1.q2|step|Q2. Exact over carries: each relaxed cube (2^22 c1) enumerated, beta=ROR(c1^(c1+DY11),12). Flip of bit 27 gives 18b1e098/18b3e098 (the third-beta row of ATLAS_BLAKE3 B appears here as a neighbor of Q*). Does not change the ledger by itself; no gain.')
import os
for k,r in recs.items():
    d=dict(base); d.update(r)
    fn=k.replace('|','_')+'.json'
    json.dump(d,open(fn,'w'),indent=1)
    print(fn)
