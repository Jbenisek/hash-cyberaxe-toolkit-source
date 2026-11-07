'''Exact evaluator of the outer system with counter 2 (T1 = v13 free) from pkg13/mitm/bits/rels.py relations, for a
design (forced F, free B, solved g): propagation order, the single check, pre/loop split, numeric solve,
CUDA code for the loop, and a full verification of a solution on the real 2-round compression (compress2).'''

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

import sys, random
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/pkg13/mitm/bits'))
import rels
hs = rels.hs; M = 0xFFFFFFFF; rol = rels.rol
def ror(x, n): return rol(x, (32 - n) % 32)
REL = []
for r in rels.RELS:
    if r[0] == 'lin' and r[3] == 'K1.a1':       # K1.d1 = ROR16(T1 ^ K1.a1)  ->  K1.a1 ^ rol(K1.d1,16) ^ T1 = 0
        r = ('lin', list(r[1]) + [('T1', 0)], r[2], 'K1.a1')
    REL.append(r)
def wset(r): return {w for w in (r[1] if r[0] == 'add' else [x for x, _ in r[1]])}
WORDS = sorted(set().union(*(wset(r) for r in REL)))
def order(known):
    known, used, out, checks = set(known), set(), [], []
    ch = True
    while ch:
        ch = False
        for i, r in enumerate(REL):
            if i in used: continue
            unk = [w for w in wset(r) if w not in known]
            if len(unk) == 1:
                known.add(unk[0]); used.add(i); out.append((i, unk[0])); ch = True
            elif not unk:
                used.add(i); checks.append(i); ch = True
    return out, checks, known
def solve1(r, u, v):
    if r[0] == 'add':
        s = r[2]
        for w, c in r[1].items():
            if w != u: s += c * v[w]
        return (-s) & M if r[1][u] == 1 else s & M
    x = r[2]; ru = None
    for w, k in r[1]:
        if w == u: ru = k
        else: x ^= rol(v[w], k)
    return ror(x, ru)
def holds(r, v): return rels.holds(r, v)
class Design:
    def __init__(s, F, B, g):
        s.F, s.B, s.g = tuple(F), tuple(B), g
        s.ord, s.checks, kn = order(set(F) | set(B) | {g})
        assert len(s.checks) == 1 and kn >= set(WORDS), (len(s.checks), set(WORDS) - kn)
        s.chk = s.checks[0]
        dep = {w: {w} for w in set(F) | set(B) | {g}}
        for i, w in s.ord: dep[w] = set().union(*(dep[x] for x in wset(REL[i]) if x != w))
        s.dep = dep
        par = {w: [x for x in wset(REL[i]) if x != w] for i, w in s.ord}
        need, st = set(), list(wset(REL[s.chk]))
        while st:
            x = st.pop()
            if x in need or x not in par or g not in dep[x]: continue
            need.add(x); st += par[x]
        s.loop = [(i, w) for i, w in s.ord if w in need]
        s.pre = [(i, w) for i, w in s.ord if g not in dep[w]]
        s.params = sorted({x for i, w in s.loop for x in wset(REL[i]) if x != w and g not in dep[x]} |
                          {x for x in wset(REL[s.chk]) if g not in dep[x]})
    def run(s, v):
        v = dict(v)
        for i, w in s.ord: v[w] = solve1(REL[i], w, v)
        return v, holds(REL[s.chk], v)
    def pre_values(s, v):
        v = dict(v)
        for i, w in s.pre: v[w] = solve1(REL[i], w, v)
        return v
    def cuda(s):
        '''straight-line C for the loop: params are kernel inputs P[k]; g is the candidate; returns (lines, check expr, ops).'''
        idx = {p: k for k, p in enumerate(s.params)}
        def name(w):
            if w == s.g: return 'g'
            if w in idx: return 'P[%d]' % idx[w]
            return 'v_' + w.replace('.', '_')
        lines, ops = [], 0
        def emit(r, u):
            nonlocal ops
            if r[0] == 'add':
                terms = ['%s%s' % ('-' if (c == 1) == (r[1][u] == 1) else '+', name(w)) for w, c in r[1].items() if w != u]
                const = (-r[2]) & M if r[1][u] == 1 else r[2] & M
                ops += len(terms) - (0 if const else 1)
                return '(0x%08xu %s)' % (const, ' '.join(terms))
            x = ['0x%08xu' % r[2]] if r[2] else []; ru = None
            for w, k in r[1]:
                if w == u: ru = k
                else:
                    x.append('ROL(%s,%d)' % (name(w), k) if k else name(w)); ops += 1 if k else 0
            ops += len(x) - 1 + (1 if ru else 0)
            e = '(' + ' ^ '.join(x) + ')'
            return 'ROL(%s,%d)' % (e, (32 - ru) % 32) if ru else e
        for i, w in s.loop:
            lines.append('uint32_t %s = %s;' % (name(w), emit(REL[i], w)))
        r = REL[s.chk]
        if r[0] == 'add':
            terms = ['%s%s' % ('+' if c == 1 else '-', name(w)) for w, c in r[1].items()]
            chk = '(0x%08xu %s)' % (r[2], ' '.join(terms)); ops += len(terms)
        else:
            x = ['0x%08xu' % r[2]] + ['ROL(%s,%d)' % (name(w), k) if k else name(w) for w, k in r[1]]
            chk = '(' + ' ^ '.join(x) + ')'; ops += len(x) - 1 + sum(1 for _, k in r[1] if k)
        return lines, chk, ops
