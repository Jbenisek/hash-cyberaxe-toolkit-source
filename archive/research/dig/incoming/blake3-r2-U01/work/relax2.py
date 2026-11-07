# necessity sampling (no false reject by automaton / PF for any (Q,h) with J1) + cost arithmetic from printed units

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

import sys, random, math, json
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/traillab/b3atlas'))
from rows_dp import ETA, M
THETA = 0x830F03C7
def j1(Q, h): return (((Q + h) & M) ^ ((Q + (h ^ ETA)) & M)) == THETA
def maj(a, b, c): return (a & b) | (a & c) | (b & c)
def auto_accept(x):
    S = {(0, 0)}
    for i in range(32):
        e = (ETA >> i) & 1; t = (THETA >> i) & 1; xi = (x >> i) & 1; N = set()
        for (ca, cb) in S:
            if e ^ ca ^ cb != t: continue
            for hi in (0, 1): N.add((maj(xi, hi, ca), maj(xi, hi ^ e, cb)))
        S = N
        if not S: return False
    return True
def pf_accept(x): return (x & 0x3c7) in (0x004, 0x3c4)
random.seed(20261012)
def solve_Q(h):
    # randomized DFS for Q with J1(Q,h): state (ca,cb)
    sys.setrecursionlimit(10000)
    def rec(i, ca, cb, q):
        if i == 32: return q
        hi = (h >> i) & 1; e = (ETA >> i) & 1; t = (THETA >> i) & 1
        if e ^ ca ^ cb != t: return None
        for qi in random.sample((0, 1), 2):
            r = rec(i + 1, maj(qi, hi, ca), maj(qi, hi ^ e, cb), q | (qi << i))
            if r is not None: return r
        return None
    return rec(0, 0, 0, 0)
n = 0; tried = 0; bad_auto = 0; bad_pf = 0; bad_j1 = 0
while n < 3000:
    h = random.getrandbits(32); tried += 1
    Q = solve_Q(h)
    if Q is None: continue
    n += 1
    if not j1(Q, h): bad_j1 += 1
    if not auto_accept(Q): bad_auto += 1
    if not pf_accept(Q): bad_pf += 1
print('J1 solutions sampled', n, 'from', tried, 'h; formula-check fails', bad_j1, ' (1)-automaton rejects', bad_auto, ' PF rejects', bad_pf)
# false-accept rate of PF among random words, measured vs exact
N = 400000; a = p = 0
for _ in range(N):
    x = random.getrandbits(32); a += auto_accept(x); p += pf_accept(x)
print('random words: automaton pass %d (%.5f, exact %.5f)  PF pass %d (%.5f, exact %.5f)' % (a, a/N, 14110208/2**32, p, p/N, 1/64))
# cost arithmetic from printed units (proof.md 9.8/11): word 50 = 46+7-3 incl. PF 7; kept word +24; WB share 83.1%
def kept(p): return 1 - (1 - p) ** 7
def word_cost(keep, upf=7): return 43 + upf + 24 * keep
res = {}
base = word_cost(kept(1/64))
print('base word cost %.3f units, kept frac %.4f' % (base, kept(1/64)))
res['base'] = dict(cost=base, kept=kept(1/64))
def bits(ratio): return math.log2(0.17 + 0.83 * ratio)
cases = {
 'no PF (every word kept, no PF op)': (43 + 24, 0, kept(1.0)),
 'PF as shipped (7 low bits, 1/64)': (base, 7, kept(1/64)),
 'exact 14 prefixes of 10 bits (1/73.14) same 7 ops': (word_cost(kept(14/1024)), 7, kept(14/1024)),
 'prefix 20 bits (29130752/2^32) same 7 ops, ceiling': (word_cost(kept(29130752/2**32)), 7, kept(29130752/2**32)),
 'exact (1) as prefilter (ceiling, free)': (word_cost(kept(14110208/2**32)), 7, kept(14110208/2**32)),
 'relaxed PF to 6 bits (prefix 8: 0.0547)': (word_cost(kept(234881024/2**32)), 7, kept(234881024/2**32)),
}
for k, (c, u, kp) in cases.items():
    print('%-55s cost/word %.3f kept %.4f ratio-to-base %.4f  bits on log2 N (WB 83.1%%) %+.4f' % (k, c, kp, c/base, bits(c/base)))
    res[k] = dict(cost=c, kept=kp, ratio=c/base, bits=bits(c/base))
json.dump(dict(n_samples=n, bad_auto=bad_auto, bad_pf=bad_pf, bad_j1=bad_j1, auto_rate=a/N, pf_rate=p/N, cost=res), open('relax2_out.json', 'w'), indent=1)
