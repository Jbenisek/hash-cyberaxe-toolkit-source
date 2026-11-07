
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

import json, os
OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming/blake3-r2-U11')
EV = ("research/dig/incoming/blake3-r2-U11/work/b3lib.py; research/dig/incoming/blake3-r2-U11/work/validate_b3.py (+validate_b3.out); "
      "research/dig/incoming/blake3-r2-U11/work/scan_m1011.py (+scan_m1011.out.json, scan.log)")
CLASS = ("Class: FREE trial word (step T of the pkgB3U root construction, one of w8..w11; not pinned w4, not cancelling w5, not a forced constant X3/X7/X11/X15). "
         "w10 is the first and w11 the second message word of D1 = G(1,6,11,12) in round 0; in round 1 w10 is the second word of C1 (slot 3, enters Y1) and w11 the second word of E0 (slot 9). "
         "Solved lines: w10 = D1.a1 - S1 - S6, w11 = X1 - D1.a1 - D1.b1. Construction validated first on our b3lib.py (3000/3000: X3/X7/X11/X15, Y4=y, S and X equal A vs B, digest words 0,2,5,7 equal). "
         "Method as blake3-r2-U06 (scan_m01.py) applied to words 10,11. Tested the pkgB3U root construction only, 2 rounds, A (len 55) vs B (len 63).")
base = dict(hash='blake3-r2', row_i=None, row_j=None, source='our workflow: scan-once', own_test=True, evidence=EV,
            date='2026-10-12', lever=False, gain_bits=0.0, gain_basis='T')
