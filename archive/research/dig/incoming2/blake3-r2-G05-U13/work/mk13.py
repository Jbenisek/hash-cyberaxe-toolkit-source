
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

import json, sys, os
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
r = json.load(open('scan13.out.json'))
OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/blake3-r2-G05-U13')
ROLE = {
 0:("forced (solved)", "w0 = Y2-C2a1-C2b1 closes the counter: tlo = ROL(K0.d1,16)^K0.a1 uses up the freedom of w0; A and B share it", ['I']),
 1:("forced (solved)", "w1 = S0-K0a1-K0b1, inverse of K0 given its prescribed outputs", ['I']),
 2:("forced (solved)", "w2 = K1a1-IV1-IV5, K1 run backwards from S9,S13 with t_hi", ['I']),
 3:("forced (solved)", "w3 = S1-K1a1-K1b1, K1 run backwards", ['I']),
 4:("pinned constant, cancelling", "constant W4 = 97475638 in A and W4' = 97475640 in B (additive difference -8); K2 reads it together with the length word v14 (55 vs 63) and overwrites v14, so the two differences cancel inside K2 (Lemma L)", ['0','C']),
 5:("cancelling (derived)", "w5 = S2-K2a1-K2b1 in A and w5' = w5+W4-W4' in B; the only word besides w4 that differs between A and B", ['C']),
 6:("free (the one free message word)", "w6 is itself a free parameter of the construction; K3a1 = IV3+IV7+w6; every other word is solved around it", ['N']),
 7:("forced (solved)", "w7 = S3-K3a1-K3b1, K3 run backwards", ['I']),
 8:("forced (pinned pair)", "w8 = D0a1-S0-S5, fixed with w9 by the 64 bits X0 and X15 (X15 pinned) of D0", ['I']),
 9:("forced (pinned pair)", "w9 = X0-D0a1-D0b1, fixed with w8 by X0 and X15", ['I']),
 10:("forced (solved)", "w10 = D1a1-S1-S6, from D1 with X11 pinned", ['I']),
 11:("forced (solved)", "w11 = X1-D1a1-D1b1, from D1 with X11 pinned", ['I']),
 12:("forced (solved)", "w12 = D2a1-S2-S7, from D2 with X7 pinned (D2a1 is a free outer word)", ['I']),
 13:("pinned constant", "constant W13 = 0007c006 (top byte 0 so the block is an honest byte string); read by the pin call C3 in round 1", ['0']),
 14:("pinned constant (zero)", "w14 = 0 fixed (honest byte string of 55/63 bytes), D3 with X3 pinned", ['0']),
 15:("pinned constant (zero)", "w15 = 0 fixed, D3 with X3 pinned", ['0']),
}
CELLS = [('K0','x',0),('K0','y',1),('K1','x',2),('K1','y',3),('K2','x',4),('K2','y',5),('K3','x',6),('K3','y',7),
 ('D0','x',8),('D0','y',9),('D1','x',10),('D1','y',11),('D2','x',12),('D2','y',13),('D3','x',14),('D3','y',15),
 ('C0','x',2),('C0','y',6),('C1','x',3),('C1','y',10)]
def desc(u):
    p = u['pert']; c = u['callstat']
    return (f"{u['call'][0]}.{u['call'][1]}: call input state equal A/B {c['call_input_state_equal_AB']}/2000, call output equal A/B {c['call_output_equal_AB']}/2000; "
            f"same-XOR-delta perturbation at this read only in both messages, no re-solve, {p['trials']} trials: round-0 pins X3,X7,X11,X15 kept {p['pins_X3_X7_X11_X15_kept']}/{p['trials']}, round-0 state X equal A/B {p['X_equal_AB']}/{p['trials']}, half-collision (digest words 0,2,5,7 equal) kept {p['lemmaH_kept']}/{p['trials']}, digest words changed vs unperturbed mean {p['digest_words_changed_vs_unperturbed_mean']:.2f}/8, digest words A/B differ mean {p['digest_words_AB_differ_mean']:.2f}/8")
