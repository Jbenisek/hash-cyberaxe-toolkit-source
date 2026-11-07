
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

import json, math, sys, os
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
D = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/blake3-r2-G05-U02')
t2 = json.load(open(os.path.join(D, 'work', 't2_out.json')))
base = t2['IV']
def cmp(name):
    r = t2[name]; out = []
    for k in ('hits16',):
        for j, lab in enumerate(('d1', 'd3', 'd4', 'd6')):
            a, b = base[k][j], r[k][j]
            z = (b - a) / math.sqrt(max(a + b, 1))
            out.append('%s %d vs %d (z %.1f)' % (lab, b, a, z))
    return '; '.join(out), r['n']
EV = ('research/dig/incoming2/blake3-r2-G05-U02/work/b3init.py, t0_validate.py, t1_structure.py, t2_window.py, t3_special.py '
      '(own code; parametrised round-0 inverse after research/r2_half.py)')
KNOWN = ('KNOWN ANSWER first: own compress reproduces BLAKE3("") 7 rounds af1349b9...f3262 and equals hash-smash/verifier/blake3.py on 600 single-block messages at 2 and 7 rounds; '
         'at h=IV the pinned record constants (X3 29d4fa98, X7 bee3af28, X11 44036000, X15 40c58500, W4 97475638, W13 0007c006, lengths 55/63) give an exact half collision (digest words 0,2,5,7 equal) '
         'and the round-0 inverse reproduces the forward round-0 state, 0 failures in 3x400 samples (flags 3 and 11, t=0 and t=12345).')
NOT = ('Not done: the full 128-bit residual rate (2^-91 per trial class) was not re-measured; the window test is low-16-bit windows of the four residual words, '
       'not the exact outcome mass; the w14=0 / w13 top byte honest-byte conditions of the 55/63 layout were not solved in this parametrisation (w14 is derived, as in r2_half.py); '
       'the price of obtaining a non-IV h (extra block in the chunk) was not re-priced.')
def rec(i, q, status, number, notes, lever=False, gain=None):
    cell = 'blake3-r2|INIT.v%d|INIT|%s' % (i, q)
    return cell, dict(hash='blake3-r2', row_i=None, row_j=None,
        object='INIT.v%d state word v%d = h[%d] (IV[%d] in every context of the record)' % (i, i, i, i),
        question={'Q2': 'Necessity: relax or replace the value, recount the exact outcome mass',
                  'Q4': 'Alternatives: which other values / sources of the word exist and what they cost or give'}[q],
        labels=['N'] if i != 6 else ['I'], status=status, number=number, source='our workflow: scan-once-wave2', own_test=True,
        evidence=EV, date='2026-10-12', lever=lever, gain_bits=gain,
        notes='universe cell %s. %s %s %s' % (cell, KNOWN, notes, NOT), topic=cell)
recs = []
for i, nm in ((4, 'h4'), (5, 'h5'), (7, 'h7')):
    s, n = cmp(nm)
    recs.append(rec(i, 'Q2', 'LOCAL_ONLY',
        'Not necessary as IV[%d]: with h[%d] replaced by 8 random non-IV values (random t, flags 3) 2400/2400 samples keep the exact half collision and the round-0 inverse (0 failures); '
        'the pins X3,X7,X11,X15,W4,W13 and W4B-W4=+8 do not move (h[%d] feeds only K%d as its b input; it shifts message words w%s). Low-16-bit window hits of residual words over %d shared-draw samples, non-IV vs IV: %s.' % (i, i, i, i - 4, {4: '0,1', 5: '2,3', 7: '6,7'}[i], n, s),
        'Window comparison uses the same free-word draws for every h; the d3 window (digest word 3) is ~2.6x the uniform 2^-16 rate for IV and non-IV alike, so the structure is h-independent in this window. Exact status: the half collision and inverse are exact-by-construction facts checked on samples (sampled, not enumerated); the residual rate is a window only.'))
    recs.append(rec(i, 'Q4', 'LOCAL_ONLY',
        'Alternatives all valid, none gives anything: any h[%d] (tested 8 random + 10 special values incl. 0, all-ones, 0x80000000, IV+-1, IV^1, a neighbour IV word: 4400 samples, 0 failures of inverse or half collision). '
        'No value changes the count of free state words (9 plus pins) or the pins. Source alternative: a non-IV h needs a preceding block in the chunk (second-block host), which costs a compression and buys no pin/rate change here.' % i,
        'Free-word count (FREE = 9 state words in the r2_half parametrisation) is the same for every h; only the message words w%s differ by h-dependent additive/xor constants (bijective re-labelling).' % {4: '0,1', 5: '2,3', 7: '6,7'}[i]))
s, n = cmp('h6')
recs.append(rec(6, 'Q2', 'COMPUTED',
    'Necessary only through K = IV[2]+h[6] and only via bit 3 of K+W4: exact half collision for h6 mod 16 in {6..13} (8 of 16 residues, all 40 draws each) and failure for the other 8 (W4B-W4 = -8 instead of +8, so the pinned C3 outputs differ). '
    'Predicted by the rule bit3(IV2+h6+W4)=0 and matched exactly (16/16 residues). So 2^31 of 2^32 values of h6 keep the pinned advice. Window hits (valid non-IV h6 = IV[6]+16*12345) low-16 windows over %d samples vs IV: %s.' % (n, s),
    'The condition depends only on h6 mod 16, so the 16-residue sweep x 40 random upper parts is exhaustive for the rule; the count 1/2 is exact for the fixed W4. The pin pair {W4, W4+8} is usable iff bit3(K+W4)=0 for either assignment of the lengths 55/63.', lever=False))
recs.append(rec(6, 'Q4', 'LOCAL_ONLY',
    'Alternative h6 values: any h6 with bit3(IV2+h6+W4)=0 (exactly half, 2^31) keeps the pinned advice unchanged; the other half gives the -8 pin direction and kills the half collision. 10 special values (4 passing the rule): 800 samples, 0 failures. '
    'A non-IV h6 would let pin pairs {v, v+8} with bit3(K+v)=1 (the half the IV class cannot use) be used: pin pool x2 at best, priced only by an extra chunk block. No gain number measured.',
    'Possible lever to look at once: doubling the usable C3 pin pool (selection SEL / pin quality), not measured here; K enters nothing else (b1 of K2 and S10 are re-labellings).'))
os.makedirs(D, exist_ok=True)
ex = add_cell.load()
for cell, r in recs:
    fn = os.path.join(D, cell.replace('|', '_') + '.json')
    json.dump(r, open(fn, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    e = add_cell.validate(json.load(open(fn, encoding='utf-8')), ex)
    print(cell, 'OK' if not e else e)
