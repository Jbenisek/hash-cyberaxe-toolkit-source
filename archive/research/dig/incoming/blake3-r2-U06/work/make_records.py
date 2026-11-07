
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
D = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming/blake3-r2-U06')
EV = ("research/dig/incoming/blake3-r2-U06/work/b3lib.py; research/dig/incoming/blake3-r2-U06/work/validate_b3.py (+validate_b3.out); "
      "research/dig/incoming/blake3-r2-U06/work/scan_m01.py (+scan_m01.out.json)")
QS = {
 'Q1': "Difference and condition count on this message word of pkgB3U (A vs B; conditions on the word value)?",
 'Q2': "Is the zero difference / the exact value of this word necessary for the Lemma H event?",
 'Q3': "How many degrees of freedom does this word carry (exact)?",
 'Q4': "Are there alternative treatments of this word (other differences, counter-absorbed difference, other values)?",
}
role = {
 0: "w0 = K0 first message word; a middle line in the root instance (function of the six outer words and X2, Section 4), in the claim's counter instance (Section 8) the free trial word fixed by c1 with the counter t solved from K0's second assignment. Read again only by C2 (fifth assignment, Y2).",
 1: "w1 = K0 second message word; a middle line in the root instance, in the counter instance w1 = S0 - K0.a1 - K0.b1 follows from w0. Read again only by E0 (message word of the first assignment).",
}
base = dict(hash='blake3-r2', row_i=None, row_j=None, object=None, source='our workflow: scan-once', own_test=True,
            evidence=EV, date='2026-10-12', lever=False, gain_bits=0.0, gain_basis='T')
def rec(w, q, status, labels, number, notes):
    r = dict(base)
    r['id'] = 'blake3-r2|m%d|msgword|%s' % (w, q)
    r['object'] = 'pkgB3U message word m%d (w%d)' % (w, w)
    r['question'] = QS[q]
    r['status'] = status; r['labels'] = labels; r['number'] = number
    r['notes'] = ('Universe cell blake3-r2|m%d|msgword|%s (unit blake3-r2-U06). Class: FREE (not pinned w4, not cancelling w5, not forced constant X3/X7/X11/X15). ' % (w, q)) + role[w] + ' ' + notes
    r['topic'] = 'b3r2.m%d.msgword.%s' % (w, q)
    return r
