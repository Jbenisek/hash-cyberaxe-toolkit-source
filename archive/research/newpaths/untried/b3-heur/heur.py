#!/usr/bin/env python3
"""heur.py  (untried/b3-heur; research only; run inside WSL Ubuntu, one CPU process at a time)

Non-gradient heuristic for the class choice of E3 (layer r1d, free const, counter base): simulated annealing over
ONE member e1 = Y3 + Y4 (Y4 is an outer word on the counter path, so one member is enough), scored by the team's
exact counter tool pair_calc_sub (beta* = 18b0e098 alone, pin H8; the same call as counter_next/stack/run_cube.sh with
-cube ffffffff e1).  Per-member rates (normalisation of scan_y4.py, free = 0):
    total = sum_j L_j N_j / 2^64  over every row      (the objective of the stack's greedy scan; best known 76,161,024)
    S     = the same sum over the six front-line taus  (class value 67,633,152, the map's Section 2.6 figure)
Phase A: e1 inside the front-line class (e1 AND 03cf8303) = 030c0303, 19 free bits, eta = 830303cf.
Phase B: all 32 bits of e1 free; eta = ROR(e1 XOR (e1 + DY3), 16) is recomputed per point, so every point is a valid
         member of its own class (a different class choice whenever a class-fixed bit flips).
Energy = -score, score = log2(S) * 64 + log2(total) in phase A (lexicographic: S first, total breaks ties) and
score = log2(total) in phase B.  Geometric temperature, 1-3 bit flips, restart after a stall.
Usage: python3 heur.py SECONDS SEED [PHASE_A_SHARE]
"""
import os, sys, time, random, subprocess, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rates import parse

D = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.expanduser('~/hashsmash/pkg7_count/bin/pair_calc_sub')
D3, D11, DELTA, Y3, Y11 = 0xfdb77cfd, 0x0a08818b, 0xfffffff8, 0x8127c181, 0x7af77f38
S8 = '00010000:0,00020000:0,00000001:0,00000002:1,00000404:1,00000808:1,01001008:0,02002040:0'
BETAF = os.path.join(D, 'beta_star.lst')
CM, CV = 0x03CF8303, 0x030C0303
FREE = [b for b in range(32) if not CM >> b & 1]
M32 = 0xFFFFFFFF
BEST_TOTAL, CLASS_S = 76161024, 67633152


def ror(x, r):
    return ((x >> r) | (x << (32 - r))) & M32


def eta_of(e1):
    return ror(e1 ^ ((e1 + D3) & M32), 16)


assert eta_of(0x070C0307) == 0x830303CF


class Evaluator:
    def __init__(self, log):
        self.cache = {}
        self.log = log
        self.n = 0
        self.secs = 0.0

    def __call__(self, e1, phase):
        if e1 in self.cache:
            return self.cache[e1]
        eta = eta_of(e1)
        args = [BIN, f'{D3:08x}', f'{D11:08x}', f'{DELTA:08x}', f'{Y3:08x}', f'{eta:08x}', BETAF, f'{Y11:08x}',
                '-rule', S8, '-cube', 'ffffffff', f'{e1:08x}', '-mode', 'both']
        t0 = time.time()
        try:
            p = subprocess.run(args, capture_output=True, text=True, timeout=20,
                               env=dict(os.environ, OMP_NUM_THREADS='1'))
            rc, out = p.returncode, p.stdout
        except subprocess.TimeoutExpired:
            rc, out = 'timeout', ''
        dt = time.time() - t0
        self.n += 1
        self.secs += dt
        if rc == 0 and 'OUTR' in out:
            S, r7, tot, nrows, rows = parse(out, 0xFFFFFFFF)
            S, r7, tot = int(S), int(r7), int(tot)
            assert S == parse(out, 0xFFFFFFFF)[0]          # free = 0: masses are integers or exact fractions
        else:
            S = r7 = tot = nrows = 0
        fixed = bin(ror(eta, 16)).count('1')               # weight of the XOR difference = class fixed bits
        res = (S, r7, tot, nrows, eta, fixed, rc)
        self.cache[e1] = res
        self.log.write(f'{phase}\t{self.n}\t{e1:08x}\t{eta:08x}\t{fixed}\t{S}\t{r7}\t{tot}\t{nrows}\t{rc}\t{dt:.3f}\n')
        self.log.flush()
        return res


def score_A(r):
    S, r7, tot = r[0], r[1], r[2]
    return (math.log2(S) if S else 0.0) * 64 + (math.log2(tot) if tot else 0.0)


def score_B(r):
    return math.log2(r[2]) if r[2] else 0.0