def real_point(rnd):
    eight = [rnd.getrandbits(32) for _ in range(8)]
    v = hs.ctr_outer(eight); v['K'] = (v['Y1'] + v['w12']) & M; v['T1'] = 0
    return v
def c1_from_y14(v, y14):
    y10 = (y14 + v['C2.c1']) & M; y6 = ror(y10 ^ v['C2.b1'], 7); a1 = (y6 + v['Y1'] + v['w12']) & M
    d1 = ror(v['Y12'] ^ a1, 16)
    return (d1 + hs.Y11) & M
def verify(v, F, y14):
    '''full check on the real 2-round compression of the two last-chunk blocks, counter T0 + 2^32*T1, flags 3.'''
    c1 = c1_from_y14(v, y14)
    r = hs.ctr_trial(v, c1)
    if r is None: return False, 'T0=0'
    a, b, t0, tv = r
    t = t0 | (v['T1'] << 32)
    (wa, da, ya), (wb, db, yb) = hs.compress2(a[:hs.LEN_A], t, hs.CTR_FLAGS), hs.compress2(b[:hs.LEN_B], t, hs.CTR_FLAGS)
    e3a, e3b = (ya[3] + ya[4] + wa[15]) & M, (yb[3] + yb[4] + wb[15]) & M
    ok = (ya[4] == F['Y4'] and ya[9] == F['Y9'] and wa[8] == F['w8'] and ya[14] == y14 and tv['Y14'] == y14
          and all(da[i] == db[i] for i in (0, 2, 5, 7)) and (ya[3], ya[11]) == (hs.Y3, hs.Y11)
          and e3a & hs.CLASS_MASK == hs.CLASS_VALUE and ror(e3a ^ e3b, 16) == hs.ETA and ya[4] == yb[4]
          and ya[9] == yb[9] and ya[14] == yb[14] and wa[8] == wb[8])
    e1 = (ya[12], (ya[1] + wa[12]) & M, wa[5], (ya[11] + ror(ya[12] ^ ((ya[1] + ya[6] + wa[12]) & M), 16)) & M)
    return ok, {'c1': c1, 'E1': e1, 'T0': t0, 'T1': v['T1'], 'ya': ya, 'yb': yb, 'wa': wa, 'wb': wb, 'da': da, 'db': db}
def y14_of(v):
    '''Y14 of a real ctr_outer point for some trial: use cube member 0 of the old table to pick one.'''
    return hs.ctr_trial(v, hs.ctr_c1(0))[3]['Y14']
DESIGN = (('Y4', 'Y9', 'w8'), ('D2.b1', 'D3.a1', 'K0.b1', 'K3.d1', 'S14', 'S15'), 'C0.b1')
if __name__ == '__main__':
    d = Design(*DESIGN)
    print('relations', len(REL), 'words', len(WORDS), 'order', len(d.ord), 'check', REL[d.chk][3], rels.show(REL[d.chk]))
    print('pre', len(d.pre), 'loop', len(d.loop), [w for _, w in d.loop]); print('params', d.params)
    print('T1 depends on g:', d.g in d.dep['T1'], ' E1 words depend on g:',
          {w: d.g in d.dep[w] for w in ('Y12', 'Y1', 'w12', 'w5', 'K')})
    rnd = random.Random(1); good = 0; okv = 0
    for _ in range(300):
        v = real_point(rnd)
        start = {w: v[w] for w in d.F + d.B + (d.g,)}
        u, h = d.run(start)
        good += h and all(u[w] == v[w] for w in WORDS)
        ok, info = verify(u, {w: v[w] for w in d.F}, y14_of(v))
        okv += ok
    print('real points reproduced by the design order with check true: %d/300 ; compress2 verification: %d/300' % (good, okv))
    lines, chk, ops = d.cuda(); print('loop ops per candidate (rotation = 1 op):', ops)
    print('\n'.join(lines)); print('check:', chk)
