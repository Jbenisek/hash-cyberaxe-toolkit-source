
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
base = 'research/dig/incoming/blake3-r2-U12/work/'
ev = lambda *f: '; '.join(base + x for x in f) + '; research/dig/incoming/blake3-r2-U06/work/b3lib.py (own construction copy)'
common = dict(hash='blake3-r2', row_i=None, row_j=None, source='our workflow: scan-once', own_test=True, date='2026-10-12', lever=False, gain_bits=None)
R = []
def rec(w, q, obj, question, labels, status, number, evid, notes, topic):
    cid = f'blake3-r2|{w}|msgword|{q}'
    d = dict(common, object=obj, question=question, labels=labels, status=status, number=number, evidence=evid,
             notes=f'Universe cell {cid}. ' + notes, topic=topic)
    R.append((cid, d))
Q = {'Q1': 'Q1 difference/condition count at this word', 'Q2': 'Q2 necessity: relax the condition, recount outcome mass',
     'Q3': 'Q3 degrees of freedom (exact count)', 'Q4': 'Q4 alternative outcomes / carry patterns and whether they reach the same later differences'}
o12 = 'message word m12 (w12; read by D2.a1 in round 0 and E1.a1 in round 1; free, solved from X2)'
o13 = 'message word m13 (w13 = W13 = 0x0007c006; read by D2.a2 in round 0 and C3.a2 in round 1; pinned)'
rec('m12','Q1',o12,Q['Q1'],['N'],'COMPUTED',
 'Difference A vs B: 0 (w12 identical in the 55- and 63-byte block; 0 of 20000 builds differ). Conditions on the word itself: 0 bits (w12 = D2.a1 - S2 - S7 is solved, not tested; every one of 2^32 values is reached, see Q3). The calls that read it are difference-free: D2 outputs (X2,X7,X8,X13) equal in A and B and E1.a1 = Y1+Y6+w12 equal, 3000/3000.',
 ev('scan_m1213.py','scan_m1213.out.json'),'Structure: free word, bytes 0-54 of the message are unconstrained (proof.md 3.1). Bit bias of w12 over 20000 builds <= 0.0077 (sampling noise).','blake3-r2 m12 word')
rec('m13','Q1',o13,Q['Q1'],['S'],'COMPUTED',
 'Difference A vs B: 0 (20000/20000 builds have w13 = W13 = 0x0007c006 in both blocks; top byte 0 in all). Conditions on the word: ONE value out of 2^32 passes the condition set "C3 on (X3,X7,X11,X15) with w4=W4 vs W4\' returns the same d and b outputs" (exhaustive 2^32 count, 35 s C program): 32 bits of condition; the honest-string condition (top byte of w13 = 0, byte 55 of the 55-byte message) is a further 8 of those bits at the message level, 2^24 candidates, still 1 solution.',
 ev('w13enum.c','w13enum_out.txt','scan_m1213.py','scan_m1213.out.json'),'Reproduces Fact P of proof.md 3.2 (A: a2=8127c181 d2=bbfbdffe c2=7af77f38 b2=76f7aefd; B: a2=7edf3e7e c2=850000c3, same d2,b2). XOR difference at C3: a2 fff8ffff, c2 fff77ffb.','blake3-r2 m13 word')
rec('m12','Q2',o12,Q['Q2'],['N'],'SAMPLED',
 'No condition group on the word, nothing to relax. Control (what the free solve protects): shifting w12 by a random odd amount in both blocks without re-solving keeps (X3,X7,X11,X15) in 0/3000 and gives digest words 0,2,5,7 equal in 0/12000 (one-sided 95% bound < 1e-3 per trial); with the solve (w12 from X2) 3000/3000 blocks are admissible and Lemma H holds.',
 ev('scan_m1213.py','scan_m1213.out.json'),'The word is not a constraint but a dependent: X7 = D2.b2 depends on w12, so w12 is pinned by X7 given the other seven outer words; this is the solve of proof.md Section 4, not a condition to relax.','blake3-r2 m12 word')
