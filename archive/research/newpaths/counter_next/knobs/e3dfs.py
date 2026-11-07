"""e3dfs.py (counter_next/knobs; research only) - "solve E3 per outer step instead of sampling it".

In the counter arrangement the E3 inputs other than h1 are fixed per outer step: U = (y = Y4, Y9, w8)
(counter/structure cone: Y9, w8 do not move with the inner word), and the inner map c1 -> h1 is a permutation of
all 2^32 words (sol_answer_Y section 7.1).  E3 on A and B is then a function of h1 alone:
    e1 = Y3 + y, e1' = Y3' + y, h1' = h1 ^ eta,
    g1 = Y9 + h1, f1 = ROR(y ^ g1, 12), e2 = e1 + f1 + w8, h2 = ROR(h1 ^ e2, 8), g2 = g1 + h2, f2 = ROR(f1 ^ g2, 7).
R = 0 needs, for the outcome j = (beta, tau, eps) (beta is a function of eps by Lemma N):
    e2 ^ e2' = eps,   g2 ^ g2' = tau,   f2 ^ f2' = ROR(tau, 8)   (=> g1 ^ g1' = ROL(tau ^ ROR(tau, 1), 12)).
A target is the 4-tuple (dg1, de2, dg2, df2).  The search enumerates EVERY h1 in [0, 2^32) meeting a target by a
breadth-first search over the bits of h1, low to high, checking each condition bit as soon as all the bits it reads
are fixed, and counts the nodes (partial assignments) visited: the work of a bit-serial solver.

Modes:
  python -B e3dfs.py nodes NU SEED NTARGETS     node counts over NU random outer steps (y in the sub-class);
                                                 targets = the NTARGETS heaviest outcomes of a15_outcomes.tsv
  python -B e3dfs.py planted NU SEED             correctness: random (y, Y9, w8, h1); target = the 4 differences
                                                 that h1 itself produces; the search must return h1
  python -B e3dfs.py list Y9 W8 Y NT [partial]   print all solutions (hex) for one outer step (for e3brute.c)
"""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys, random
import numpy as np

M32 = 0xffffffff
Y3, Y3B = 0x8127c181, 0x7edf3e7e
ETA = 0x830303cf
SUBMASK, SUBVAL = 0x07ef8303, 0x030c0303
TSV = _hca_public_path_text('__HCA_WORKSPACE__/research/pkg10/pkg/count/a15_outcomes.tsv')


def rol(x, r): return ((x << r) | (x >> (32 - r))) & M32
def ror(x, r): return ((x >> r) | (x << (32 - r))) & M32


def load_targets(n=None):
    rows = []
    with open(TSV) as f:
        hdr = f.readline().split('\t')
        for ln in f:
            d = dict(zip(hdr, ln.rstrip('\n').split('\t')))
            L, N = int(d['E1']), int(d['N3'])
            rows.append((L * N, int(d['beta'], 16), int(d['tau'], 16), int(d['eps'], 16), L, N))
    rows.sort(reverse=True)
    tot = sum(r[0] for r in rows)
    return (rows[:n] if n else rows), tot


def outcome_target(tau, eps):
    return (rol(tau ^ ror(tau, 1), 12), eps, tau, ror(tau, 8))


def e3_full(y, h, Y9, w8):
    e1, e1b = (Y3 + y) & M32, (Y3B + y) & M32
    hb = h ^ ETA
    g1, g1b = (Y9 + h) & M32, (Y9 + hb) & M32
    f1, f1b = ror(y ^ g1, 12), ror(y ^ g1b, 12)
    e2, e2b = (e1 + f1 + w8) & M32, (e1b + f1b + w8) & M32
    h2, h2b = ror(h ^ e2, 8), ror(hb ^ e2b, 8)
    g2, g2b = (g1 + h2) & M32, (g1b + h2b) & M32
    f2, f2b = ror(f1 ^ g2, 7), ror(f1b ^ g2b, 7)
    return (g1 ^ g1b, e2 ^ e2b, g2 ^ g2b, f2 ^ f2b)


def search(y, Y9, w8, targets, partial=False, g1only=False):
    """targets: list of 4-tuples (dg1, de2, dg2, df2).  partial: only the dg1 and de2 conditions;
    g1only: only the dg1 condition.  Returns (solutions [(h, target index)], nodes per level k = 1..32)."""
    if g1only:
        return search_g1(Y9, targets)
    U = np.uint64
    e1, e1b = U((Y3 + y) & M32), U((Y3B + y) & M32)
    Y9u, w8u, yu, eta = U(Y9), U(w8), U(y), U(ETA)
    T = [tuple(U(v) for v in t) for t in targets]
    cand = np.array([0], dtype=np.uint64)
    alive = np.full((1, len(T)), True)
    nodes = []
    for k in range(1, 33):
        cand = np.concatenate([cand, cand | U(1 << (k - 1))])
        alive = np.concatenate([alive, alive])
        nodes.append(len(cand))
        mk = U((1 << k) - 1)
        h = cand
        hb = h ^ eta
        g1 = (Y9u + h) & mk
        g1b = (Y9u + hb) & mk
        dg1 = g1 ^ g1b
        nf, nh, n2 = k - 12, k - 20, k - 27
        if nf > 0:
            mf = U((1 << nf) - 1)
            f1 = ((g1 >> U(12)) ^ (yu >> U(12))) & mf
            f1b = ((g1b >> U(12)) ^ (yu >> U(12))) & mf
            e2 = (e1 + f1 + w8u) & mf
            e2b = (e1b + f1b + w8u) & mf
            de2 = e2 ^ e2b
        if nh > 0 and not partial:
            mh = U((1 << nh) - 1)
            h2 = ((h ^ e2) >> U(8)) & mh
            h2b = ((hb ^ e2b) >> U(8)) & mh
            g2 = (g1 + h2) & mh
            g2b = (g1b + h2b) & mh
            dg2 = g2 ^ g2b
        if n2 > 0 and not partial:
            m2 = U((1 << n2) - 1)
            df2 = (((f1 ^ g2) >> U(7)) ^ ((f1b ^ g2b) >> U(7))) & m2
        ok = np.zeros(len(cand), dtype=bool)
        newalive = np.zeros_like(alive)
        for ti, (tg1, te2, tg2, tf2) in enumerate(T):
            c = alive[:, ti] & (dg1 == (tg1 & mk))
            if nf > 0:
                c &= (de2 == (te2 & mf))
            if nh > 0 and not partial:
                c &= (dg2 == (tg2 & mh))
            if n2 > 0 and not partial:
                c &= (df2 == (tf2 & m2))
            newalive[:, ti] = c
            ok |= c
        cand = cand[ok]
        alive = newalive[ok]
    sols = []
    for h, al in zip(cand.tolist(), alive.tolist()):
        d = e3_full(y, h, Y9, w8)
        for ti, t in enumerate(targets):
            if al[ti] and (d[:2] == t[:2] if partial else d == t):
                sols.append((h, ti))
    return sols, nodes


