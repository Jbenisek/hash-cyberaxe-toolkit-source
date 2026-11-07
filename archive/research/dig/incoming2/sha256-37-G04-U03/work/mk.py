
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
D = os.path.dirname(os.path.abspath(__file__)) + '/..'
W = 'research/dig/incoming2/sha256-37-G04-U03/work/'
EV = '; '.join([W + 'scan.c', W + 'dep.out', W + 'w17_base.out', W + 'bucket_base.out', W + 'real_base.out', W + 'w17_fix_*.out', W + 'bucket_fix_*.out'])
words = {
 'E-3': dict(nm='E_-3', idx=1, w='W0,W1', fix=[('0', '00000000'), ('315a2db3 (published)', '315a2db3')],
   b16=('0.640', '0.122'), u17=('0.911', '0.039'),
   f16={'00000000': '2^-12.0062 [2^-12.0173, 2^-11.9952]', '315a2db3': '2^-12.0028 [2^-12.0139, 2^-11.9917]'},
   f17={'00000000': '2^-13.0015 [2^-13.0236, 2^-12.9794]', '315a2db3': '2^-12.9839 [2^-13.0059, 2^-12.9620]'},
   real=('0.266', '0.593', '0.116'), rb=('0.187', '0.303')),
 'E-2': dict(nm='E_-2', idx=2, w='W0,W1,W2', fix=[('5ed877a8 (published)', '5ed877a8'), ('ffffffff', 'ffffffff')],
   b16=('0.785', '0.650'), u17=('0.612', '0.021'),
   f16={'5ed877a8': '2^-12.0005 [2^-12.0116, 2^-11.9895]', 'ffffffff': '2^-12.0096 [2^-12.0207, 2^-11.9985]'},
   f17={'5ed877a8': '2^-12.9959 [2^-13.0180, 2^-12.9739]', 'ffffffff': '2^-13.0086 [2^-13.0308, 2^-12.9865]'},
   real=('0.398', '0.235', '0.923'), rb=('0.183', '0.914')),
 'E-1': dict(nm='E_-1', idx=3, w='W0,W1,W2,W3', fix=[('0', '00000000'), ('78a7f752 (published)', '78a7f752')],
   b16=('0.789', '0.809'), u17=('0.836', '0.321'),
   f16={'00000000': '2^-12.0110 [2^-12.0220, 2^-11.9999]', '78a7f752': '2^-12.0044 [2^-12.0155, 2^-11.9934]'},
   f17={'00000000': '2^-13.0210 [2^-13.0432, 2^-12.9987]', '78a7f752': '2^-13.0046 [2^-13.0268, 2^-12.9825]'},
   real=('0.946', '0.533', '0.859'), rb=('0.843', '0.958')),
}

def rec(wk, q, status, labels, obj, question, number, notes):
    cid = 'sha256-37|CV.%s|CV|%s' % (wk, q)
    return cid, dict(hash='sha256-37', row_i=None, row_j=None, object=obj, question=question, labels=labels, status=status, number=number,
      source='our workflow: scan-once-wave2', own_test=True, evidence=EV, date='2026-10-12', lever=False, gain_bits=0.0, gain_basis='q3',
      notes='universe cell %s. ' % cid + notes)

tool = ("Tool scan.c (ours; links traillab traillab.c unchanged; adapted from retest/close37/job5/job5.c). Validated on known answers before use: "
 "R16 table rebuilt = 1,052,672 (u,l) pairs / 1,042,240 distinct u / 28 of 32 l (equals proof 6.2); Lemma 4.1 map on the published CV reproduces the published W0..W7; "
 "P(row17|row16) sampler gave 2^-13.0067 [2^-13.0178, 2^-12.9956] vs the known SMC stage 2^-13.000 on 65,232 forward-verified (CV1,l) passes; "
 "512 recorded passes re-verified from CV1 by forward stepping rows 0..17 on both members, 0 failures. ")
