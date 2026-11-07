"""T1: replace h[i] (i=4..7) by non-IV values; check round-0 inverse, exact half collision, and for h6 the bit-3 rule."""
import sys, random, json
sys.path.insert(0, '.')
from b3init import *
import warnings
warnings.simplefilter('ignore')
rn = np.random.default_rng(7)
rr = random.Random(11)
out = {}

def run(h, n=300, t=0, flags=3):
    fr = rand_free(rn, n)
    w, wb, X, S = derive(h, PIN, fr, t=t, flags=flags)
    bx = bh = 0
    for k in range(n):
        wa = [int(a[k]) for a in w]; wbb = [int(a[k]) for a in wb]
        v0, _ = my_compress(h, wa, t, 55, flags, 1)
        _, oa = my_compress(h, wa, t, 55, flags, 2)
        _, ob = my_compress(h, wbb, t, 63, flags, 2)
        bx += [int(x[k]) for x in X] != v0
        bh += not all(oa[i] == ob[i] for i in (0, 2, 5, 7))
    dw4 = (int(wb[4][0]) - PIN['w4']) & M
    return n, bx, bh, dw4

for i in (4, 5, 7):
    rows = []
    for trial in range(8):
        h = list(IV); h[i] = rr.getrandbits(32)
        n, bx, bh, dw4 = run(h, t=rr.getrandbits(32))
        rows.append((h[i], n, bx, bh, dw4))
    tot = sum(r[1] for r in rows)
    print('h[%d] -> 8 random non-IV values, random t, flags 3: samples %d, round0-inverse mismatches %d, half-collision failures %d, W4B-W4 = %s'
          % (i, tot, sum(r[2] for r in rows), sum(r[3] for r in rows), sorted({hex(r[4]) for r in rows})))
    out['h%d' % i] = dict(samples=tot, x_bad=sum(r[2] for r in rows), half_fail=sum(r[3] for r in rows))
# all four at once
h = list(IV)
for i in (4, 5, 6, 7): h[i] = rr.getrandbits(32)
K = (IV[2] + h[6]) & M
print('all four h4..h7 random; bit3(K+W4)=%d' % (((K + PIN['w4']) >> 3) & 1), run(h))

# h6: all 16 residues mod 16 x 40 random upper parts
res = {}
for r in range(16):
    fails = 0; tot = 0; dws = set()
    for u in range(40):
        h6 = ((rr.getrandbits(28) << 4) | r) & M
        h = list(IV); h[6] = h6
        n, bx, bh, dw4 = run(h, n=20)
        assert bx == 0
        fails += (bh > 0); tot += 1; dws.add(dw4)
    K = (IV[2] + ((0 << 4) | r)) & M
    res[r] = (tot, fails, sorted(hex(x) for x in dws))
valid = [r for r in range(16) if res[r][1] == 0]
invalid = [r for r in range(16) if res[r][1] == res[r][0]]
mixed = [r for r in range(16) if r not in valid and r not in invalid]
print('h6 residues mod 16 with exact half collision (all 40 draws pass):', valid)
print('h6 residues failing every draw:', invalid, ' mixed:', mixed)
for r in range(16): print('  r=%2d  draws=%d fail=%d  W4B-W4=%s' % (r, *res[r][:2], res[r][2]))
# predicted by bit 3 of (IV2+h6+W4)
pred_ok = []
for r in range(16):
    x = (IV[2] + r + PIN['w4']) & M  # only low 4 bits of h6 matter for bit3 given the carries: need low bits of IV2+W4 too
pred = [r for r in range(16) if ((((IV[2] + PIN['w4'] + r) & M) >> 3) & 1) == (((IV[2] + IV[6] + PIN['w4']) >> 3) & 1) ]
print('current IV[6] mod 16 =', IV[6] & 15, ' bit3(K+W4) =', ((IV[2] + IV[6] + PIN['w4']) >> 3) & 1)
print('rule check: valid iff bit3(IV2+h6+W4) == 0 ; predicted residues (low 4 of h6, carry from low 4 bits of IV2+W4 included):')
lo = (IV[2] + PIN['w4']) & 15
pr = [r for r in range(16) if ((((lo + r) >> 3) & 1) == 0)]
print(pr, ' matches measured:', pr == valid)
json.dump(dict(h6_valid_residues=valid, h6_invalid=invalid, h6_mixed=mixed, rest=out), open('t1_out.json', 'w'))
