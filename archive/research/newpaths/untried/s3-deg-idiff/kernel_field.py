"""Step 4: best case for a LOW-degree internal difference. Inside U<p> (periodic lane 16), take K2 = kernel of the
linear part of delta_2 (delta_2 is affine on U<p>; on K2-cosets it is constant), then search the largest 2-round-affine
sub-field V' of K2 (same per-row chi1 test, greedy hitting subspace). On V' the bound is deg delta_r <= d_{r-1}+deg delta_{r-1}
with delta_2 constant: (0,0,1,3,7,15) instead of the state's (1,1,2,4,8,16). Then K3 = V' cap ker(lin delta_3).
Measures, by cube sums on random p-periodic cosets: state and delta degrees per round on V' and on K3.
Usage: python kernel_field.py SEED P SECONDS NCUBES DIMS"""
import sys, json, time, random
import numpy as np
import symlib as S


def run(pts, l16):                      # same helpers as idiff_chain.py
    return {r: A for r, A in S.states(S.unpack_src(pts), l16, 6)}


def dbits(A, p):
    return S.bits_of([a ^ S.rotl(a, p) for a in A])


def kernel_combos(vecs):
    piv = {}; ker = []
    for i, v in enumerate(vecs):
        c = 1 << i
        while v:
            b = v.bit_length() - 1
            if b in piv:
                v ^= piv[b][0]; c ^= piv[b][1]
            else:
                piv[b] = (v, c); break
        if not v:
            ker.append(c)
    return ker


seed, p, secs, ncub = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
dims = [int(x) for x in sys.argv[5].split(',')]
rng = random.Random(seed)
l16 = S.lane16_for(p)
sym = S.sym_basis(p)
MASK = S.MASK


def lin_kernel(t, B, r):
    """kernel (as vectors) of the linear part of delta_r on t + span(B); also returns #nonaffine second differences"""
    n = len(B)
    quads = []
    for _ in range(64):
        a = S.combine(rng.getrandbits(n), B); b = S.combine(rng.getrandbits(n), B)
        quads += [t ^ a ^ b, t ^ a, t ^ b, t]
    st = run([t] + [t ^ b for b in B] + quads, l16)[r]
    db = dbits(st, p)
    q = db[1 + n:].reshape(64, 4, 1600)
    nonaff = int(np.count_nonzero((q[:, 0] ^ q[:, 1] ^ q[:, 2] ^ q[:, 3]).any(axis=1)))
    lin = db[1:1 + n] ^ db[0]
    vecs = [int.from_bytes(np.packbits(lin[i], bitorder='little').tobytes(), 'little') for i in range(n)]
    return [S.combine(c, B) for c in kernel_combos(vecs)], nonaff


t0 = S.combine(rng.getrandbits(len(sym)), sym)
K2, na2 = lin_kernel(t0, sym, 2)
print(json.dumps({'p': p, 'U_dim': len(sym), 'delta2_nonaffine_2nd_diffs': na2, 'K2_dim': len(K2)}), flush=True)

# 2-round-affine search inside K2
c, F = S.affine_map(l16, 'chi1in')
Fr = [S.restrict(f, K2) for f in F]
pairs = S.chi_pairs(Fr)
best = None; runs = 0; t1 = time.time()
while time.time() - t1 < secs:
    Q = S.hitting_greedy(pairs, rng, rng.choice((0, 0, 1, 2)))
    d = len(K2) - S.rank(Q); runs += 1
    if best is None or d > best[0]:
        best = (d, Q)
Vc = S.annihilator(best[1], len(K2))
V = [S.combine(v, K2) for v in Vc]
print(json.dumps({'Vprime_dim': len(V), 'runs': runs, 'pairs_in_K2': len(pairs),
                  'failing_pairs': S.check_pairs_on(pairs, Vc)}), flush=True)

# delta_3 on V' (should be affine: delta_2 constant, rounds 1-2 affine), kernel K3
K3, na3 = lin_kernel(t0, V, 3)
print(json.dumps({'delta3_nonaffine_on_Vprime': na3, 'K3_dim': len(K3)}), flush=True)
json.dump({'p': p, 'K2': [hex(v) for v in K2], 'Vprime': [hex(v) for v in V], 'K3': [hex(v) for v in K3]},
          open(f'kernel_field_p{p}.json', 'w'))


def rotp(v):
    return ((v << p) | (v >> (64 - p))) & MASK


def degree_scan(tag, B):
    for k in dims:
        if k > len(B):
            continue
        nzS = {r: 0 for r in range(1, 7)}; nzD = {r: 0 for r in range(1, 7)}
        for _ in range(ncub):
            t = S.combine(rng.getrandbits(len(sym)), sym)
            while True:
                dd = [S.combine(rng.getrandbits(len(B)) or 1, B) for _ in range(k)]
                if S.rank(dd) == k:
                    break
            u = S.cd.points(t, dd)
            for r, A in S.states(u, l16, 6):
                s = [int(np.bitwise_xor.reduce(a)) for a in (A if r < 6 else A[:4])]
                nzS[r] += any(s); nzD[r] += any(x ^ rotp(x) for x in s)
        print(json.dumps({'space': tag, 'dim': k, 'cubes': ncub, 'nonzero_state_sums': nzS, 'nonzero_delta_sums': nzD}), flush=True)


degree_scan(f"V'{p} (2-round-affine, delta2 const)", V)
if K3:
    degree_scan(f"K3_{p} (delta2, delta3 const)", K3)
