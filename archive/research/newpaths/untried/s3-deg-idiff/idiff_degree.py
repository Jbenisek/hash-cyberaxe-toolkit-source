"""Step 2: degree of the state S_r and of the internal difference delta_r = S_r xor rot_p(S_r) after rounds r = 1..6,
by cube sums, on z-periodic spaces:
  U<p>  : symmetric part of the 1-round-affine family U320 (dim 5p), p-periodic lane 16 (p = 8, 16, 32)
  V<p>  : best symmetric 2-round-affine sub-field found by fields.py (periodic lane 16)
  Vn<p> : same with the native lane 16 (input internal difference = constant lane-16 asymmetry, nonzero)
  W40   : control, certified W40 with random (non-symmetric) cosets; delta taken with period CTRL_P
Cube sum over t + span(k directions), t a random p-periodic source (W40: random 320-bit source). Rounds 1-5: full
1600-bit state; round 6: the 256-bit digest (lanes 0..3 after iota). Sum of delta = sum xor rot_p(sum) (rot is linear).
Usage: python idiff_degree.py SEED NCUBES SPACES(comma) DIMS(comma)"""
import sys, json, time, random
import numpy as np
import symlib as S

seed, ncub = int(sys.argv[1]), int(sys.argv[2])
spaces = sys.argv[3].split(',')
dims = [int(x) for x in sys.argv[4].split(',')]
CTRL_P = 32
rng = random.Random(seed)
FO = json.load(open('fields_out.json'))
MASK = S.MASK


def space(tag):
    if tag == 'W40':
        return CTRL_P, S.NATIVE, list(S.cd.W), None
    kind, p = (tag[:2], int(tag[2:])) if tag.startswith('Vn') else (tag[0], int(tag[1:]))
    sym = S.sym_basis(p)
    if kind == 'U':
        return p, S.lane16_for(p), sym, sym
    key = f'p{p}_' + ('native_l16' if kind == 'Vn' else 'periodic_l16')
    basis = [int(h, 16) for h in FO['bases'][key]]
    return p, (S.NATIVE if kind == 'Vn' else S.lane16_for(p)), basis, sym


def rotp(v, p):
    return ((v << p) | (v >> (64 - p))) & MASK


def cube(t, dirs, l16):
    u = S.cd.points(t, dirs)
    res = {}
    for r, A in S.states(u, l16, 6):
        L = A if r < 6 else A[:4]
        res[r] = [int(np.bitwise_xor.reduce(a)) for a in L]
    return res


def pick(rng, basis, k, mode):
    if mode == 'basis':
        return rng.sample(basis, k)
    while True:
        d = []
        for _ in range(k):
            c = rng.getrandbits(len(basis)) or 1
            d.append(S.combine(c, basis))
        if S.rank(d) == k:
            return d


out = []
for tag in spaces:
    p, l16, basis, sym = space(tag)
    n = S.rank(basis)
    print(json.dumps({'space': tag, 'p': p, 'lane16': hex(l16), 'dim': n, 'sponge_selfcheck': S.selfcheck(l16, rng)}), flush=True)
    for k in dims:
        if k > n:
            continue
        for mode in ('basis', 'span'):
            t0 = time.time()
            nzS = {r: 0 for r in range(1, 7)}; nzD = {r: 0 for r in range(1, 7)}; wD = {r: 0 for r in range(1, 7)}
            for _ in range(ncub):
                t = rng.getrandbits(320) if sym is None else S.combine(rng.getrandbits(len(sym)), sym)
                res = cube(t, pick(rng, basis, k, mode), l16)
                for r, s in res.items():
                    ds = [x ^ rotp(x, p) for x in s]
                    nzS[r] += any(s); nzD[r] += any(ds); wD[r] += sum(x.bit_count() for x in ds)
            rec = {'space': tag, 'dim': k, 'mode': mode, 'cubes': ncub, 'nonzero_state_sums': nzS,
                   'nonzero_delta_sums': nzD, 'mean_delta_sum_bits': {r: round(wD[r] / ncub, 1) for r in wD},
                   'sec': round(time.time() - t0, 1)}
            out.append(rec)
            print(json.dumps(rec), flush=True)
