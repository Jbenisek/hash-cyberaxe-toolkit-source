'''Exact threshold search with FIXED chain starts, run over every start vector with at most one guessed carry
(one addition starts at bit s != 0, the others at bit 0): n=16 -> 1 + 9*15 = 136 searches.
usage: python exact_lb_one.py T n cap'''
import sys, math
sys.dont_write_bytecode = True
import sched
T = float(sys.argv[1]); n = int(sys.argv[2]); cap = int(sys.argv[3])
S = sched.scaled(n); NAMES = sched.NAMES; NS = sched.NSUM
OPS = [[(w, r) for terms, _ in ops for w, r in terms] for name, ops in S]
WI = {'g': 9}; WI.update({z: i for i, z in enumerate(NAMES)})
CB = [math.log2(NS[z]) for z in NAMES]

def search(st):
    layer = {(0,) * 9: (0.0, 0, (0,) * 10, (0,) * 10)}
    for step in range(9 * n):
        nxt = {}
        for p, (L, gm, inf, comp) in layer.items():
            for zi in range(9):
                if p[zi] == n: continue
                s = st[zi]; j = (s + p[zi]) % n
                L2 = L; gm2 = gm; inf2 = list(inf); comp2 = list(comp)
                if p[zi] == 0 and s != 0: L2 += CB[zi]
                for w, r in OPS[zi]:
                    jj = (j - r) % n; b = 1 << jj
                    if w == 'g':
                        if not gm2 & b: gm2 |= b; L2 += 1
                    else:
                        wi = WI[w]
                        if not comp2[wi] & b and not inf2[wi] & b: inf2[wi] |= b; L2 += 1
                b = 1 << j
                if zi == 8: L2 -= 1
                elif inf2[zi] & b: inf2[zi] &= ~b; L2 -= 1; comp2[zi] |= b
                else: comp2[zi] |= b
                if L2 > T + 1e-9: continue
                if p[zi] == n - 1 and s != 0: L2 -= CB[zi]
                q = p[:zi] + (p[zi] + 1,) + p[zi + 1:]
                if q not in nxt: nxt[q] = (L2, gm2, tuple(inf2), tuple(comp2))
        layer = nxt
        if not layer: return 'unreachable@%d' % (step + 1)
        if len(layer) > cap: return 'aborted@%d' % (step + 1)
    return 'REACHABLE'

if __name__ == '__main__':
    res = {}
    configs = [(0,) * 9] + [tuple(s if k == zi else 0 for k in range(9)) for zi in range(9) for s in range(1, n)]
    for st in configs:
        r = search(st); res[r.split('@')[0]] = res.get(r.split('@')[0], 0) + 1
        if not r.startswith('unreach'): print('  starts', st, r, flush=True)
    print('n=%d T=%g, %d start vectors with <= 1 guessed carry: %s' % (n, T, len(configs), res))
