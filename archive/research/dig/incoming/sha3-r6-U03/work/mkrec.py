import json, os
EV="research/dig/incoming/sha3-r6-U03/work/ (kk.py validated 24r vs hashlib and 6r vs organizer verifier; cone.py, fam.py, fp.py, q.py; cone.json, footprint.json, q_results.json)"
def rec(cell, q, question, obj, labels, status, number, notes):
    r=dict(hash="sha3-r6",row_i=None,row_j=None,object=obj,question=question,labels=labels,status=status,number=number,
           source="our workflow: scan-once",own_test=True,evidence=EV,date="2026-10-12",lever=False,gain_bits=None,
           notes="universe cell %s|%s. "%(cell,q)+notes,topic="sha3r6 "+cell+" "+q)
    fn=("sha3-r6_%s_chi_%s.json"%(cell,q)); json.dump(r,open(fn,'w'),indent=1); 
R2="round2.chi"; R3="round3.chi"
O2="1-indexed round 3 chi + theta4 parities (leader chi3 block, 53.30 ops/message); 140-bit key = digest lanes 0..3 at z in KEEP (35 planes)"
O3="1-indexed round 4 chi + theta5-at-store (leader 'round-4 cone', 46.11 ops/message, 1363 of 1600 words)"
G="Family = leader's 128-byte prefix family rebuilt by us (L8=0, L5=L15=D0, C2=NOT rotl(C4,1); z XORed into lanes 4 and 14): A2 affine in z checked 30x256, z-flip support 22 words (matches Lemma 3). "
rec(R2,"Q1","How many rows, bits and conditions does the chi3 block use?",O2,["N","B"],"COMPUTED",
 "rows 320 of 320 (1600 chi outputs, 1600 input bits, 320 theta4 column parities); conditions at this block: 0 own (the 256 linear prefix conditions of rounds 1-2 are upstream); per Gray step only 273 of 320 rows (499 of 1600 theta3-applied words) change, 47 rows have unchanged input",
 G+"Exact backward bit-cone from the 140 key bits through rounds 6,5,4,3 (cone.json): chi6 140 out/35 rows; chi5 1161 out/290 rows (reads 1363 words, matches leader Lemma 10); chi4 1600/320; chi3 1600/320 rows, 320 theta columns. Step footprint measured with 24 random bases x 32 flips x 256 groups: 22 / 499 / 1087 words after A2 / theta3 / chi3; 273 chi3 rows touched, identical for every flip (z-rotation symmetry). Leader quotes 554 words for the stored round-3 patch; ours is the exact union over 256 groups (499), theirs may be a structural bound (ours structural 750). Not reconciled with K=13 bodies (not read).")
rec(R2,"Q2","Which chi3 rows and bits are necessary?",O2,["N","K"],"COMPUTED",
 "all 320 rows / 1600 outputs / 320 parities necessary (cone = 1600 of 1600); sampled flip test: 1600 of 1600 chi3-output bits and 1600 of 1600 theta4-applied bits changed the key in 64 of 64 random family states; 0 rows removable",
 G+"Structural cone says every chi3 output is needed (theta4 spreads each into the chi4 cone which is full). Own flip test (q.py): S3 bits and T4 bits, 64 states each, min hits 64/64. So no chi3 row can be dropped; the only saving possibility is skipping recomputation of the 47 rows whose inputs did not change in a step (see Q1).")
rec(R2,"Q3","How many bits of freedom (log2) are left through the chi3 block?",O2,["N","I"],"SAMPLED",
 "32.0 bits per group (z), no loss at chi3: 262,137 distinct z gave 262,137 distinct chi3 outputs (2^18 sample); family total 1024-256 = 768 bits before the key (140-bit key keeps 140; 12 bits above the 128 needed)",
 G+"chi3 and the whole 3-round prefix is a bijection of the 1600-bit state, so the 2^32 z values per group stay distinct exactly (BEDROCK argument); sample confirms. A2 is affine with 32 independent directions (E_j have disjoint supports). 256 = four lane equations (64 each). Exact count over all 2^32 z not enumerated; the bijection argument covers it.")
rec(R3,"Q1","How many rows, bits and conditions does the round-4 cone use?",O3,["N","B"],"COMPUTED",
 "chi4: 320 of 320 rows, 1600 outputs, 320 theta5 parities all needed; stores 1363 of 1600 theta5-applied words (237 skipped); next round reads those 1363 words in 290 rows (1450 row-level); chi5 computes 1161 outputs; conditions at this block: 0",
 G+"Exact backward cone (cone.json): chi6 140 out/35 rows/175 words; chi5 1161 out/290 rows/1363 words; chi4 1600/320. Matches the leader dossier numbers (1,161 chi outputs, 1,363 words read, 175 words) with our own code. Step footprint: all 1600 words after chi4 change on every z-flip (T4/S4/T5 = 1600 of 1600 in the union over 256 groups), 320 of 320 chi4 rows touched. Naming: this reads 4867f093 'round-4 cone' as stored words of 1-indexed round 4.")
rec(R3,"Q2","Which round-4 rows and words are necessary?",O3,["N","K"],"COMPUTED",
 "necessary: all 320 chi4 rows and 1600 outputs; of the 1600 theta5-applied words exactly 1363 are necessary and 237 are not (unneeded per lane: lanes 0-9 about 13-15 each, lanes 10-24 6 each); flip test agrees exactly: 1363 of 1600 words change the key, 0 outside the cone, 0 cone words silent (64 states)",
 G+"Set equality between structural cone and sampled sensitivity verified (q_results.json T5_sens_vs_cone: agree true, 0 sensitive outside cone, 0 cone words without effect; min hits among the 1363 is 21/64). chi4 outputs and theta4-applied words: 1600/1600 sensitive in 64/64 states.")
rec(R3,"Q3","How many bits of freedom (log2) are left through the round-4 cone?",O3,["N","I"],"SAMPLED",
 "32.0 bits per group survive into the 1363-word cone and into the 140-bit key (2^18 sample: 262,137 distinct z -> 262,137 distinct 1363-bit cone images and 262,137 distinct keys); key space 140 bits vs 128 needed = 12 bits slack; across the 768-bit family the key is the bottleneck at 140",
 G+"Round 4 is a bijection, so its output keeps all 32 bits exactly; the 1363-word projection and the 140-bit key are lossy in principle but showed no collision in 2^18 samples (expected random-collision count about 0). Sample only; no exhaustive 2^32 check.")