for call, xy, i in CELLS:
    x = r[str(i)]; w = x['word']; u0 = x['use0']; u1 = x['use1']
    role, why, lab = ROLE[i]
    deps = [k for k, v in x['dep'].items() if v > 0.9]
    depstr = (f"depends on {len(deps)} of the 10 free parameters ({', '.join(deps)}; a random single-bit flip changes it in >0.9 of 30 trials each)" if deps else "depends on none of the 10 free parameters (constant)")
    isr1 = call.startswith('C')
    here = u1 if isr1 else u0; other = u0 if isr1 else u1
    agree = ("value agrees (same word, A==B at both reads)" if w['eqAB'] == 2000 else "value agrees between the two reads (same word); A and B differ in it at both")
    if i in (4, 13):
        roleuse1 = "the round-1 use is a read of the pin call C3 (m4 as x, m13 as y): changing it alone loses the half-collision (kept 0/600)"
    else:
        roleuse1 = "the round-1 use keeps the half-collision under a same-delta change (kept 600/600; it only re-randomises the residual digest words, the input states of those calls being equal or carrying the residual difference)"
    if w['eqAB'] == 2000:
        dv = '0 bits (identical in A and B in 2000/2000 builds)'
    else:
        dv = 'differs in 2000/2000 builds; XOR difference popcount mean %.2f (min %d, max %d)' % (w['diff_popcount_mean'], w['diff_popcount_min'], w['diff_popcount_max'])
    num = (f"Word {call}.{xy} reads m{i} ({'step q1 (mx)' if xy == 'x' else 'step q3 (my)'}); role at this use: {role}. Value as used: A-B difference {dv}; distinct values over 2000 builds {w['distinct']}; {why}; {depstr}. "
           f"THIS USE ({'round 1' if isr1 else 'round 0'}) {desc(here)}. "
           f"OTHER USE ({'round 0' if isr1 else 'round 1'}) {desc(other)}. "
           f"Two uses: {agree}; the roles differ by design: every round-0 read is pin-critical (round-0 pins kept 0/600 when the read is changed alone), while {roleuse1}. Counts are samples on the pkgB3U Sec 8 counter construction (10 free parameters, t_hi < 2^16), not exact over the whole family.")
    cid = f"blake3-r2|MSG.{call}.{xy}|MSG|Q1"
    rec = dict(hash='blake3-r2', row_i=None, row_j=None,
      object=f"read {xy} of call {call} = message word m{i} (step {'q1 (mx)' if xy == 'x' else 'q3 (my)'})",
      question="Q1 word role at this use (free / pinned / cancelling / forced) and whether the word's two uses agree",
      labels=lab, status='SAMPLED', number=num, source="our workflow: scan-once-wave2", own_test=True,
      evidence="research/dig/incoming2/blake3-r2-G05-U13/work/scan13.py; scan13.out.json; validate13.py; b3ctr.py (copied from research/dig/incoming/blake3-r2-U07/work/b3ctr.py)",
      date="2026-10-12", lever=False, gain_bits=None,
      notes=f"universe cell {cid}. Tool validated first: comp matches organizer hash-smash/verifier/blake3.py _compress on 1000 random inputs at 2 and 7 rounds (0 mismatches), the 7-round empty-input vector af1349b9 reproduced, construction pins hold 2000/2000. Counter construction of pkgB3U Sec 8; all words recomputed from the 10 free parameters via build(). Round-1 schedule is P=(2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8) applied to m. Sampled, window of the construction; no gain seen. 0/600 means one-sided 95% bound below 0.005 per trial; UNKNOWN is not UNSAT.",
      topic=cid)
    fn = os.path.join(OUT, cid.replace('|', '_') + '.json')
    json.dump(rec, open(fn, 'w', encoding='utf-8'), indent=1)
    add_cell.validate(json.load(open(fn, encoding='utf-8')), add_cell.load()); print('ok', os.path.basename(fn))
