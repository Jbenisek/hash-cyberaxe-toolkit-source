'''Batch instances for the t1filter solver (design of split_e3/ev.py: F = Y4,Y9,w8; B = D2.b1,D3.a1,K0.b1,K3.d1,S14,S15;
loop variable g = C0.b1; T1 = K1.a1 ^ rol(K1.d1,16) computed).
A BATCH holds the five words D2.b1, D3.a1, K3.d1, S14, S15 (and E3) fixed and varies K0.b1 only. Then the upstream
parameters of the loop (Y4, X4, X8, w6) and S11, X13, X9, S6 are batch constants (asserted below).
Batch kinds:
  N  : E3 and the five held words from a real point (ev.real_point, T1 = 0); proposal 0 is the real point itself
       (its g is a root with T1 = 0, which must NOT be returned since T1 = 0 is outside [1,2^19)); others random K0.b1.
  R  : E3 from a real point, the five held words random (as gen.py draws B), K0.b1 random.
  P  : planted: a full outer point built from the 8 basis words + T1 = t, t uniform in [1,2^19) (exact relation set,
       triangular propagation); E3 and held words from it; proposal 0 is that point (root g_true with T1 = t in range).
Outputs (tag = argv): inst_<tag>.txt (format of split_e3/solve: id + 14 params), batch_<tag>.txt (C solver input),
inst_<tag>.json (metadata).  usage: python gen_batch.py <tag> <nN> <nR> <nP> <per_batch> <seed>'''

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
M = ev.M
d = ev.Design(*ev.DESIGN)
HELD = ('D2.b1', 'D3.a1', 'K3.d1', 'S14', 'S15')
VAR = 'K0.b1'
BATCH_CONST = ('Y4', 'Y9', 'X4', 'X8', 'w6', 'S11', 'X13', 'X9', 'S6')
PROP_VARS = ('S12', 'S1', 'X0', 'X5', 'K1.b1', 'K1.d1')
# planted points: propagate from the 8 basis words + T1
BASIS = list(ev.rels.BASIS) + ['T1']
ORD, CHK, KN = ev.order(set(BASIS))
assert KN >= set(ev.WORDS), 'basis+T1 not triangular'
def planted_point(rnd, t1):
    v = {w: rnd.getrandbits(32) for w in ev.rels.BASIS}; v['T1'] = t1
    for i, w in ORD: v[w] = ev.solve1(ev.REL[i], w, v)
    assert all(ev.holds(ev.REL[i], v) for i in CHK) and all(ev.holds(r, v) for r in ev.REL)
    return v
def pre_all(start):
    '''all words that do not depend on g (pre part), from E3 + B'''
    return d.pre_values(start)
if __name__ == '__main__':
    tag = sys.argv[1]; nN, nR, nP, per, seed = map(int, sys.argv[2:7])
    rnd = random.Random(seed)
    inst, batches = [], []
    kinds = ['N'] * nN + ['R'] * nR + ['P'] * nP
    for bid, kind in enumerate(kinds):
        if kind == 'P':
            t1 = rnd.randrange(1, 1 << 19); v = planted_point(rnd, t1)
        else:
            v = ev.real_point(rnd)
        E3 = {w: v[w] for w in d.F}
        held = {w: v[w] for w in HELD} if kind in 'NP' else {w: rnd.getrandbits(32) for w in HELD}
        consts = None; ids = []
        for j in range(per):
            k0 = v[VAR] if (j == 0 and kind in 'NP') else rnd.getrandbits(32)
            start = dict(E3, **held); start[VAR] = k0
            pv = pre_all(start)
            bc = tuple(pv[w] for w in BATCH_CONST)
            if consts is None: consts = bc
            assert bc == consts, 'batch constant moved'
            pid = len(inst); ids.append(pid)
            planted = (j == 0 and kind in 'NP')
            inst.append({'id': pid, 'batch': bid, 'kind': kind, 'planted': planted, 'E3': E3,
                         'B': dict(held, **{VAR: k0}), 'g_true': v[d.g] if planted else None,
                         'T1_true': v['T1'] if planted else None,
                         'params': [pv[p] for p in d.params], 'prop': [pv[w] for w in PROP_VARS]})
        batches.append((bid, kind, consts, ids))
    with open('inst_%s.txt' % tag, 'w', newline='\n') as f:
        for it in inst: f.write('%d %s\n' % (it['id'], ' '.join('%08x' % x for x in it['params'])))
    with open('batch_%s.txt' % tag, 'w', newline='\n') as f:
        f.write('%d\n' % len(batches))
        for bid, kind, consts, ids in batches:
            f.write('B %d %d %s\n' % (bid, len(ids), ' '.join('%08x' % x for x in consts)))
            for pid in ids: f.write('I %d %s\n' % (pid, ' '.join('%08x' % x for x in inst[pid]['prop'])))
    json.dump(inst, open('inst_%s.json' % tag, 'w'))
    print('params', d.params); print('batch consts', BATCH_CONST, 'proposal vars', PROP_VARS)
    print('batches', len(batches), 'instances', len(inst), 'planted', sum(i['planted'] for i in inst))