rec('m13','Q2',o13,Q['Q2'],['S'],'COMPUTED',
 'Exact outcome mass of the condition on w13 over all 2^32 values: d-output equal 16 values, b-output equal 30 values, both 1 (W13 only). Relaxed to one group: rebuilt blocks with each of the 15 d-only and 29 b-only values (admissible X constants 150/150 each) give digest words 0,2,5,7 equal in 0 of 150 each, while W13 gives them in 150/150: both groups are necessary. Changing w13 in both blocks without re-solving: constants kept 0/3000, digest equal 0/12000. Top-byte-zero group: 2^24 of 2^32 values, of the 15 d-only values 8 (0x8000c006..0x8007c006) violate it.',
 ev('w13enum.c','w13enum_out.txt','scan_m1213.py','scan_m1213.out.json'),'d-only list: 0000c006..0006c006, 8000c006..8007c006 (15 besides W13); b-only list: 0007bec6.. etc (29). Relaxing never adds a usable member.','blake3-r2 m13 word')
rec('m12','Q3',o12,Q['Q3'],['N'],'COMPUTED',
 '32 bits: w12 = X2 + c (affine, c fixed by the other seven words) is a bijection of the free outer word X2; verified: w12 - X2 takes 1 value in 40 contexts x 50 X2 values, 2^24 consecutive X2 give 2^24 distinct w12, and 3000/3000 built blocks are admissible with Lemma H holding. No carry restriction (a1 = S2+S7+w12 is a plain addition). Residual spread over X2 (4096 values, others fixed): 4096 distinct residuals, mean weight 63.6/128, min 41, none zero.',
 ev('scan_m1213.py','scan_m1213.out.json'),'Exact count of w12 values = 2^32 (all reached) for fixed other parameters; one of the eight outer words of the construction.','blake3-r2 m12 word')
rec('m13','Q3',o13,Q['Q3'],['S'],'COMPUTED',
 '0 bits: exactly 1 value (0x0007c006) of 2^32 (also 1 of the 2^24 with top byte zero) satisfies the condition; the construction places no other freedom on w13 (given w13, w12 and the rest re-solve through D2.a1 = X2 - D2.b1 - w13).',
 ev('w13enum.c','w13enum_out.txt','scan_m1213.py'),'Exhaustive over 2^32 for the fixed constants X3,X7,X11,X15,W4,W4\'. A different (X3,X7,X11,X15,W4) would move the solution; that is a different construction, not tested here.','blake3-r2 m13 word')
rec('m12','Q4',o12,Q['Q4'],['N','Z'],'LOCAL_ONLY',
 'No alternative carry pattern at the word: A and B share w12, so D2 and E1.a1/E1.d1 are identical (3000/3000). The only place w12 shapes a difference is E1 (c1 = Y11 + d1(w12), additive difference of Y11 fixed): exhaustive 2^32 sweep of w12 through E1 for one real pair (Y11A=7b0d3b38? see file; w5 differs by 8): XOR difference of the four E1 outputs is never zero in any word (0 of 2^32 for each of dA2,dB2,dC2,dD2), mean weight 60.4 of 128, minimum 32 (at w12=0ef33c2d), no value with <=30. So every w12 reaches a nonzero, different later difference; none cancels a lane.',
 ev('e1sweep.c','e1sweep_out.txt','scan_m1213.py','scan_m1213.out.json'),'LOCAL_ONLY: one pair context (Q4_ctx in scan_m1213.out.json), E1 window only, not carried to the digest R. The minimum weight 32 is one number for one context, not a lever.','blake3-r2 m12 word')
rec('m13','Q4',o13,Q['Q4'],['S','Z'],'COMPUTED',
 'No alternative outcome: the only w13 with the same d and b outputs for w4=W4 and w4=W4\' is W13 (1 of 2^32). Near misses exist (15 d-only, 29 b-only) but none keeps digest words 0,2,5,7 (0 of 150 rebuilt blocks each); at W13 the difference is the fixed pattern (a2 xor fff8ffff, c2 xor fff77ffb) and Y3,Y11 differ with Y7,Y15 equal in 3000/3000 blocks. w13 is also read by D2.a2, which is difference-free (outputs equal 3000/3000).',
 ev('w13enum.c','w13enum_out.txt','scan_m1213.py',
'scan_m1213.out.json'),'Same later difference at every admissible instance, because the admissible set is a single point.','blake3-r2 m13 word')
ctx = json.load(open('scan_m1213.out.json'))['Q4_ctx']
for cid, d in R:
    d['number'] = d['number'].replace('Y11A=7b0d3b38? see file; ', 'Y11A=%d, Y11B=%d; ' % (ctx['Y11A'], ctx['Y11B']))
    fn = '../' + cid.replace('|', '_') + '.json'
    json.dump(d, open(fn, 'w'), indent=1)
    add_cell.validate(json.load(open(fn)), add_cell.load()); print('ok', fn)