out = []
for wk, d in words.items():
    n = d['nm']; f = d['fix']
    out.append(rec(wk, 'Q1', 'COMPUTED', ['D', 'I'], 'CV word %s (chaining-value word, common to both members)' % n,
     'How many values of %s does the ordinary-collision attack use, and where does it enter?' % n,
     '%s: no cell, no condition, dCV=0 (rows -4..-1 carry none in chi37). The gate (A_-1 in F7, A_-2 via F6; 5.98 + 3.90 bits) does not touch it: 2^32 of 2^32 values pass; 0 of 200,000 random trials changed W6 or W7 when %s changed. It enters Lemma 4.1 only through %s (own-word offset exact: %s += d moves W%d by -d, 0 violations of 3000); W16.. follow by the real expansion. Free 32-bit coordinate, 0 bits used by the gate.' % (n, n, d['w'], n, d['idx']),
     tool + 'Method (dep): 200,000 random CVs and a0 in G, +delta on one CV word, fraction of W0..W7 that change (dep.out; %s row has W4..W7 = 0).' % n))
    out.append(rec(wk, 'Q2', 'LOCAL_ONLY', ['D', 'Z'], 'CV word %s replaced by a constant' % n,
     'Is %s necessary: replace it by a fixed value and recompute the row-16 and row-16/17 rates?' % n,
     'Replace %s := %s: row-16 any-l rate per good pair %s, row17|row16 %s; %s := %s: %s, %s. References: table 2^-12.0087 per good pair, SMC stage 2^-13.000; 95%% Wilson intervals; 2^28 good pairs and 2^27 sampler draws per run. No gain and no loss: no condition on %s exists; it cannot be dropped (the first block supplies all 8 words) but its value does not matter.' % (n, f[0][0], d['f16'][f[0][1]], d['f17'][f[0][1]], n, f[1][0], d['f16'][f[1][1]], d['f17'][f[1][1]], n),
     tool + 'LOCAL_ONLY: rows 16 and 17 prefix only (row 16 by forward sampling; row 17 by W-space importance sampler over R16 entries with the 9 fixed E17 bits then a full forward check); rows 18..36 not tested. Uniformity of the other CV words under each replacement also flat (p 0.03 to 0.999 over the 12 fixed-value runs).'))
    out.append(rec(wk, 'Q3', 'LOCAL_ONLY', ['D', 'I', 'Z'], 'CV word %s freedom given the gate and rows 16-17' % n,
     'How many bits of %s remain free given the gate, row 16 and row 17?' % n,
     '32.000 bits at every stage tested, no loss measurable. Row-16 pass-rate homogeneity over 256 buckets of %s: p = %s (>>24) / %s (&0xff) on 260,318 passes of 1.07e9 good pairs (max bucket ratio about 1.10, inside noise). Rows 16&17 jointly (65,232 forward-verified passes): byte entropy deficit at the sampling floor, uniformity p = %s (>>24) / %s (&0xff). Structure: the events depend on W0,W1,W2,W6,W7 and %s = (function of W%d..W7) - W%d.' % (n, d['b16'][0], d['b16'][1], d['u17'][0], d['u17'][1], n, d['idx'] + 1, d['idx']),
     tool + 'One of the 8 low-p-side tests per word family (low byte p = %s) was not repeated in the 12 fixed-value runs, so it is read as scatter. Gain 0. LOCAL_ONLY: prefix rows 16-17; the full event (about 2^-74) cannot be sampled, rows 18+ not tested.' % d['u17'][1]))
    out.append(rec(wk, 'Q4', 'LOCAL_ONLY', ['D', 'Z'], 'CV word %s source: real first blocks vs uniform CV' % n,
     'Is there an alternative to the uniform-CV premise for %s (real first blocks of F_37, other signings)?' % n,
     'Real first blocks CV1 = F_37(IV,M0), 536,561,417 blocks (2^29.0): %s top byte uniform p = %s; among 569,856 good pairs (rate 2^-9.8789 [2^-9.8827, 2^-9.8752] vs exact 2^-9.8796) %s uniform p = %s (>>24) / %s (&0xff); row-16 homogeneity p = %s / %s; row-16 passes 111 = 2^-12.3258 [2^-12.5938, 2^-12.0578] (table 2^-12.0087 sits just outside this 95%% interval; close37 job5 had 137 on the same model, inside). No bias in %s at this size, so no steering from the first-block side. Signings: dE=0 by definition; a nonzero chaining-value difference is another characteristic, not tested.' % (n, d['real'][2], n, d['real'][0], d['real'][1], d['rb'][0], d['rb'][1], n),
     tool + 'LOCAL_ONLY: first-block uniformity measured to 2^29 blocks, row 16 only; H1 evidence beyond 2^36 blocks not provided. The nonzero-dCV alternative is the unmapped CV.diff cell.'))
ex = add_cell.load(); bad = 0
for cid, r in out:
    p = D + '/' + cid.replace('|', '_').replace('.', '_') + '.json'
    json.dump(r, open(p, 'w', encoding='utf-8'), indent=1)
    e = add_cell.validate(json.load(open(p, encoding='utf-8')), ex)
    if e: bad += 1; print(cid, e)
print(len(out), 'records, invalid', bad)
