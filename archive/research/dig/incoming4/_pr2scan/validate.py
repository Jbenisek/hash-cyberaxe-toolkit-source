import time, copy, sys
from pos_scan_lib import *

def variant(specs, kind, idx, lane):
    sp = copy.deepcopy(specs)
    for rd in sp:
        if rd['idx'] == idx:
            for ln in ([0, 1, 2] if lane == 9 else [lane]):
                if kind == 'arc': rd['c'][ln] = 0
                elif kind == 'sbox': rd['sb'][ln] = not rd['sb'][ln]
                elif kind == 'mds': rd['M'][ln] = [1 if k == ln else 0 for k in range(3)]
    return sp

def ntt_degree(alpha, beta, specs, deg_bound_pow):
    n = 1 << deg_bound_pow
    w = root_of_unity(n)
    pts = [mpz(1)]
    for _ in range(n - 1): pts.append(pts[-1] * w % P)
    vals = [F_eval(alpha, beta, specs, W) for W in pts]
    co = intt(vals, w)
    return poly_degree(co)

if __name__ == '__main__':
    r = int(sys.argv[1]); pw = int(sys.argv[2])
    sp0 = specs_from_2(r)
    alpha, beta, line = line_affine(0)
    cases = [('base', None, None, None)] + [tuple(a.split(':')) for a in sys.argv[3:]]
    for c in cases:
        if c[0] == 'base': sp = sp0
        else: sp = variant(sp0, c[0], int(c[1]), int(c[2]))
        t = time.time()
        tr = W_deg(alpha, beta, sp)
        t1 = time.time()
        nd = ntt_degree(alpha, beta, sp, pw)
        print(r, c, 'tracker', tr, 'ntt', nd, 'MATCH' if tr and tr[0] == nd else 'DIFF', round(t1 - t, 3), round(time.time() - t1, 1), flush=True)
