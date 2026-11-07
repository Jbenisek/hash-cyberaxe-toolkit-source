"""clump.py (counter_next/knobs; research only): how strongly do E3 solutions of one outer step cluster?

Within one outer step, the partial-system solutions (dg1, de2 of a listed target) are grouped by their FULL E3
differences (dg2, df2).  If a listed target's full solutions behave like these groups, a full E3 solution has
(size-biased mean group size - 1) companions in the same outer step.  On REAL outer steps the E1 differences
(beta, tau, eps of E1, from the real compressions) of the group members are also compared: a full SUCCESS clumps
only if the companions also share the E1 outcome.
usage: python -B clump.py NREAL SEED NT
"""
import sys, random
from collections import Counter, defaultdict
sys.dont_write_bytecode = True
import e3dfs as D
import e3real as R
import arrange_check as A


def groups_of(y, Y9, w8, sols):
    g = defaultdict(list)
    for h, ti in sols:
        d = D.e3_full(y, h, Y9, w8)
        g[(ti, d[2], d[3])].append(h)
    return g


def summarize(tag, sizes):
    if not sizes:
        print(f'{tag}: no groups'); return
    s1, s2 = sum(sizes), sum(s * s for s in sizes)
    c = Counter(sizes)
    print(f'{tag}: {len(sizes)} groups, {s1} solutions; size-biased mean group size {s2 / s1:.2f}; '
          f'sizes {dict(sorted(c.items()))}')


def main():
    nreal, seed, nt = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    rows, _ = D.load_targets(nt)
    targets = [D.outcome_target(r[2], r[3]) for r in rows]
    # synthetic cases from pick_u.py
    sizes = []
    for ln in open('brute_cases.txt'):
        if ln.startswith('#'):
            continue
        p = ln.split()
        if int(p[3]) == 0:
            continue
        y, Y9, w8 = (int(x, 16) for x in p[:3])
        sols = [(int(a, 16), int(b)) for a, b in (q.split(':') for q in p[5].split(','))]
        g = groups_of(y, Y9, w8, sols)
        sizes += [len(v) for v in g.values()]
    summarize('synthetic outer steps (brute_cases.txt)', sizes)
    # real outer steps
    rng = random.Random(seed)
    rsizes, e1_same, e1_pairs, nsteps_with = [], 0, 0, 0
    e1_group_sizes = []
    for oi in range(nreal):
        o = A.outer(*[rng.getrandbits(32) for _ in range(7)], A.sub_member(rng))
        sols, _ = D.search(o['y'], o['Y9'], o['w8'], targets, partial=True)
        if not sols:
            continue
        nsteps_with += 1
        g = groups_of(o['y'], o['Y9'], o['w8'], sols)
        for key, hs in g.items():
            rsizes.append(len(hs))
            e1 = Counter()
            for h in hs:
                tr = R.real_trial(o, R.d1_of_h(o, h))
                # E1 differences from the trace are not returned by real_trial: recompute them here
                ii, words = A.inner(o, R.d1_of_h(o, h))
                wb = list(words); wb[4] = A.W4B; wb[5] = (words[5] + A.DELTA) & 0xFFFFFFFF
                ta, tb = {}, {}
                R.O.compress_full(R.O.IV, words, ii['t'], 55, 3, trace=ta)
                R.O.compress_full(R.O.IV, wb, ii['t'], 63, 3, trace=tb)
                ea, eb = ta['E1'], tb['E1']
                e1[(ea['b1'] ^ eb['b1'], ea['a2'] ^ eb['a2'], ea['c2'] ^ eb['c2'])] += 1
            e1_group_sizes += list(e1.values())
    print(f'real outer steps: {nreal}, with partial solutions: {nsteps_with}')
    summarize('real outer steps, groups by full E3 differences', rsizes)
    summarize('real outer steps, sub-groups that also share the E1 differences (beta, tau, eps)', e1_group_sizes)


if __name__ == '__main__':
    main()
