'''Exact threshold search in the lattice model with FREE chain starts (guessed carries allowed): when an addition first
advances, every start bit s is tried (s != 0 costs log2(#summands) bits until its chain closes).  BFS over
(starts, progress) keeping every state with level <= T.  usage: python exact_lb_free.py T cap n'''
import sys, math
sys.dont_write_bytecode = True
import sched
n = int(sys.argv[3]) if len(sys.argv) > 3 else 32
S = sched.scaled(n); NAMES = sched.NAMES; NS = sched.NSUM
OPS = [[(w, r) for terms, _ in ops for w, r in terms] for name, ops in S]
WI = {'g': 9}; WI.update({z: i for i, z in enumerate(NAMES)})
CB = [math.log2(NS[z]) for z in NAMES]

def main(T, cap):
    layer = {((-1,) * 9, (0,) * 9): (0.0, 0, (0,) * 10, (0,) * 10)}
    for step in range(9 * n):
        nxt = {}
        for (st, p), (L, gm, inf, comp) in layer.items():
            for zi in range(9):
                if p[zi] == n: continue
                for s in (range(n) if st[zi] < 0 else (st[zi],)):
                    j = (s + p[zi]) % n
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
                    key = (st[:zi] + (s,) + st[zi + 1:], p[:zi] + (p[zi] + 1,) + p[zi + 1:])
                    if key not in nxt: nxt[key] = (L2, gm2, tuple(inf2), tuple(comp2))
        layer = nxt
        if not layer: return 'unreachable (no order with level <= %g; died at total progress %d)' % (T, step + 1)
        if len(layer) > cap: return 'aborted at total progress %d with %d states' % (step + 1, len(layer))
    return 'reachable'

if __name__ == '__main__':
    T = float(sys.argv[1]); cap = int(sys.argv[2])
    print('n=%d free starts T=%g:' % (n, T), main(T, cap))
