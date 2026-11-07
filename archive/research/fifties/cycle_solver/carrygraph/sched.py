'''Carry-graph (time-sweep) schedule for the cycle at word size n (rotations scaled by n/32; all cycle rotations are
multiples of 4, so n in {8,16,24,32} keeps the exact structure).  Each addition Z has a frame f_Z; at time t it
processes bit (t - f_Z) mod n.  Events (consumed by cg.c):
  G  w b      guess bit b of word w (g at first use; an addition output needed before it is computed)
  C  z m      guess the carry entering the first processed bit of z (m values), when that bit is not bit 0
  Z  z        carry of z := 0 (chain starts at bit 0)
  A  z j mode compute bit j of z (mode 0 store, 1 verify an earlier guess, 2 check = 0 for 'chk')
  V  z        verify the guessed carry of z (after bit f-1 of the wrapped chain)
plus the expected log2 live-branch level after each event (independent-bits model).
usage: python sched.py n [restarts] [seed] -> writes sched_n<n>.txt and prints the width profile'''
import sys, math, random
sys.dont_write_bytecode = True
import cyc
SP = cyc.ADDS([0] * 14)                         # structure only (constants are instance data)
NAMES = [a[0] for a in SP]
WORDS = ['g'] + [z for z in NAMES if z != 'chk']
NSUM = {name: len(ops) + 1 for name, ops, c in SP}   # summands incl. constant -> carry in [0, NSUM-1]

def scaled(n):
    return [(name, [([(w, r * n // 32) for w, r in terms], None) for terms, xc in ops]) for name, ops, c in SP]

def schedule(n, fr):
    S = scaled(n)
    known = set(); comp = set(); guessed = set(); started = set()
    ev = []; lev = 0.0; levs = []
    def push(e, d):
        nonlocal lev
        lev += d; ev.append(e); levs.append(lev)
    for t in range(n):
        for name, ops in S:
            f = fr[name] % n; j = (t - f) % n
            for terms, _ in ops:
                for w, r in terms:
                    jj = (j - r) % n
                    if w == 'g':
                        if jj not in known: known.add(jj); push(('G', 'g', jj), 1)
                    elif (w, jj) not in comp and (w, jj) not in guessed:
                        guessed.add((w, jj)); push(('G', w, jj), 1)
            if name not in started:
                started.add(name)
                if j != 0: push(('C', name, NSUM[name]), math.log2(NSUM[name]))
            if j == 0: push(('Z', name), 0)
            if name == 'chk': push(('A', name, j, 2), -1)
            elif (name, j) in guessed: guessed.discard((name, j)); comp.add((name, j)); push(('A', name, j, 1), -1)
            else: comp.add((name, j)); push(('A', name, j, 0), 0)
            if f != 0 and j == n - f - 1: push(('V', name), -math.log2(NSUM[name]))   # last bit; its carry-out enters bit n-f
    return ev, levs

def cost(levs): return math.log2(sum(2.0 ** l for l in levs))

def optimise(n, restarts, seed):
    rnd = random.Random(seed); best = None
    for _ in range(restarts):
        fr = {z: rnd.randrange(n) for z in NAMES}; cur = cost(schedule(n, fr)[1]); imp = True
        while imp:
            imp = False
            for z in NAMES:
                for v in range(n):
                    o = fr[z]; fr[z] = v; s = cost(schedule(n, fr)[1])
                    if s < cur - 1e-9: cur, imp = s, True
                    else: fr[z] = o
        if best is None or cur < best[0]: best = (cur, dict(fr))
    return best

def write(n, fr, ev, path):
    '''numeric file for cg.c: structure (words 0=g,1..8 = addition outputs; addition 8 = chk), then events.'''
    W = {w: i for i, w in enumerate(WORDS)}; Z = {z: i for i, z in enumerate(NAMES)}
    S = scaled(n)
    with open(path, 'w', newline='\n') as fo:
        fo.write('%d %d\n' % (n, len(S)))
        for name, ops in S:
            fo.write('%d %d' % (NSUM[name], len(ops)))
            for terms, _ in ops:
                fo.write(' %d' % len(terms))
                for w, r in terms: fo.write(' %d %d' % (W[w], r))
            fo.write('\n')
        fo.write('%d\n' % len(ev))
        code = {'G': 0, 'C': 1, 'Z': 2, 'A': 3, 'V': 4}
        for e in ev:
            if e[0] == 'G': a = (W[e[1]], e[2], 0)
            elif e[0] == 'C': a = (Z[e[1]], e[2], 0)
            elif e[0] in 'ZV': a = (Z[e[1]], 0, 0)
            else: a = (Z[e[1]], e[2], e[3])
            fo.write('%d %d %d %d\n' % ((code[e[0]],) + a))

def consts32(P):
    '''instance constants for cg.c from the 14 solve.cu params: per addition, operand xconsts then the additive const.'''
    out = []
    for name, ops, c in cyc.ADDS(P):
        out += [xc for _, xc in ops] + [c]
    return out

if __name__ == '__main__':
    n = int(sys.argv[1]); R = int(sys.argv[2]) if len(sys.argv) > 2 else 10; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    c, fr = optimise(n, R, seed)
    ev, levs = schedule(n, fr)
    nG = sum(1 for e in ev if e[0] == 'G'); nGg = sum(1 for e in ev if e[0] == 'G' and e[1] == 'g')
    print('n=%d best frames %s' % (n, fr))
    print('  events %d, bit guesses %d (g %d, early intermediate %d), carry guesses %d' %
          (len(ev), nG, nGg, nG - nGg, sum(1 for e in ev if e[0] == 'C')))
    print('  predicted peak level %.2f bits, predicted log2(transitions) %.2f, exhaustive log2 = %d' % (max(levs), c, n))
    write(n, fr, ev, 'sched_n%d.txt' % n)
