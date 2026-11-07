# PNB count (afkmr08 Def. 1) for 2-round BLAKE3 pins. Read-only use of hash-smash/verifier/blake3.py.
# (A) pins X3,X7,X11,X15 after round 0; (B) R=2 output words 0,2,5,7. Flip each of the 512 message bits.
import sys, random, importlib.util
spec = importlib.util.spec_from_file_location("b3", sys.argv[1]); b3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(b3)
N = int(sys.argv[2]); rnd = random.Random(1019)
def round0(cv, m, ctr, bl, fl):
    v = list(cv) + list(b3.IV[:4]) + [ctr & b3.MASK, ctr >> 32, bl, fl]
    for i, (a, b, c, d) in enumerate([(0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14)]):
        b3._g(v, a, b, c, d, m[2*i], m[2*i+1])
    return (v[3], v[7], v[11], v[15])
def out2(cv, m, ctr, bl, fl):
    o = b3._compress(cv, m, ctr, bl, fl, 2); return (o[0], o[2], o[5], o[7])
okA = [0]*512; okB = [0]*512; perA = [[0]*4 for _ in range(512)]
for _ in range(N):
    cv = [rnd.getrandbits(32) for _ in range(8)]; m = [rnd.getrandbits(32) for _ in range(16)]
    m[14] = m[15] = 0; m[13] &= 0x00FFFFFF; ctr = rnd.getrandbits(40); bl, fl = 63, 2 | 8
    xa, xb = round0(cv, m, ctr, bl, fl), out2(cv, m, ctr, bl, fl)
    for k in range(512):
        m2 = list(m); m2[k >> 5] ^= 1 << (k & 31)
        ya = round0(cv, m2, ctr, bl, fl)
        for j in range(4): perA[k][j] += ya[j] == xa[j]
        okA[k] += ya == xa; okB[k] += out2(cv, m2, ctr, bl, fl) == xb
free = [k for k in range(512) if (k >> 5) not in (4, 13)]
pA = [okA[k]/N for k in free]; pB = [okB[k]/N for k in free]
print("N", N, "free bits", len(free))
print("A pins X3,X7,X11,X15: count p>=0.9 =", sum(p >= 0.9 for p in pA), " max p =", max(pA))
print("B out words 0,2,5,7 (R=2): count p>=0.9 =", sum(p >= 0.9 for p in pB), " max p =", max(pB))
best = max(free, key=lambda k: max(perA[k])); print("best single-pin bit", best, [x/N for x in perA[best]])
