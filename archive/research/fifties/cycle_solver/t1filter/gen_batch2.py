'''Batch instances, LAYOUT 2 (the production layout of the t1filter solver).
Free-word coordinates B2 = (D2.b1, K3.d1, S15, X4 | D3.a1, K0.b1), loop variable g = C0.b1 (valid k=1 design on the exact
relation set, same 21-equation loop and same 14 loop parameters as split_e3/ev.py DESIGN; design2.py).
A BATCH holds E3 = (Y4,Y9,w8) and D2.b1, K3.d1, S15, X4; the two words D3.a1, K0.b1 vary per proposal (2^64 proposals per
batch).  Then the table inputs Y4, X4, X8, w6, S11 (and X13) are batch constants (asserted); w5 = f(S14) varies.
Batch kinds:
  N : E3 + held words from a real point (ev.real_point, T1 = 0); proposal 0 is the real point (root with T1 = 0, must
      NOT be returned); other proposals random (D3.a1, K0.b1).
  R : E3 from a real point; held words random; proposals random.
  P : planted: basis words random except Y4 from a real point (keeps the E3 class), T1 = t uniform in [1,2^19),
      triangular propagation on the exact relations; proposal 0 is that point (root with T1 = t).
Outputs as gen_batch.py; the json 'B' field holds the ORIGINAL design's six B words (for compare.py / ev.Design.run).
usage: python gen_batch2.py <tag> <nN> <nR> <nP> <per_batch> <seed>'''

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

import sys, json, random
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3'))
import ev
d0 = ev.Design(*ev.DESIGN)
F = ('Y4', 'Y9', 'w8'); HELD2 = ('D2.b1', 'K3.d1', 'S15', 'X4'); VAR2 = ('D3.a1', 'K0.b1')
d2 = ev.Design(F, HELD2 + VAR2, 'C0.b1')
assert d2.params == d0.params
BATCH_CONST = ('Y4', 'Y9', 'X4', 'X8', 'w6', 'S11', 'X13')
PROP_VARS = ('S12', 'S1', 'X0', 'X5', 'K1.b1', 'K1.d1', 'X9', 'S6')
ORD, CHK, KN = ev.order(set(ev.rels.BASIS) | {'T1'})
assert KN >= set(ev.WORDS)
def planted_point(rnd, t1):
    v = {w: rnd.getrandbits(32) for w in ev.rels.BASIS}; v['Y4'] = ev.real_point(rnd)['Y4']; v['T1'] = t1
    for i, w in ORD: v[w] = ev.solve1(ev.REL[i], w, v)
    assert all(ev.holds(r, v) for r in ev.REL)
    return v
if __name__ == '__main__':
    tag = sys.argv[1]; nN, nR, nP, per, seed = map(int, sys.argv[2:7])
    rnd = random.Random(seed)
    inst, batches = [], []
    for bid, kind in enumerate(['N'] * nN + ['R'] * nR + ['P'] * nP):
        v = planted_point(rnd, rnd.randrange(1, 1 << 19)) if kind == 'P' else ev.real_point(rnd)
        E3 = {w: v[w] for w in F}
        held = {w: v[w] for w in HELD2} if kind in 'NP' else {w: rnd.getrandbits(32) for w in HELD2}
        consts = None; ids = []
        for j in range(per):
            planted = (j == 0 and kind in 'NP')
            var = {w: v[w] for w in VAR2} if planted else {w: rnd.getrandbits(32) for w in VAR2}
            pv = d2.pre_values(dict(E3, **held, **var))
            bc = tuple(pv[w] for w in BATCH_CONST)
            if consts is None: consts = bc
            assert bc == consts, 'batch constant moved'
            pid = len(inst); ids.append(pid)
            inst.append({'id': pid, 'batch': bid, 'kind': kind, 'planted': planted, 'E3': E3,
                         'B': {w: pv[w] for w in d0.B}, 'B2': dict(held, **var),
                         'g_true': v[d0.g] if planted else None, 'T1_true': v['T1'] if planted else None,
                         'params': [pv[p] for p in d0.params], 'prop': [pv[w] for w in PROP_VARS]})
        batches.append((bid, kind, consts, ids))
    with open('inst_%s.txt' % tag, 'w', newline='\n') as f:
        for it in inst: f.write('%d %s\n' % (it['id'], ' '.join('%08x' % x for x in it['params'])))
    with open('batch_%s.txt' % tag, 'w', newline='\n') as f:
        f.write('%d\n' % len(batches))
        for bid, kind, consts, ids in batches:
            f.write('B %d %d %s\n' % (bid, len(ids), ' '.join('%08x' % x for x in consts)))
            for pid in ids: f.write('I %d %s\n' % (pid, ' '.join('%08x' % x for x in inst[pid]['prop'])))
    json.dump(inst, open('inst_%s.json' % tag, 'w'))
    w5s = {}
    for it in inst: w5s.setdefault(it['batch'], set()).add(ev.Design(*ev.DESIGN).pre_values(dict(it['E3'], **it['B']))['w5'])
    print('batches', len(batches), 'instances', len(inst), 'planted', sum(i['planted'] for i in inst),
          '| distinct w5 per batch (min):', min(len(s) for s in w5s.values()))
