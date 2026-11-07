
# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import json,sys,os
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/dig')); import add_cell
OUT=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/blake3-r2-G05-U09')
EV="research/dig/incoming2/blake3-r2-G05-U09/work/"
def rec(cell,obj,q,labels,status,number,evid,notes):
    return dict(hash="blake3-r2",row_i=None,row_j=None,object=obj,question=q,labels=labels,status=status,number=number,
      source="our workflow: scan-once-wave2",own_test=True,evidence=evid,date="2026-10-12",lever=False,gain_bits=None,
      topic=cell,notes="universe cell %s. "%cell+notes)
CAL=("Model = word-activity (active/inactive words; an add/xor with >=2 active inputs may cancel at one 32-bit condition; fold needs Z[i], Z[i+8] equal). "
 "Own C++ model actmodel.cpp written from that spec (not the older trunc_search.c). KNOWN ANSWER first: initial block-length difference v14, all 65,536 message supports, "
 "state after round 0 inactive is reachable for exactly one support {m4,m5} with 4 final-step conditions = the four-checks law (matches b3-mode RESULT). "
 "Word-level model only: bit-level partial cancellations, carries and actual solvability are NOT modelled; a condition count is not a price.")
R=[]
c="blake3-r2|MODE.parent|MODE|"
R.append(rec(c+"Q1","parent compression (flags 4+8, b=64, left||right CV): condition count of the parent route","Q1 value/condition count as used: min word conditions over all message-difference supports of a parent (IV, t=0, b=64, flags 4 or 12)",["N"],"COMPUTED",
 "Exact in the word model: min total word conditions = 8 (256 bits) for every one of the 65,535 nonzero supports; none at 7 or less (cap-8 search), none above 8. Flags 4 vs 12 are constants equal on both sides, so identical.",
 EV+"actmodel.cpp; "+EV+"chain1.log",
 "Door 3 RELABEL test (re-enumerate 65,535 parent patterns) done on our own code: confirms the 8-condition minimum. "+CAL+" Counted: every step (K,D,C,E) plus fold, no message modification. Run time 12 min, one process."))
R.append(rec(c+"Q2","parent compression: necessity of the full fold match (relax digest word 1)","Q2 necessity: let digest word 1 differ (RELAX 2) and recount the minimum conditions over all parent supports",["N"],"COMPUTED",
 "Exact in the word model: with digest word 1 free to differ, min conditions = 7 for all 65,535 supports (8 -> 7, one fold condition per word). RELAX 4 (word 2) was started and stopped unfinished for time: NOT RUN to completion. Larger relax sets not run.",
 EV+"actmodel.cpp; "+EV+"chain1.log",
 "Door 38 RELAX test, the RELAX 2 half, own code; agrees with the earlier gridwave6 summary (C min 7 under RELAX 2). The relaxed route is only useful for a near-collision first block, not a full collision. "+CAL))
R.append(rec(c+"Q3","parent compression: exact count of minimal supports","Q3 degrees of freedom: how many message-difference supports reach the minimum",["N"],"COMPUTED",
 "Exact in the word model: 65,535 of 65,535 nonzero supports have minimum exactly 8 (0 below, 0 above), strict RELAX 0; no pattern is singled out. Distinct minimal cancellation routes per support not enumerated.",
 EV+"chain1.log",
 "This is a count over supports, not over carries; the count over carry patterns is not done (door 3 notes that non-equal carry patterns stay OPEN). "+CAL))
R.append(rec(c+"Q4","parent compression: alternatives (door 23 tree/CV pairs rehash; door 38 separability at N=2^24)","Q4 alternatives: rehash the SOLCLOUD_13 two-round 64/128 and tree candidates with our reference; separability bias of the 2-round parent at N=2^24",["Z"],"SAMPLED",
 "Door 23: 40 two-round candidate pairs rehashed (32 root11-vs-root10 64/128-byte pairs + 8 tree pairs 64|128 vs 1088): 0 collide; all 8 digest words differ in every pair; digest-difference bits min/mean/max 114/129.5/144 (consistent with random). Control: the 24 one-round pairs of the same certificate all collide, as claimed. Door 38: separability at N=2^24: T1 max bias 0.000338 (2.77 sigma), T2 0.000349 (2.86 sigma), T3 word cells worst 0.00384 (262,144 quads each), T4 bit cells worst 0.00978 (65,536 quads each), 0 flagged, 0 confirmed. Both sampled, no interval beyond sigma.",
 EV+"rehash23.py; "+EV+"sep_test_copy.py; "+EV+"sep_u09_24.out",
 "Door 23 RELABEL test done with the organizer verifier (hash-smash/verifier/blake3.py, checked first on the empty-input 7-round vector). Candidates read as data from the SOLCLOUD_13 certificate, their code not run. Door 38 test is a copy of our earlier sep_test.py (self-check 50/50 vs verifier at 2 and 7 rounds). RELAX 2 half of door 38 is in the Q2 record; RELAX 4 not run. No saving found."))