def search_g1(Y9, targets):
    """Feasibility of the dg1 condition alone (depends on Y9 only): returns ([(h, ti)] for up to the first
    solutions found per target, nodes).  Stops each target at its first full-width solution."""
    U = np.uint64
    Y9u, eta = U(Y9), U(ETA)
    sols, nodes = [], []
    for ti, t in enumerate(targets):
        tg = U(t[0])
        cand = np.array([0], dtype=np.uint64)
        for k in range(1, 33):
            cand = np.concatenate([cand, cand | U(1 << (k - 1))])
            nodes.append(len(cand))
            mk = U((1 << k) - 1)
            dg1 = ((Y9u + cand) & mk) ^ ((Y9u + (cand ^ eta)) & mk)
            cand = cand[dg1 == (tg & mk)]
            if len(cand) == 0:
                break
            # exact reduction: the future depends only on the carry pair into bit k -> one prefix per pair
            ca = ((Y9u & mk) + cand) >> U(k)
            cb = ((Y9u & mk) + ((cand ^ eta) & mk)) >> U(k)
            _, idx = np.unique(ca * U(2) + cb, return_index=True)
            cand = cand[np.sort(idx)]
        if len(cand):
            sols.append((int(cand[0]), ti))
    return sols, nodes


def rand_member(rng):
    e = (rng.getrandbits(32) & ~SUBMASK & M32) | SUBVAL
    return (e - Y3) & M32


def main():
    mode = sys.argv[1]
    if mode == 'nodes':
        NU, seed, nt = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        rows, tot = load_targets(nt)
        targets = [outcome_target(r[2], r[3]) for r in rows]
        mass = sum(r[0] for r in rows)
        print(f'targets {len(targets)} (heaviest outcomes of a15_outcomes.tsv), mass share {mass / tot:.6f} '
              f'(C_targets {mass / 2**81:.2f}, C_total {tot / 2**81:.2f})')
        rng = random.Random(seed)
        tot_nodes, per_level, nsol = [], np.zeros(32), 0
        for u in range(NU):
            y, Y9, w8 = rand_member(rng), rng.getrandbits(32), rng.getrandbits(32)
            sols, nodes = search(y, Y9, w8, targets)
            tot_nodes.append(sum(nodes))
            per_level += np.array(nodes)
            nsol += len(sols)
        a = np.array(tot_nodes, dtype=float)
        print(f'outer steps {NU}: nodes per outer step mean {a.mean():.1f}, median {np.median(a):.0f}, '
              f'max {a.max():.0f}, sd {a.std():.1f}; E3 solutions found {nsol}')
        print('mean nodes per level k = 1..32:', ' '.join(f'{v / NU:.1f}' for v in per_level))
    elif mode == 'planted':
        NU, seed = int(sys.argv[2]), int(sys.argv[3])
        rng = random.Random(seed)
        found = extra = 0
        for u in range(NU):
            y, Y9, w8, h = rand_member(rng), rng.getrandbits(32), rng.getrandbits(32), rng.getrandbits(32)
            t = e3_full(y, h, Y9, w8)
            sols, _ = search(y, Y9, w8, [t])
            hs = [s for s, _ in sols]
            found += h in hs
            extra += len(hs) - (h in hs)
            for s in hs:
                assert e3_full(y, s, Y9, w8) == t
        print(f'planted: {NU} outer steps, planted h1 found {found} of {NU}; other exact solutions {extra} '
              f'(every returned h1 re-verified by the full E3 formulas)')
    elif mode == 'list':
        Y9, w8, y, nt = int(sys.argv[2], 16), int(sys.argv[3], 16), int(sys.argv[4], 16), int(sys.argv[5])
        partial = len(sys.argv) > 6 and sys.argv[6] == 'partial'
        rows, tot = load_targets(nt)
        targets = [outcome_target(r[2], r[3]) for r in rows]
        sols, nodes = search(y, Y9, w8, targets, partial)
        print(f'# y {y:08x} Y9 {Y9:08x} w8 {w8:08x} targets {len(targets)} partial {partial}: '
              f'{len(sols)} solutions, nodes {sum(nodes)}')
        for h, ti in sorted(sols):
            print(f'{h:08x} {ti}')


if __name__ == '__main__':
    main()
