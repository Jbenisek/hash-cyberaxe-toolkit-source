'''Base configurations for the block harness.
  python -B make_configs.py gen  [nG] [seed]   -> poolG_cand.json + poolG_inst.txt (instance file for ./solve)
  (run ./solve poolG_inst.txt poolG_roots.txt in WSL: one exhaustive 2^32 sweep of g per candidate)
  python -B make_configs.py finish             -> configs.json (every word, every intermediate) + configs.txt (C input)
Pool S: real roots of the split_e3 GPU solver (inst_2.json / roots_2.txt, read-only): 8 per E3 tuple + every T1-valid root.
Pool G: the split_e3 generator's "generating point" mode with T1 drawn in [1, 2^19): a forward point (outer basis, Y4 in
        the class, T1, c1) whose own (Y4,Y9,w8,Y14) is the prescribed E3; confirmed by one exhaustive solver sweep that its
        g is a root of the 21-equation loop for its six free words (sibling roots recorded).'''
import sys, json, random, os
sys.dont_write_bytecode = True
from common import *   # noqa

def record(cid, pool, v, extra):
    D = [v[k] for k in FRAME_D]; O = [v[k] for k in FRAME_O]; R = real_of(v)
    for f, c in (('D', D), ('O', O), ('R', R)):
        w, chk = ref_derive(f, c)
        assert real_of(w) == R and chk == 0, (cid, f)
    ok, info = ev.verify(v, {k: v[k] for k in DESIGN.F}, v['Y14'])
    assert ok, (cid, 'split_e3 verify failed')
    obs = ref_obs(R)
    wa, wb, t = messages(R)
    tr = {'A': compress_trace(wa, t, LEN_A, FLAGS), 'B': compress_trace(wb, t, LEN_B, FLAGS)}
    return dict(id=cid, pool=pool, D=D, O=O, R=R, words={k: v[k] for k in sorted(v) if isinstance(v[k], int)},
                obs=obs, trace=tr, t1_valid=t1_ok(v['T1']), **extra)

def gen(nG, seed):
    rnd = random.Random(seed); cand = []
    while len(cand) < nG:
        c = [rnd.getrandbits(32) for _ in range(7)] + [hs.class_member(rnd.getrandbits(32) % hs.CLASS_SIZE),
                                                       rnd.randrange(1, 1 << 19), rnd.getrandbits(32)]
        v, _ = ref_derive('O', c)
        if v['T0'] == 0: continue
        cand.append({'O': c, 'E3': {k: v[k] for k in DESIGN.F}, 'B': {k: v[k] for k in DESIGN.B}, 'g': v[DESIGN.g],
                     'Y14': v['Y14']})
    with open('poolG_inst.txt', 'w', newline='\n') as f:
        for i, cd in enumerate(cand):
            pv = DESIGN.pre_values(dict(cd['E3'], **cd['B']))
            f.write('%d %s\n' % (i, ' '.join('%08x' % pv[p] for p in DESIGN.params)))
    json.dump(cand, open('poolG_cand.json', 'w'))
    print('pool G candidates', len(cand))

def read_roots(path):
    out = {}
    for line in open(path):
        p = line.split(); out[int(p[0])] = (int(p[1]), [int(x, 16) for x in p[2:]])
    return out

def finish(per_e3=8):
    cfgs = []
    # ---- pool S: split_e3 solver roots
    inst = {i['id']: i for i in json.load(open(os.path.join(SPLIT, 'inst_2.json')))}
    roots = read_roots(os.path.join(SPLIT, 'roots_2.txt'))
    taken = {}; t1v = 0
    for pid, (cnt, rs) in sorted(roots.items()):
        it = inst[pid]
        if it['gen']: continue
        for g in rs:
            start = dict(it['E3'], **it['B']); start[DESIGN.g] = g
            v, h = DESIGN.run(start)
            assert h
            valid = t1_ok(v['T1'])
            if taken.get(it['e3'], 0) >= per_e3 and not valid: continue
            v = trial_words(v, ev.c1_from_y14(v, it['Y14']))
            cfgs.append(record(len(cfgs), 'S', v, {'e3tuple': 'S%d' % it['e3'], 'inst': pid, 'roots': rs}))
            taken[it['e3']] = taken.get(it['e3'], 0) + 1; t1v += valid
    print('pool S configs', len(cfgs), 'of which T1-valid', t1v, 'per E3 tuple', taken)
    # ---- pool G: generating points with T1 in range, solver-confirmed
    cand = json.load(open('poolG_cand.json')); rG = read_roots('poolG_roots.txt'); nG = 0; sib = 0
    for i, cd in enumerate(cand):
        cnt, rs = rG[i]
        assert cd['g'] in rs, ('generating g not a solver root', i)
        sib += cnt - 1
        v, _ = ref_derive('O', cd['O'])
        cfgs.append(record(len(cfgs), 'G', v, {'e3tuple': 'G%d' % i, 'inst': i, 'roots': rs}))
        nG += 1
    print('pool G configs', nG, '(all generating g found among solver roots; sibling roots', sib, ')')
    json.dump(cfgs, open('configs.json', 'w'))
    with open('configs.txt', 'w', newline='\n') as f:
        for c in cfgs:
            f.write('%d %s %s\n' % (c['id'], c['pool'], ' '.join('%08x' % x for x in c['D'] + c['O'] + c['R'])))
    print('configs', len(cfgs), 'T1-valid', sum(c['t1_valid'] for c in cfgs))

if __name__ == '__main__':
    os.chdir(HERE)
    if sys.argv[1] == 'gen': gen(int(sys.argv[2]) if len(sys.argv) > 2 else 64, int(sys.argv[3]) if len(sys.argv) > 3 else 11)
    else: finish()