def anneal(ev, rng, phase, start, bits, score, t_hi, t_lo, deadline, trace):
    cur = start
    cs = score(ev(cur, phase))
    best, bs = cur, cs
    t_start = time.time()
    span = max(deadline - t_start, 1e-9)
    stall = 0
    while time.time() < deadline:
        frac = (time.time() - t_start) / span
        T = t_hi * (t_lo / t_hi) ** frac
        k = rng.choices((1, 2, 3), weights=(6, 3, 1))[0]
        nxt = cur
        for b in rng.sample(bits, k):
            nxt ^= 1 << b
        if nxt in ev.cache:
            stall += 1
        ns = score(ev(nxt, phase))
        acc = ns >= cs or rng.random() < math.exp((ns - cs) / T)
        if acc:
            cur, cs = nxt, ns
        if ns > bs:
            best, bs, stall = nxt, ns, 0
        else:
            stall += 1
        if stall > 150:                                   # restart: random point, or back to the best
            if rng.random() < 0.5:
                cur = best
            else:
                cur = start
                for b in bits:
                    if rng.random() < 0.5:
                        cur ^= 1 << b
            cs = score(ev(cur, phase))
            stall = 0
            trace.write(f'{phase} restart at eval {ev.n}, T {T:.4g}, best {best:08x} score {bs:.6f}\n')
        if ev.n % 50 == 0:
            r = ev.cache[best]
            trace.write(f'{phase} eval {ev.n} t {time.time()-t_start:6.1f}s T {T:.4g} cur {cur:08x} best {best:08x} '
                        f'S {r[0]:,} total {r[2]:,} eta {r[4]:08x}\n')
            trace.flush()
    return best


def main():
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 540
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    share = float(sys.argv[3]) if len(sys.argv) > 3 else 0.35
    try:
        os.nice(5)
    except OSError:
        pass
    with open(os.path.join(D, 'heur.pid'), 'w') as f:
        f.write(f'{os.getpid()}\n')
    rng = random.Random(seed)
    t0 = time.time()
    log = open(os.path.join(D, f'evals_s{seed}.tsv'), 'w')
    log.write('phase\tn\te1\teta\tfixed_bits\tS\tr7\ttotal\trows\trc\tsec\n')
    trace = open(os.path.join(D, f'trace_s{seed}.txt'), 'w')
    ev = Evaluator(log)
    # self-test against the two baseline outputs computed by one_cube.sh
    for e1 in (0x070C0307,):
        r = ev(e1, 'T')
        trace.write(f'selftest {e1:08x}: S {r[0]:,} r7 {r[1]:,} total {r[2]:,} rows {r[3]} eta {r[4]:08x}\n')
        assert r[0] == CLASS_S and r[2] == BEST_TOTAL, r
    # phase A: inside the class
    start = CV
    for b in FREE:
        if rng.random() < 0.5:
            start |= 1 << b
    dlA = t0 + secs * share
    bestA = anneal(ev, rng, 'A', start, FREE, score_A, 0.1, 0.003, dlA, trace)
    nA = ev.n
    # phase B: all 32 bits, class (eta) free
    bestB = anneal(ev, rng, 'B', bestA, list(range(32)), score_B, 1.0, 0.01, t0 + secs, trace)
    # summary
    rows = list(ev.cache.items())
    inA = [(e, r) for e, r in rows if e & CM == CV]
    Svals = sorted({r[0] for _, r in inA})
    Tvals = sorted({r[2] for _, r in inA})
    trace.write(f'\nevaluations {ev.n} (phase A {nA}), binary seconds {ev.secs:.1f}, wall {time.time()-t0:.1f}\n')
    trace.write(f'class members evaluated: {len(inA)}; distinct S values {len(Svals)}: {Svals[:5]}...{Svals[-3:]}\n')
    trace.write(f'class members: distinct total values {len(Tvals)}; max total {Tvals[-1]:,} '
                f'(best known {BEST_TOTAL:,}); members above best known: '
                f'{sum(1 for _, r in inA if r[2] > BEST_TOTAL)}; S above {CLASS_S:,}: '
                f'{sum(1 for _, r in inA if r[0] > CLASS_S)}\n')
    etas = {}
    for e, r in rows:
        k = r[4]
        if k not in etas or r[2] > etas[k][1][2]:
            etas[k] = (e, r)
    trace.write(f'distinct eta (classes) visited: {len(etas)}\n')
    for k, (e, r) in sorted(etas.items(), key=lambda kv: -kv[1][1][2])[:15]:
        trace.write(f'  eta {k:08x} fixed {r[5]:2d}: best member {e:08x} total {r[2]:,} S {r[0]:,} r7 {r[1]:,} rows {r[3]}\n')
    rb = ev.cache[bestB]
    trace.write(f'best overall (phase B) {bestB:08x} eta {rb[4]:08x}: total {rb[2]:,} S {rb[0]:,} rows {rb[3]}\n')
    trace.close()
    log.close()
    os.remove(os.path.join(D, 'heur.pid'))


if __name__ == '__main__':
    main()
