'''lattice.py with FREE chain starts: when an addition first advances, the search also chooses its start bit s
(s != 0 = guessed carry, +log2(#summands) bits until the chain closes).  Beam search on (peak, level).
usage: python lattice2.py <beam> [rank: peak|level]'''
import sys, math
sys.dont_write_bytecode = True
import sched
n = 32
S = sched.scaled(n); NAMES = sched.NAMES; NS = sched.NSUM
OPS = [[(w, r) for terms, _ in ops for w, r in terms] for name, ops in S]
WI = {'g': 9}; WI.update({z: i for i, z in enumerate(NAMES)})
CB = [math.log2(NS[z]) for z in NAMES]

def run(beam, rank):
    layer = {((-1,) * 9, (0,) * 9): (0.0, 0.0, 0, (0,) * 10, (0,) * 10)}
    for step in range(9 * n):
        nxt = {}
        for (st, p), (pk, L, gm, inf, comp) in layer.items():
            for zi in range(9):
                if p[zi] == n: continue
                starts = range(n) if st[zi] < 0 else (st[zi],)
                for s in starts:
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
                    if p[zi] == n - 1 and s != 0: L2 -= CB[zi]
                    st2 = st[:zi] + (s,) + st[zi + 1:]; q = p[:zi] + (p[zi] + 1,) + p[zi + 1:]
                    pk2 = max(pk, L2); key = (st2, q)
                    if key not in nxt or (pk2, L2) < nxt[key][:2]: nxt[key] = (pk2, L2, gm2, tuple(inf2), tuple(comp2))
        k = (lambda kv: (kv[1][0], kv[1][1])) if rank == 'peak' else (lambda kv: (kv[1][1], kv[1][0]))
        layer = dict(sorted(nxt.items(), key=k)[:beam])
    best = min(layer.items(), key=lambda kv: kv[1][0])
    return best[1][0], best[0][0]

if __name__ == '__main__':
    beam = int(sys.argv[1]); rank = sys.argv[2] if len(sys.argv) > 2 else 'peak'
    pk, st = run(beam, rank)
    print('free starts, beam=%d rank=%s: best peak level %.2f, starts %s' % (beam, rank, pk, dict(zip(NAMES, st))))
