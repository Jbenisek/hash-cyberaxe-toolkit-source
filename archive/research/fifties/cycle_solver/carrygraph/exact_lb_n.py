'''Exact threshold search in the lattice model of lattice.py (zero starts, i.e. every carry chain from bit 0, no guessed
carries): is there ANY bit-serial order whose live-branch level never exceeds T?  BFS over progress vectors, layer by
layer, keeping every state with L <= T (exact, no beam).  Stops with "reachable" or "unreachable" (a proof for this
model) or "aborted" when a layer exceeds the cap.  usage: python exact_lb.py T cap'''
import sys
sys.dont_write_bytecode = True
import sched
n = int(sys.argv[3]) if len(sys.argv) > 3 else 32
S = sched.scaled(n); NAMES = sched.NAMES
OPS = []
for name, ops in S:
    OPS.append([(w, r) for terms, _ in ops for w, r in terms])
WI = {'g': 9}; WI.update({z: i for i, z in enumerate(NAMES)})

def main(T, cap):
    # value: (L, gmask, inflight tuple(10), comp tuple(10)) ; word index 9 = g
    start = (0,) * 9
    layer = {start: (0, 0, (0,) * 10, (0,) * 10)}
    for step in range(9 * n):
        nxt = {}
        for p, (L, gm, inf, comp) in layer.items():
            for zi in range(9):
                if p[zi] == n: continue
                j = p[zi]
                L2 = L; gm2 = gm; inf2 = list(inf); comp2 = list(comp)
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
                if L2 > T: continue
                q = p[:zi] + (j + 1,) + p[zi + 1:]
                if q not in nxt: nxt[q] = (L2, gm2, tuple(inf2), tuple(comp2))
        layer = nxt
        if not layer: return 'unreachable (no order with level <= %g; died at total progress %d)' % (T, step + 1)
        if len(layer) > cap: return 'aborted at total progress %d with %d states' % (step + 1, len(layer))
        if step % 16 == 15: print('  progress %d: %d states' % (step + 1, len(layer)), flush=True)
    return 'reachable'

if __name__ == '__main__':
    T = float(sys.argv[1]); cap = int(sys.argv[2])
    print('T=%g:' % T, main(T, cap))
