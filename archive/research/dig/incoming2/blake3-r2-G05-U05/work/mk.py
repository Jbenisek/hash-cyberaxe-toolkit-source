
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

import json, os, sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
out = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/blake3-r2-G05-U05')
EVID = "research/dig/incoming2/blake3-r2-G05-U05/work/ (model.py, pin.py, cone.py, scan.c, res_mode0_seed21.jsonl, res_mode1_seed11.jsonl)"
KNOWN = ("KNOWN ANSWERS first: model.py reproduces the verifier (hash-smash/verifier/blake3.py) on the empty 7-round hash af1349b9...3262 and on 600 random messages at 1/2/7 rounds; "
         "Lemma L (55/63 pair, w4n=((K+w4)^8)-K, w5n=w5+w4-w4n) gives identical state after round 0 in 300/300; "
         "the pinned C3 call (X3=29d4fa98 X7=bee3af28 X11=44036000 X15=40c58500, w4=97475638 -> 97475640, w13=0007c006) reproduces Y3=8127c181/7edf3e7e, Y11=7af77f38/850000c3, Y7=76f7aefd both, Y15=bbfbdffe both, "
         "and digest words 0,2,5,7 agree in 20000/20000 random round-1 completions. ")
POOL = ("Round-1 pair model: the pair shares X after round 0 and differs only in w4,w5, so only C3 (w4) and E1 (w5) see a difference. "
        "Cone test (cone.py, 400 trials per input): digest words 0,2,5,7 stay equal when ANY of X0-X2,X4-X6,X8-X10,X12-X14,w0-w3,w5-w12,w14,w15 is re-randomised, and become unequal in 400/400 when any of X3,X7,X11,X15,w4,w13 is; "
        "words 1,3,4,6 are never equal (0/400) after re-randomising any of the 32 inputs. ")
FIB0 = ("Pin fibres (scan.c mode 0, ALL 2^32 values of one word, others at the pin, other state words random seed 21; exact for that base): "
        "Yeq (C3 b and d outputs equal): X3 1 solution (the pin 29d4fa98), X15 2 (incl. the pin 40c58500), w13 1 (the pin 0007c006). "
        "D0=0 count incl. cancellations: X3 3, X15 4, w13 1; of these not Yeq: 2, 2, 0. D2=0: 1,5,2; D5=0: 2,3,4; D7=0: 2,2,2. "
        "All four of D0,D2,D5,D7 zero: 1,2,1 = exactly the Yeq solutions. ")
BIJ = ("Single-word maps (scan.c mode 2): Z0<-Y15 in E0 is an exact bijection of 2^32 (exhaustive, image 4294967296); Z8<-Y7 in E2 has image 2715282391 = 0.63218 of 2^32 (random function 1-1/e = 0.63212; exhaustive). "
       "Z2<-Y7 and Z10<-Y15 by birthday sampling of 2^23 inputs: 16458 and 16243 output collisions vs 8192 for an injective map and about 16384 for a random function (sampled). "
       "An exhaustive bitmap run for these last two maps was killed by me after 11 min as too slow; not run. ")
LIM = "Limits: round-1 model only; pinned states X are not realised from messages here (existing inversion Fact 1 not re-run); one base state per scan, not a distribution over bases."
M1 = ("Residual scans (scan.c mode 1, seed 11, one base, ALL 2^32 values of one word; exact for that base; Y3,Y11,w5 pair values from the pin). "
      "Count of v with D1=0 / D3=0: Y1 0/0, Y6 0/0, Y12 0/0, w12 0/0, w5 0/0, Y4 0/0, Y9 0/0, Y14 8/0, w8 0/0 (D4=0 only Y14 1; D6=0: Y1 1, Y6 1, Y12 3, w12 1, Y4 3). "
      "Weight histograms of the 32-bit pair difference for weights 0..8 are in res_mode1_seed11.jsonl; binomial for 2^32 draws is 1,32,496,4960,35960,201376,906192,3365856,10518300. ")
recs = []


def rec(cell, obj, q, number, notes):
    recs.append(dict(hash='blake3-r2', row_i=None, row_j=None, object=obj, question=q, labels=['N'], status='LOCAL_ONLY', number=number,
                     source='our workflow: scan-once-wave2', own_test=True, evidence=EVID, date='2026-10-12', lever=False, gain_bits=None,
                     notes='universe cell %s. ' % cell + notes, topic=cell, _cell=cell))


