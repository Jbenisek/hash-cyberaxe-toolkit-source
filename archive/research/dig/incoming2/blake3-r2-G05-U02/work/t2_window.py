"""T2: window rates of the 128-bit residual (digest words 1,3,4,6) for h = IV vs one non-IV word. LOCAL_ONLY (low-k-bit windows)."""
import sys, time, json, math
sys.path.insert(0, '.')
from b3init import *
import warnings
warnings.simplefilter('ignore')
CH = 1 << 20
NCH = int(sys.argv[1]) if len(sys.argv) > 1 else 64
budget = float(sys.argv[2]) if len(sys.argv) > 2 else 600
rr = np.random.default_rng(2026)
cfgs = {'IV': {}, 'h4': {4: 0x1badb002}, 'h5': {5: 0xdeadbeef}, 'h7': {7: 0x0c0ffee1}, 'h6': {6: 0x1F83D9AB + 16 * 12345}}
K = (IV[2] + (0x1F83D9AB + 16 * 12345)) & M
assert ((K + PIN['w4']) >> 3) & 1 == 0
res = {}
t0 = time.time()
tot_n = 0
for name, mod in cfgs.items():
    h = list(IV)
    for i, v in mod.items(): h[i] = v
    hits16 = np.zeros(4, dtype=np.int64); hits20 = np.zeros(4, dtype=np.int64); allw = 0; n = 0
    zero_full = np.zeros(4, dtype=np.int64)
    rs = np.random.default_rng(99)   # identical X-free draws for every configuration
    for _ in range(NCH):
        fr = {i: rs.integers(0, 1 << 32, size=CH, dtype=np.uint64).astype(U) for i in FREE}
        w, wb, X, S = derive(h, PIN, fr)
        r = tail(h, PIN, X, w, wb)
        for j in range(4):
            hits16[j] += int(np.count_nonzero((r[j] & U(0xFFFF)) == 0))
            hits20[j] += int(np.count_nonzero((r[j] & U(0xFFFFF)) == 0))
            zero_full[j] += int(np.count_nonzero(r[j] == 0))
        n += CH
        if time.time() - t0 > budget: break
    res[name] = dict(n=n, hits16=hits16.tolist(), hits20=hits20.tolist(), zero32=zero_full.tolist())
    print(name, res[name], 'elapsed %.0fs' % (time.time() - t0), flush=True)
    tot_n += n
json.dump(res, open('t2_out.json', 'w'))
# z-scores of each configuration against 2^-k expectation
for name, r in res.items():
    z = []
    for j in range(4):
        e = r['n'] / 65536.0
        z.append((r['hits16'][j] - e) / math.sqrt(e))
    e20 = r['n'] / 1048576.0
    z20 = [(r['hits20'][j] - e20) / math.sqrt(e20) for j in range(4)]
    print(name, 'n=%d  z16=%s  z20=%s' % (r['n'], ['%.2f' % x for x in z], ['%.2f' % x for x in z20]))