c="blake3-r2|MODE.ctr|MODE|"
R.append(rec(c+"Q1","chunk counter words v12 (t_lo) and v13 (t_hi) for t>=1: where they are read","Q1 role of the counter words at this use: which calls read them at 2 rounds",["D","N"],"COMPUTED",
 "t_lo (v12) is read first by round-0 K0 (d input) then D1, and spreads to 13 of 16 G calls; t_hi (v13) by K1 then D2 (13 of 16 calls); every digest word changed in 2000/2000 trials for a flip of t bit 0, 31, 32 and 50. In the pkgCK construction the same t is used by both messages: a constant redraw, solved to prescribe a K0 value.",
 EV+"ctr_taint.py",
 "Own compressor validated against hash-smash/verifier/blake3.py on 60 cases (rounds 1, 2, 7) first. Taint = no-cancellation word propagation; empirical = bit flips on random h, m, t. Door 37 stacked-ledger test was not run."))
R.append(rec(c+"Q2","chunk counter difference: can a counter difference replace the length line","Q2 necessity: minimum final-step conditions if the two messages carry different counters (state after round 0 inactive)",["N"],"COMPUTED",
 "Exact in the word model, four-checks metric (state after round 0 inactive, K,D,C free, E + fold counted): t_hi difference alone = 4 (support {m2,m3}, one support only); t_lo alone = 8 (one support); t_lo+t_hi = 8; t_lo+length(v14) = 8; control v14 alone = 4 ({m4,m5}). No counter route below 4.",
 EV+"actmodel.cpp; "+EV+"chain1.log",
 "t_hi reaches the four-checks floor 4 through K1 (m2,m3), like the length line through K2; t_lo does not (8). Floor 4 is the known law, so no gain; a t_hi difference would need a pin like the length line gets from C3 and none is known, and legal t_hi < 2^19. "+CAL))
R.append(rec(c+"Q3","chunk counter for t>=1: exact degrees of freedom","Q3 degrees of freedom: legal counter values and how many a K0 prescription uses",["K"],"COMPUTED",
 "Exact: legal chunk counters t < 2^51 (t_lo 2^32 values x t_hi 2^19 values, max 2251799813685247 from the SOLCLOUD_13 domain check). K0 d1 = ROR(t_lo XOR a1, 16) is a bijection in t_lo for fixed (h, w0): verified exhaustively on 2^20 values, algebraic for all 2^32. So prescribing d1 costs exactly one 32-bit word of freedom and leaves 19 bits of t_hi unused.",
 EV+"ctr_taint.py",
 "Matches the pkgCK note that solving t uses up w0. Cost of building t chunks of prefix is in the ledger and not re-derived here."))
R.append(rec(c+"Q4","chunk counter: alternatives by initial-difference class","Q4 alternatives: initial-state difference classes {t_lo}, {t_hi}, {t_lo,t_hi}, {t_lo,v14}",["Z"],"COMPUTED",
 "Exact in the word model (all 65,536 supports each): four-checks minimum 8, 4, 8, 8 for t_lo, t_hi, both, t_lo+len. Nothing under 4. Not scanned: v15 (flags) combinations, row-a CV differences (door 45), the other 11 subsets.",
 EV+"chain1.log",
 "Door 37 (fresh CV per context) not tested by its RELABEL method; only arithmetic from the map numbers: one extra compression per context = 2^50.115 x 430 units = 2^58.9 vs 2^71.935 total = about +0.0002 bit (DERIVED, consistent with 'cheap', door stays CLAIMED-UNTESTED). "+CAL))
for r in R:
    fn=os.path.join(OUT,r['topic'].replace('|','_')+'.json')
    json.dump(r,open(fn,'w',encoding='utf-8'),indent=1)
    add_cell.validate(json.load(open(fn,encoding='utf-8')),add_cell.load()); print('ok',os.path.basename(fn))