Q = {
 1: ("How many difference/condition constraints does this word carry (own count over the printed definitions)?", ['I', 'N'], 'SAMPLED',
     "{w}: difference between A and B = 0 (structural: B copies A except w4,w5; 0/20000 builds differ). Direct conditions on the word alone: 0. It enters one pinned condition through D1: X11 (D1's c output) = 44036000, 32 bits, carried by the PAIR (w10,w11) jointly (X11 = pin in 20000/20000 builds; D1 forward from S1,S6,S11,S12 with (w10,w11) reproduces X1,X6,X11,X12 in 20000/20000). Both words together: 64 bits of words, 32 bits spent on the pin, 32 bits left as the y link. Bit balance over 20000 contexts: max bias {bias} (no fixed bit); counts per bit in [{lo},{hi}]",
     "Universe cell blake3-r2|{w}|msgword|Q1. " ),
 2: ("Is each condition group on this word necessary (relax one, recount the exact outcome)?", ['I', 'Z'], 'SAMPLED',
     "{w}: every group is needed. Flip one bit of {w} in both A and B (6000 trials: 4 random bits x 1500 contexts): X3/X7/X11/X15 kept 0/6000, X11 kept 0/6000, Y4=y kept 0/6000, digest words 0,2,5,7 equal A vs B 0/6000 (S still equal 6000/6000; X lanes 1,6,11,12 = D1 outputs change 6000/6000). Flip in B only: lemma H events kept 0/6000, X(B)=X(A) 0/6000. Control unchanged: lemma H kept 1500/1500. Relax the X11 pin: with X11 pinned, for every w10 exactly one w11 hits it (40000/40000 solved w11 hit the pin, 0/40000 other random w11), so the pin leaves 2^32 of the 2^64 pairs (a factor 2^32, bijection of w11 -> c2)",
     "Universe cell blake3-r2|{w}|msgword|Q2. Counts are sampled bit flips (4 random of 32 bits per context), not all 32 bits; the 2^32-of-2^64 count is exact by the bijection argument (a2 = a1+b1+w11, d2 = ROR(d1 XOR a2,8), c2 = c1+d2 each bijective in w11), confirmed 40000/40000. " ),
 3: ("What is the local freedom of this word given the other rows (exact count)?", ['I'], 'COMPUTED',
     "(w10,w11) given a context (six outer words + X2): exactly 2^32 pairs, parametrised by y. w10 is a bijection of y (inverse w10 -> y round-trips {rt}/{n} on 2^25 consecutive and 2^25 random y; 2^25 distinct w10 each) and w11 is a function of w10 (distinct pairs 2^25 of 2^25 both sweeps; distinct w11 {dw11} of 2^25 consecutive = a random function, not injective alone). The pair is free per context only to 32 bits, not 64: the pin X11 fixes one 32-bit relation. Over contexts: 150000 random 8-word builds give 150000 distinct w10, 149998 distinct w11, 150000 distinct pairs. Dependence on the 8 free params: all of C0c1, C0d1, D3d1, S15, S9, w5, X2, y change both w10 and w11 (1500/1500 each)",
     "Universe cell blake3-r2|{w}|msgword|Q3. Sweeps are 2^25 of 2^32 y values for one random context (checked equal to build() on 2000 y), the bijection w10<->y is exact by composition of invertible lines (a1 = S1+S6+w10, d1 = ROR(S12^a1,16), c1 = S11+d1, X12 = X11-c1, C0 chain back to y). NOT done: whether every pair (w10t,w11t) of 2^64 is reachable over all contexts (surjectivity onto 64 bits) was not tested; the per-context count of 2^32 is what we know. " ),
 4: ("Are there alternative treatments of this word (other differences, input-difference absorption, other values)?", ['I', 'Z'], 'SAMPLED',
     "(w10,w11) with the same D1 outputs: exactly one pair per (S1,S12) input choice. A difference in D1 inputs S1 and/or S12 between A and B is absorbed exactly by (w10,w11): S1 and S12 both differ 100000/100000, S1 only 100000/100000, S12 only 100000/100000 (outputs X1,X6,X11,X12 equal). Differences in S6 or S11 cannot be absorbed: b1,c1,d1 are fixed by the outputs, so S6 = ROL(b1,12)^c1 and S11 = c1-d1 are forced equal (100000/100000). The route is closed: S12 is a function of (S4,S8) at K0 for any counter/flags (200000/200000), so an S12-only difference cannot arise; S12 differing means S4,S8 differ, and S4 (D3 input) and S8 (D2 input) have no absorbing words in this layout (w14=w15=0, w13=W13 pinned). Carry patterns: all additions are solved by subtraction, one outcome each, no 75/32-type multiplicity",
     "Universe cell blake3-r2|{w}|msgword|Q4. Where it would reach the same later differences: the D1 outputs are identical so X and everything after is identical, but only if the other K-lanes agree; not a usable path in the pkgB3U layout. Not tested: joint hand-designed cancellations through C1/E0 in round 1. " ),
}
d = json.load(open(os.path.join(OUT, 'work', 'scan_m1011.out.json')))
q1 = d['Q1']; sw = d['Q3_y_sweep']
for wn in (10, 11):
    w = f'w{wn}'; mname = f'm{wn}'
    for q in (1, 2, 3, 4):
        quest, labels, status, num, note = Q[q]
        num = num.replace('{w}', w)
        if q == 1:
            num = num.replace('{bias}', f"{q1['max_bit_bias_w%d' % wn]:.4f}").replace('{lo}', str(q1['bitcount_range_w%d' % wn][0])).replace('{hi}', str(q1['bitcount_range_w%d' % wn][1]))
        if q == 3:
            num = num.replace('{rt}', '33554432').replace('{n}', '33554432').replace('{dw11}', str(sw['consecutive']['distinct_w11']))
        rec = dict(base)
        cid = f'blake3-r2|{mname}|msgword|Q{q}'
        rec.update(id=cid, object=f'pkgB3U message word {mname} ({w})', question=quest, labels=labels, status=status, number=num,
                   notes=note.replace('{w}', mname) + CLASS, topic=f'b3r2.{mname}.msgword.Q{q}')
        json.dump(rec, open(os.path.join(OUT, f'blake3-r2_{mname}_msgword_Q{q}.json'), 'w'), indent=1)
