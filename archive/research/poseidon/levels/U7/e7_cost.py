# E7: cost of x^5 vs x^d (d = 5^-1 mod p-1), forward vs backward per level.
import time, random
from common import *
import gmpy2
d = inv(5, P-1)
print("d = 5^-1 mod (p-1) =", hex(d), " bits", d.bit_length(), " hamming weight", bin(d).count("1"))
assert (d*5) % (P-1) == 1
# multiplication counts
sq = d.bit_length()-1; mul_bin = bin(d).count("1")-1
print("x^5: 2 squarings + 1 multiplication = 3 field mults (x^2, x^4, x^4*x)")
print("x^d left-to-right binary: %d squarings + %d multiplications = %d" % (sq, mul_bin, sq+mul_bin))
# sliding window w
def sliding(e, w):
    bits = bin(e)[2:]; i = 0; muls = 0; table = (1 << (w-1))  # odd powers precomp: 1 sq + (2^(w-1)-1) muls
    pre = 1+(2**(w-1)-1)
    n = len(bits)
    while i < n:
        if bits[i] == '0': i += 1; continue
        j = min(i+w, n)
        while bits[j-1] == '0': j -= 1
        muls += 1; i = j
    return (n-1)+muls-1+pre   # n-1 squarings, window multiplications, minus 1 for the first (initial value)
best = min((sliding(d, w), w) for w in range(2, 8))
print("x^d sliding window (best w=%d): ~%d field mults" % (best[1], best[0]), "  ratio to x^5:", round(best[0]/3, 1))
print("x^d cost vs x^5 (field-mult count): about %.0fx" % (best[0]/3))
# timing
x = random.Random(1).randrange(2, P)
for name, e in (("x^5", 5), ("x^d", d)):
    t = time.perf_counter(); n = 2000 if e == 5 else 200
    for _ in range(n): pow(x, e, P)
    py = (time.perf_counter()-t)/n
    X = mpz(x); Pm = mpz(P); em = mpz(e)
    t = time.perf_counter()
    for _ in range(n): gmpy2.powmod(X, em, Pm)
    gm = (time.perf_counter()-t)/n
    print("timing %s: python pow %.2f us, gmpy2.powmod %.2f us" % (name, py*1e6, gm*1e6))
print("note: tiny exponents are dominated by call overhead; use the mult counts above as the cost model.")
# per-level table
S5 = 3; Sd = best[0]; MDSm = 9
print("\n=== per-level cost in field multiplications (additions/constants ignored), r=1 and r=2 ===")
print("forward round: full = 3 S-boxes (9) + MDS (9) = 18; partial = 1 S-box (3) + MDS (9) = 12; R0 = 2 live S-boxes + M*(A,B,K) with K precomputed = 6+9 = 15 (can be 6 if K is folded: M*(A,B,K) = A*m0+B*m1+const => 6); R63 = 3 S-boxes + row 0 only (3) = 12")
print("backward round (state after M -> state before C): M^-1 (9) + inverse S-boxes: full = 3*%d, partial = 1*%d (other lanes unchanged)" % (Sd, Sd))
rows = {}
for r in (1, 2):
    sched = PR.schedule(r)
    lv = []
    for lvl, idx in enumerate(sched, 1):
        full = idx < 4 or idx >= 60
        if idx == 0: fw = 6+6   # 2 live sboxes + 6 mults for A m0 + B m1 (K m2 folded)
        elif idx == 63: fw = 9+3
        else: fw = 18 if full else 12
        if idx == 0: bw = 2*Sd   # invert lanes 0,1 only (need lane-2 consistency check from the plane); M^-1 9 as well
        elif idx == 63: bw = 9+3*Sd   # from a chosen full state; inverse M
        else: bw = 9+(3*Sd if full else Sd)
        if idx == 0: bw += 9
        lv.append((idx, "L%d" % lvl, fw, bw))
    rows[r] = lv
    print("\nr=%d: level / orig round / forward mults / backward mults" % r)
    for idx, L, fw, bw in lv: print("  %-4s R%-3d forward %3d   backward %6d" % (L, idx, fw, bw))
    print("  total forward", sum(x[2] for x in lv), "  total backward", sum(x[3] for x in lv))
# meet-in-the-middle prefix costs
print("\nforward-vs-backward at a split point (cumulative mults) for r=1: split after level k: forward k levels, backward 9-k levels")
lv = rows[1]
for k in range(0, 10):
    f = sum(x[2] for x in lv[:k]); b = sum(x[3] for x in lv[k:])
    print("  split after L%d: forward prefix %5d + backward suffix %7d = %7d" % (k, f, b, f+b))
print("\nA full backward step is ~%dx a forward step per S-box; backward through the 4 final full rounds costs %d vs forward %d." % (round(Sd/3), sum(x[3] for x in lv[-4:]), sum(x[2] for x in lv[-4:])))
# timing a whole forward hash and a whole backward chain
t = time.perf_counter()
for _ in range(200): PR.hash_reduced(12345, 678910, 1)
print("python big-int: one forward hash (r=1) %.1f us" % ((time.perf_counter()-t)/200*1e6))
def inv5(y): return pow(y, d, P)
t = time.perf_counter()
for _ in range(20): [inv5(v) for v in range(1000, 1000+24)]
print("python big-int: 24 inverse S-boxes %.1f us (one backward pass would invert ~24)" % ((time.perf_counter()-t)/20*1e6))
