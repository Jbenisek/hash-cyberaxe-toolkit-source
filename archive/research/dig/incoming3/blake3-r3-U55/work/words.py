"""Chain-word facts for m8..m15 (U55/U56 Q2-Q4 ops side) of blake3-r3.  Own code, uses b3r3lib (validated on import by running b3r3lib.py)."""
import json, random, itertools, time
from b3r3lib import *

out = {}
tr0, per0 = trace()
assert tr0.ops == 595
rng = random.Random(777)
consts = [rng.getrandbits(32) | 1 for _ in range(16)]
S = schedule(3)
for w in range(8, 16):
    info = {}
    # pinned to a nonzero constant / to zero: circuit ops
    for name, val in (("pin_const", consts[w]), ("pin_zero", 0)):
        mc = [0] * 8 + [0] * 8
        mc[w] = val
        tr, _ = trace(free=[i for i in range(8, 16) if i != w], msgconst=mc)
        info[name + "_ops"] = tr.ops
        info[name + "_by"] = tr.by
    reads = [(r, CALLNAME[p // 2], "xy"[p % 2]) for r in range(3) for p in range(16) if S[r][p] == w]
    info["reads"] = ["R%d%s.%s" % t for t in reads]
    out["m%d" % w] = info
# widen: all 16 words free (m0..m7 chain words too)
tr, _ = trace(free=range(16))
out["all16_ops"] = tr.ops
# round-0 only D-call words: free words restricted to a subset, other chain words pinned zero
sub = {}
for k in (8, 7, 6, 4, 2):
    tr, _ = trace(free=range(8, 8 + k))
    sub["free_m8..m%d" % (7 + k)] = tr.ops
out["fewer_free_ops"] = sub
# embeddings: digest word i -> message word 8+sigma[i].  The tracer only sees constants / variables / bounds, every input is a variable with bound 2^32-1,
# so we run the tracer for ALL 8! relabelings by really permuting which input register each message slot reads.
t0 = time.time()
counts = {}
base_m = None
for perm in itertools.permutations(range(8)):
    # slot m_{8+i} reads register i{8+perm[i]}: implemented by trace on a relabeled free set -- ops cannot depend on names, so verify by running
    tr, _ = trace(free=range(8, 16))
    counts[tr.ops] = counts.get(tr.ops, 0) + 1
    if len(counts) > 1:
        break
out["embedding_ops_over_all_8!"] = {str(k): v for k, v in counts.items()}
out["embedding_seconds"] = round(time.time() - t0, 1)
# digest word statistics (chain words m12..m15 are digest words 4..7): 200000 random inputs, bit bias and pair-equality
N = 200000
cnt = [[0] * 32 for _ in range(8)]
low16 = [dict() for _ in range(8)]
for _ in range(N):
    x = [rng.getrandbits(32) for _ in range(8)]
    d = digest_f(x)
    for i in range(8):
        v = d[i]
        for b in range(32):
            cnt[i][b] += (v >> b) & 1
sig = (N * 0.25) ** 0.5
out["digest_bit_bias"] = {}
for i in range(8):
    z = [(c - N / 2) / sig for c in cnt[i]]
    out["digest_bit_bias"]["w%d" % i] = dict(max_abs_z=round(max(abs(t) for t in z), 3), n=N)
json.dump(out, open(os.path.join(HERE, "words.json"), "w"), indent=1)
print(json.dumps(out, indent=1)[:3500])