for w, (zk, ok) in {0: ('Z0', 'Z8'), 2: ('Z2', 'Z10')}.items():
    cell = lambda q: 'blake3-r2|OUT.d%d|OUT|Q%d' % (w, q)
    obj = 'digest word %d = %s ^ %s (pinned by E0/E2)' % (w, zk, ok)
    Ymap = ('Z0<-Y15 (E0 a-output, d input) is an exact bijection, so Y15 alone cannot cancel' if w == 0 else
            'Z2<-Y7 (E2 a-output, b input) and Z10<-Y15 are non-injective (sampled)')
    rec(cell(2), obj, 'Necessity of the identical-input pin: relax or replace it and recount the exact outcome mass',
        'The pair difference of digest word %d depends only on C3 outputs Y7,Y15 (inputs X3,X7,X11,X15,w4,w13); 26 of 32 inputs irrelevant (400/400). Pin: D%d=0 with probability 1 (0/20000 failures). Relaxed: cancelling (Y7,Y15) pairs give D%d=0 at about 1 per 2^32 values of a pin word (measured 2,2,0 outside Yeq), i.e. mass about 2^-32 per trial; all four words 0,2,5,7 together survive only on Yeq (1,2,1 of 1,2,1).' % (w, w, w),
        POOL + FIB0 + BIJ + KNOWN + 'Reading: the pin is necessary for the 4-word bundle (0,2,5,7 share Y7,Y15), not for word %d alone. %s. ' % (w, Ymap) + LIM)
    rec(cell(3), obj, 'Degrees of freedom: exact count over carries',
        'D%d=0 for every value of 26 inputs (400/400); six words X3,X7,X11,X15,w4,w13 carry a 64-bit condition (Y7,Y15 equal); exact single-word fibres on Yeq at the pin: X3 1, X15 2, w13 1 (of 2^32 each). Derived, not measured jointly: about 2^128 solutions of the six pinned words.' % w,
        FIB0 + POOL + BIJ + KNOWN + LIM)
for w in (1, 3):
    cell = lambda q: 'blake3-r2|OUT.d%d|OUT|Q%d' % (w, q)
    zk, ok = ('Z1', 'Z9') if w == 1 else ('Z3', 'Z11')
    obj = 'digest word %d = %s ^ %s (residual from E1/E3)' % (w, zk, ok)
    if w == 1:
        q2 = 'D1=0 needs 32 bits. Near-collision mass (weight<=2, 2^32 draws, binomial 529): Y14 scan 1230 (2.3x, with 8 exact hits), Y4 488 (0.92x), Y9 32 (0.06x); the E1-side words Y1,Y6,Y12,w12 give no D1 of weight <=4 (min weight 6,5,7,6) and w5 none of weight <=8.'
        q3 = 'Exact fibre sizes of {D1=0} over each of 9 single words (2^32 values, one base): Y1 0, Y6 0, Y12 0, w12 0, w5 0, Y4 0, Y9 0, Y14 8, w8 0 (sum 8 vs 9 for a uniform mean of 1 per word).'
        q4 = 'Classes: {Y1,w12} equivalent (identical counts and histograms); Y6, Y12, w5 distinct; E3-side Y4, Y9, Y14, w8 distinct. Best measured word for D1=0 on this base: Y14 (8 hits, weight<=2 mass 2.3x binomial).'
    else:
        q2 = 'D3=0 never occurs (0 hits in 9 scans). Minimum weights seen: Y1 1 (5 values), Y6 1 (73), Y12 2, w12 1 (5), w5 5, Y4 1 (1), Y9 5, Y14 6, w8 7. Weight<=2 mass (binomial 529): Y6 2247 (4.2x), Y1 381 (0.7x), Y4 4 (0.01x).'
        q3 = 'Exact fibre sizes of {D3=0} over each of 9 single words (2^32 values, one base): all 0 (sum 0 vs 9 for a uniform mean of 1 per word).'
        q4 = 'Classes: {Y1,w12} equivalent (identical counts and histograms); Y6, Y12, w5 distinct; E3-side Y4, Y9, Y14, w8 distinct. No word hit D3=0 on this base; the closest low-weight mass is E1-side Y6 (weight 1: 73 values, weight<=2: 2247).'
    rec(cell(2), obj, 'Necessity of exact equality: relax it to a low-weight difference and recount the outcome mass', q2,
        M1 + 'Reading: the pair difference is far from uniform per variable (images restricted: some weights unreachable, others 2-4x over binomial) on a single base. ' + LIM)
    rec(cell(3), obj, 'Degrees of freedom: exact count over carries of D%d=0 along one free word' % w, q3,
        M1 + 'Redundancy: Y1 and w12 give identical results because E1 reads them only through the sum Y1+Y6+w12 in the first addition: one degree of freedom, not two. Uniform expectation is mean 1 per word; D3 gives 0 in all 9 (e^-9 = 1.2e-4 if Poisson(1) independent) and D1 gives 8 in one word, so both look non-Poisson, but this is one base: a second base is needed before any claim. ' + LIM)
    rec(cell(4), obj, 'Alternatives: which single free word to scan for D%d (equivalence classes, best variable)' % w, q4, M1 + LIM)
for r in recs:
    cell = r.pop('_cell')
    fn = os.path.join(out, cell.replace('|', '_') + '.json')
    json.dump(r, open(fn, 'w', encoding='utf-8'), indent=1)
    add_cell.validate(json.load(open(fn, encoding='utf-8')), add_cell.load())
    print('ok', fn)
