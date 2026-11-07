'''Are the per-group obstructions cheap? Find the GF(2) functionals lam with lam.R constant on EVERY group (group
invariants: lam.R depends on (outer words, member) only, not on the cube index j). If infeasibility is always witnessed
by such a lam, one pair evaluation per group decides it (cost ~ one pair, not 2^10+ points).
usage: python invariants.py <n_rand> <n_pass> <seed> <npts>'''
import sys, random, time
sys.dont_write_bytecode = True
import fresh as Fr

def rref_null(rows, n=128):
    'nullspace basis (list of ints) of the span of rows (ints of n bits)'
    piv = {}
    for r in rows:
        for p, b in piv.items():
            if r >> p & 1: r ^= b
        if r:
            p = r.bit_length() - 1
            for q in list(piv):
                if piv[q] >> p & 1: piv[q] ^= r
            piv[p] = r
    free = [c for c in range(n) if c not in piv]
    null = []
    for f in free:
        v = 1 << f
        for p, b in piv.items():
            if b >> f & 1: v |= 1 << p
        null.append(v)
    return null, len(piv)

def dot(a, b): return bin(a & b).count('1') & 1

def main():
    nr, npass, seed, npts = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3], 0), int(sys.argv[4])
    rnd = random.Random(seed); t0 = time.time(); groups = []; scanned = 0
    while len(groups) < nr + npass:
        ow = tuple(rnd.getrandbits(32) for _ in range(7)); k = rnd.getrandbits(19)
        v, e1 = Fr.group_v(ow, k); scanned += 1
        x, T = Fr.frontline_T(v, e1)
        want_pass = len(groups) >= nr
        if want_pass and not T: continue
        vecs = [Fr.pack(r) for r in (Fr.pair(v, rnd.getrandbits(21)) for _ in range(npts)) if r is not None]
        groups.append((vecs, x, T, 'pass' if want_pass else 'rand'))
    print('groups', len(groups), 'scanned', scanned, 'time %.0fs' % (time.time() - t0), flush=True)
    # per-group hull, feasibility
    info = []
    for vecs, x, T, lab in groups:
        b, o = Fr.affine_basis(vecs)
        info.append((len(b), Fr.in_span(b, o), o))
    # universal group invariants: nullspace of the union of all within-group difference spaces
    diff_rows = []
    for vecs, *_ in groups:
        b, o = Fr.affine_basis(vecs); diff_rows += list(b.values())
    U, rk = rref_null(diff_rows)
    print('union of within-group difference spaces: rank %d -> %d universal group invariants' % (rk, len(U)))
    # global relations among them: constant over all groups?
    consts = [[dot(lam, inf[2]) for inf in info] for lam in U]
    # reduce: invariants with constant 0 everywhere (global relations) vs varying
    Gl, _ = rref_null([inf[2] ^ info[0][2] for inf in info] + diff_rows)
    print('global affine relations (constant over all groups): %d' % len(Gl))
    # does a universal invariant explain each infeasible group?
    nexp = ninf = 0; inv_reject = {'rand': [0, 0], 'pass': [0, 0]}
    for gi, (vecs, x, T, lab) in enumerate(groups):
        feas = info[gi][1]
        # group is rejected by universal invariants iff some lam in span(U) has lam.R0 = 1 while lam.R0' for the
        # 'zero' target is 0: i.e. R0 not orthogonal to span(U) -> 0 not in (R0 + U-perp)
        rej = any(dot(lam, info[gi][2]) for lam in U)
        inv_reject[lab][0] += rej; inv_reject[lab][1] += 1
        if not feas:
            ninf += 1; nexp += rej
        assert not (rej and feas)
    print('infeasible groups %d, of which explained by universal invariants %d' % (ninf, nexp))
    for lab in ('rand', 'pass'):
        a, n = inv_reject[lab]
        f = sum(1 for gi, g in enumerate(groups) if g[3] == lab and not info[gi][1])
        print('  %s: %d groups, hull-infeasible %d, rejected by universal invariants alone %d' % (lab, n, f, a))
    for i, lam in enumerate(U):
        w = [(lam >> (32 * q)) & 0xFFFFFFFF for q in range(4)]
        print('  inv %d mask R1 %08x R3 %08x R4 %08x R6 %08x weight %d  const=1 in %d/%d groups' %
              (i, w[0], w[1], w[2], w[3], bin(lam).count('1'), sum(consts[i]), len(groups)))

main()