recs = []
for w in (0, 1):
    other = 'w1' if w == 0 else 'w0'
    recs.append(rec(w, 'Q1', 'BEDROCK', ['0', 'I'],
      "difference 0 bits (XOR diff of w%d between A and B = 0); conditions on the word 0 bits (all 32 bits unconstrained); 0/20000 random 8-word inputs with A[w%d] != B[w%d]; per-bit one-frequency in [0.4923, 0.5093] over 20000 (max bias 0.0093 w0 / 0.0076 w1, 3-sigma is 0.0106)" % (w, w, w),
      "Structural: A and B differ only in w4, w5 (Lemma L), so the word is shared, difference zero, and no condition is placed on the word itself; the only link to the event is that it is the inverse of K0 on (S4,S8). Own re-implementation of Sections 1-4 (Steps O,M,Y,T,S2) validated on a known answer first: 3000/3000 random inputs give X3,X7,X11,X15 = constants, Y4 = y, equal S and X for A and B, equal digest words 0,2,5,7, different words in the other four, and A,B differ only in w4,w5. Row has no condition, so BEDROCK by structure; the numeric check is own_test."))
    recs.append(rec(w, 'Q2', 'SAMPLED', ['0'],
      "0 of 6000 differences in B only (3000 contexts, one random bit-flip + one random delta each) keep digest words 0,2,5,7 equal; all 8 of 8 digest words differ in every one (min 8); changing the value of w%d in A alone (nonzero XOR) keeps the admissible constants X3,X7,X11,X15 in 0/3000. 95%% upper bound on the keep rate about 5e-4 (rule of three)" % w,
      "Necessary: a difference in this word reaches %s, whose output goes into E%d (round 1 call on lanes 2,7,8,13 for w0 / lanes 0,5,10,15 for w1), which breaks the zero difference that Lemma H needs for digest words 0,2,5,7. The test is a sample (hypothesis: structural reason above), not a proof; for the exact value, any change of w%d with the rest fixed destroys the pinned X constants (structure: K0 is an exact bijection, Q3)." % (('C2 (Y2)' if w == 0 else 'S0 and E0'), 2 if w == 0 else 0, w)))
    if w == 0:
        q3n = ("w0 is 32 bits marginally: within a context w0 <-> X2 is a bijection (2^24 consecutive X2: 16,777,216 distinct w0; 2^24 random distinct X2: 16,777,216 distinct w0). w1 is NOT injective in X2 (16,740,360 / 16,744,446 distinct of 2^24, which is the random-function collision rate; expected about 16,744,448), so (w0,w1) is one 32-bit curve per context (distinct pairs 2^24 of 2^24). Pair (w0,w1) <-> (S4,S8) is an exact bijection of 2^64 (200000/200000 both ways); every target pair has a context (20000/20000 constructed, S9 solved from S4 and X2 from S8, full forward check incl. Lemma H); fibre per pair = 6 free words (C0.c1, C0.d1, D3.d1, S15, w5, y) = 2^192 of the 2^256 admissible blocks. Counter instance: w0 free 32 bits (w0 -> K0.a1 -> t is a bijection, 100000/100000 forward K0 checks with solved t), w1 and t follow.")
        q3note = "Exact accounting: 2^256 admissible blocks (Lemma T2d, 8 free words) = 2^64 for (w0,w1) times 2^192; the 2^192 is from the construction (one S9 and one X2 solve per target), verified on samples of targets, not by enumeration of 2^192. w0 and w1 together use 64 of the 256 bits; they are not additional to the eight words."
    else:
        q3n = ("w1 carries 32 bits marginally but is determined by w0 in a context and by (S4,S8) globally: w1 as a function of X2 is not injective in a context (16,740,360 distinct of 2^24 consecutive X2; 16,744,446 for random), pair injective. Pair (w0,w1) <-> (S4,S8) exact bijection of 2^64 (200000/200000 both ways); fibre per pair 2^192 (6 free words), see the w0 cell for the 20000/20000 constructive targets. Counter instance: w1 = S0 - K0.a1 - K0.b1 follows from w0 (100000/100000 forward checks), 0 extra bits.")
        q3note = "Exact accounting as for m0: w1 adds no dof beyond (w0,w1) = 64 bits of the 256; given w0 and the context, w1 is a function (it is the second inverse line of K0, Fact 1)."
    recs.append(rec(w, 'Q3', 'COMPUTED', ['I'], q3n, q3note))
    recs.append(rec(w, 'Q4', 'SAMPLED', ['I', 'Z'],
      "alternatives for (w0,w1) with the same K0 output (S4,S8): exactly 1 (K0 inverse, 200000/200000). Counter-absorbed difference (t_B = t_A ^ a1_A ^ a1_B, w1' compensated so K0 outputs S0,S4,S8,S12 are equal): K0 states equal 2000/2000 but Lemma H kept 0/2000, all 8 of 8 digest words differ (min 8)",
      "Alternatives tested: (a) other values of the pair: none (bijection); (b) a w%d difference absorbed by differing chunk counters in A and B (different prefixes F): K0 is neutralised but the difference reappears in %s, so the 4 equal digest words are lost: Z (no gain), sample of 2000 contexts, flags 3, counters random. (c) only open degree of freedom is the choice of context X2 / c1 (2^32 choices, same event, a free search variable, already used). Not tested: differences in both w0 and w1 jointly with a hand-designed cancellation inside C2/E0/E2." % (w, 'C2 (Y2, then E2)' if w == 0 else 'E0 (message word)')))
for r in recs:
    # keep exact-count claim of w1 differences correct
    p = os.path.join(D, r['id'].replace('|', '_') .replace('_msgword', '') + '.json')
    json.dump(r, open(p, 'w'), indent=1)
    errs = add_cell.validate(json.load(open(p)), add_cell.load())
    print(os.path.basename(p), errs)
