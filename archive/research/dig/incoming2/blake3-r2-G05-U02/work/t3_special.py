"""T3: special non-IV values for h4,h5,h7 (and h6 when the bit-3 rule holds): zero, all-ones, top bit, IV^1, IV+-1, a neighbour IV word."""
import sys
sys.path.insert(0, '.')
from b3init import *
import warnings
warnings.simplefilter('ignore')
rn = np.random.default_rng(3)
tot = {4: [0, 0, 0], 5: [0, 0, 0], 6: [0, 0, 0], 7: [0, 0, 0]}
skipped6 = 0
for i in (4, 5, 6, 7):
    cands = [0, M, 0x80000000, 1, IV[i] ^ 1, (IV[i] + 1) & M, (IV[i] - 1) & M, IV[(i + 1) % 8], IV[i - 4], (IV[i] ^ M)]
    for v in cands:
        h = list(IV); h[i] = v
        if i == 6 and ((((IV[2] + v + PIN['w4']) & M) >> 3) & 1) != 0:
            skipped6 += 1; continue
        n = 200
        fr = rand_free(rn, n)
        w, wb, X, S = derive(h, PIN, fr, t=5, flags=3)
        bx = bh = 0
        for k in range(n):
            wa = [int(a[k]) for a in w]; wbb = [int(a[k]) for a in wb]
            v0, _ = my_compress(h, wa, 5, 55, 3, 1)
            _, oa = my_compress(h, wa, 5, 55, 3, 2); _, ob = my_compress(h, wbb, 5, 63, 3, 2)
            bx += [int(x[k]) for x in X] != v0
            bh += not all(oa[j] == ob[j] for j in (0, 2, 5, 7))
        tot[i][0] += n; tot[i][1] += bx; tot[i][2] += bh
for i in tot: print('h[%d] special values: samples %d  inverse mismatches %d  half-collision failures %d' % (i, *tot[i]))
print('h6 candidates skipped by the bit-3 rule:', skipped6)
