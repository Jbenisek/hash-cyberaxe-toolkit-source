'''Beyond the uniform time sweep: any bit-serial carry-graph order in which each addition Z advances its carry chain one
bit at a time from a start bit s_Z (s_Z != 0 means a guessed carry, verified when the chain closes), at ANY relative
speeds.  A state is the progress vector p (bits done per addition); the live-branch level of a state is
    L(p) = #g bits known + #addition-output bits needed but not yet computed (guessed ahead) + open carry guesses - #chk bits done
(every guessed-ahead bit is verified when computed, so it nets out).  Beam search (layer = total progress) for the path
from p = 0 to p = 32^9 with the smallest peak L.  usage: python lattice.py <beam> <starts: zero|sweep>'''
import sys, math
sys.dont_write_bytecode = True
import sched
n = 32
S = sched.scaled(n); NAMES = sched.NAMES; NS = sched.NSUM
IDX = {z: i for i, z in enumerate(NAMES)}
FR32 = {'Y12': 8, 'd1': 0, 'a1': 0, 'Dd1': 16, 'w10': 0, 'C1a1': 8, 'C1c1': 20, 'Y1': 0, 'chk': 20}

def run(beam, starts):
    st = [starts[z] for z in NAMES]
    cb = [math.log2(NS[z]) for z in NAMES]
    # state: (progress tuple) -> (peak, L, gmask, inflight dict word->mask, comp dict word->mask)
    init = (tuple([0] * 9),)
    layer = {tuple([0] * 9): (0.0, 0.0, 0, {}, {})}
    for step in range(9 * n):
        nxt = {}
        for p, (pk, L, gm, inf, comp) in layer.items():
            for zi, (name, ops) in enumerate(S):
                if p[zi] == n: continue
                j = (st[zi] + p[zi]) % n
                L2 = L; gm2 = gm; inf2 = dict(inf); comp2 = dict(comp)
                if p[zi] == 0 and st[zi] != 0: L2 += cb[zi]
                for terms, _ in ops:
                    for w, r in terms:
                        jj = (j - r) % n; b = 1 << jj
                        if w == 'g':
                            if not gm2 & b: gm2 |= b; L2 += 1
                        elif not comp2.get(w, 0) & b and not inf2.get(w, 0) & b:
                            inf2[w] = inf2.get(w, 0) | b; L2 += 1
                b = 1 << j
                if name == 'chk': L2 -= 1
                elif inf2.get(name, 0) & b: inf2[name] &= ~b; L2 -= 1; comp2[name] = comp2.get(name, 0) | b
                else: comp2[name] = comp2.get(name, 0) | b
                if p[zi] == n - 1 and st[zi] != 0: L2 -= cb[zi]
                q = p[:zi] + (p[zi] + 1,) + p[zi + 1:]
                pk2 = max(pk, L2)
                if q not in nxt or (pk2, L2) < nxt[q][:2]: nxt[q] = (pk2, L2, gm2, inf2, comp2)
        layer = dict(sorted(nxt.items(), key=lambda kv: (kv[1][0], kv[1][1]))[:beam])
    (p, v), = layer.items()
    return v[0]

if __name__ == '__main__':
    beam = int(sys.argv[1]); mode = sys.argv[2]
    starts = {z: 0 for z in NAMES} if mode == 'zero' else {z: (n - FR32[z]) % n for z in NAMES}
    print('starts=%s beam=%d: best peak level found %.2f bits' % (mode, beam, run(beam, starts)))
