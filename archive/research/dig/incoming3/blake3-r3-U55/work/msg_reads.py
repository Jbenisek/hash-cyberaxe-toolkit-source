"""Per-read facts for the 48 reads (3 rounds x 8 calls x x/y) of the blake3-r3 target 0^32||x. Own code.
Output: msg_reads.json  {key 'R0C0.x': {...}}"""
import json, random, os
from b3r3lib import *

S = schedule(3)
tr0, per0 = trace()
assert tr0.ops == 595
rng = random.Random(20261012)
TR = 400
res = {}
for r in range(3):
    for j in range(8):
        for pos in (0, 1):
            w = S[r][2 * j + pos]
            key = "R%d%s.%s" % (r, CALLNAME[j], "xy"[pos])
            var = w >= 8
            tr, _ = trace(drop=(r, j, pos))
            # perturb ONLY this read (xor random delta) with random chain words; count digest words and bits that change
            wchg = [0] * 8
            anyw = []
            bits = 0
            for _ in range(TR):
                x = [rng.getrandbits(32) for _ in range(8)]
                d0 = digest_f(x)
                delta = rng.getrandbits(32) | 1
                d1 = digest_f(x, perturb=lambda rr, jj, pp, val: (val ^ delta) if (rr, jj, pp) == (r, j, pos) else val)
                ch = [a ^ b for a, b in zip(d0, d1)]
                n = sum(1 for c in ch if c)
                anyw.append(n)
                for i, c in enumerate(ch):
                    if c:
                        wchg[i] += 1
                bits += sum(bin(c).count("1") for c in ch)
            # also: is the value read really m[w]? check by marking
            rec = []
            compress(list(range(100, 116)), 3, record=rec)
            seen = [t for t in rec if t[:3] == (r, j, pos)][0][3]
            assert seen == w
            res[key] = dict(round=r, call=CALLNAME[j], pos="xy"[pos], word=w, var=var,
                            read_ops=per0[(r, j)]["xadd" if pos == 0 else "yadd"], call_ops=per0[(r, j)]["total"],
                            drop_total=tr.ops, drop_delta=tr.ops - 595,
                            mean_words_changed=sum(anyw) / TR, min_words_changed=min(anyw), digest_words_hit=wchg,
                            mean_bits_changed=bits / TR, trials=TR)
json.dump(res, open(os.path.join(HERE, "msg_reads.json"), "w"), indent=1)
# summary
byw = {}
for k, v in res.items():
    byw.setdefault(v["word"], []).append((k, v["read_ops"], v["drop_delta"]))
for w in sorted(byw):
    print("m%d" % w, byw[w])
print("sum of read_ops", sum(v["read_ops"] for v in res.values()), "calls total", sum(v["call_ops"] for k, v in res.items() if k.endswith(".x")))
