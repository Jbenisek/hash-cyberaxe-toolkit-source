'''Width of the carry-graph (bit-serial) solve of the 21-equation cycle.
(1) Time-sweep model: each addition Z gets a frame f_Z; at time t = 0..31 it processes bit (t - f_Z) mod 32 (Sol D4 7.2
    style, generalised to 9 additions).  A word bit needed before it is computed is guessed and verified later; g bits are
    guessed at first use; a carry chain that does not start at t = 0 needs a guessed carry (verified at t = 31).
    Expected live branches at each event = 2^(guesses - checks so far); DFS work ~ sum over events.  We minimise
    the peak and the sum over all 32^9 frame vectors by exhaustive coordinate search with restarts.
(2) Tree decomposition of the bit-level constraint graph (any elimination order, not only time sweeps):
    min-fill / min-degree upper bounds and the minor-min-width (contraction degeneracy) LOWER bound on treewidth.
usage: python width.py [restarts]'''
import sys, random, math, itertools
sys.dont_write_bytecode = True
import cyc
P0 = [0] * 14
ADDS = cyc.ADDS(P0)
NAMES = [a[0] for a in ADDS]
CARRYBITS = {}
for name, ops, c in ADDS:                    # number of summands incl. the constant -> max carry value
    n = len(ops) + 1
    CARRYBITS[name] = math.log2(n)            # carry in {0..n-1}: log2(n) bits if guessed (upper estimate of entropy)

def sweep(fr, trace=False):
    '''fr: dict addition -> frame. returns (peak level, log2 sum of 2^level over events, events).'''
    known = {('g', j): False for j in range(32)}
    comp = {(z, j): False for z in NAMES for j in range(32)}
    guessed = set()
    lev = 0.0; peak = 0.0; tot = 0.0; ev = []
    started = {z: False for z in NAMES}
    for t in range(32):
        for name, ops, c in ADDS:
            j = (t - fr[name]) % 32
            for terms, xc in ops:
                for w, r in terms:
                    jj = (j - r) % 32
                    if w == 'g':
                        if not known[('g', jj)]:
                            known[('g', jj)] = True; lev += 1; ev.append(lev)
                    elif not comp[(w, jj)] and (w, jj) not in guessed:
                        guessed.add((w, jj)); lev += 1; ev.append(lev)
            if j != 0 and not started[name]:
                lev += CARRYBITS[name]; ev.append(lev)        # guessed carry into the first processed bit
            started[name] = True
            if (name, j) in guessed:
                lev -= 1; guessed.discard((name, j))          # verification of an early guess
            comp[(name, j)] = True
            ev.append(lev)
            if name == 'chk':
                lev -= 1
            if j == 31 and fr[name] != 0:
                pass
            if (j + 1) % 32 == (32 - fr[name]) % 32 and fr[name] != 0:
                lev -= CARRYBITS[name]                         # guessed carry verified (bit 31-f_Z just done at t=31)
            ev.append(lev)
    peak = max(ev)
    s = math.log2(sum(2.0 ** e for e in ev))
    return peak, s, lev

def optimise(restarts, seed=1):
    rnd = random.Random(seed); best = None
    for _ in range(restarts):
        fr = {z: rnd.randrange(32) for z in NAMES}
        cur = sweep(fr)[1]
        improved = True
        while improved:
            improved = False
            for z in NAMES:
                for v in range(32):
                    old = fr[z]; fr[z] = v
                    s = sweep(fr)[1]
                    if s < cur - 1e-9: cur = s; improved = True
                    else: fr[z] = old
        if best is None or cur < best[0]: best = (cur, dict(fr))
    return best

# ---------------- (2) bit-level graph ----------------
def bitgraph():
    '''vertices: ('g',j), (Z,j) for addition outputs except chk, ('c',Z,j) carry INTO bit j of Z (j=1..31).
    one constraint per addition bit: its operand bits, carry in, carry out, output bit -> clique.'''
    adj = {}
    def addv(v): adj.setdefault(v, set())
    cons = []
    for name, ops, c in ADDS:
        for j in range(32):
            S = set()
            for terms, xc in ops:
                for w, r in terms: S.add((w, (j - r) % 32))
            if j > 0: S.add(('c', name, j))
            if j < 31: S.add(('c', name, j + 1))
            if name != 'chk': S.add((name, j))
            cons.append(S)
    for S in cons:
        for v in S: addv(v)
        for a, b in itertools.combinations(S, 2): adj[a].add(b); adj[b].add(a)
    return adj

def elim_width(adj, rule, rnd=None):
    adj = {v: set(n) for v, n in adj.items()}; width = 0
    while adj:
        if rule == 'mindeg':
            key = lambda v: (len(adj[v]), rnd.random() if rnd else 0)
        else:
            def key(v):
                nb = list(adj[v]); f = 0
                for i in range(len(nb)):
                    for k in range(i + 1, len(nb)):
                        if nb[k] not in adj[nb[i]]: f += 1
                return (f, len(adj[v]), rnd.random() if rnd else 0)
        v = min(adj, key=key)
        nb = adj.pop(v); width = max(width, len(nb))
        for a in nb:
            adj[a].discard(v)
            adj[a] |= (nb - {a})
    return width

def mmw(adj):
    '''minor-min-width lower bound: repeatedly contract a min-degree vertex into its min-degree neighbour.'''
    adj = {v: set(n) for v, n in adj.items()}; lb = 0
    while len(adj) > 1:
        v = min(adj, key=lambda x: len(adj[x]))
        lb = max(lb, len(adj[v]))
        if not adj[v]: adj.pop(v); continue
        u = min(adj[v], key=lambda x: len(adj[x]))
        for a in adj[v]:
            if a != u: adj[a].discard(v); adj[a].add(u); adj[u].add(a)
        adj[u].discard(v); adj.pop(v)
    return lb

if __name__ == '__main__':
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    zero = {z: 0 for z in NAMES}
    pk, s, end = sweep(zero)
    print('(1) time sweep, all frames 0: peak level %.2f  log2(sum 2^level) %.2f  end level %.2f' % (pk, s, end))
    best = optimise(R)
    pk, s, end = sweep(best[1])
    print('    best of %d restarts (min log2 sum): frames %s -> peak %.2f, log2 sum %.2f, end %.2f' % (R, best[1], pk, s, end))
    adj = bitgraph()
    print('(2) bit graph: %d vertices, %d edges' % (len(adj), sum(len(n) for n in adj.values()) // 2))
    print('    treewidth LOWER bound (minor-min-width):', mmw(adj))
    rnd = random.Random(3)
    ub = min(elim_width(adj, 'mindeg', rnd) for _ in range(5))
    print('    treewidth upper bound min-degree (best of 5):', ub)
    ubf = elim_width(adj, 'minfill', rnd)
    print('    treewidth upper bound min-fill:', ubf)
