'''Bit-level moves with E3 held and NO re-solve: on real points, flip each single bit (and each adjacent bit pair) of each
free word of the design, keep g, and test whether the check still holds (i.e. Y4, Y9, w8 unchanged).'''
import sys, random
sys.dont_write_bytecode = True
from ev import Design, DESIGN, real_point
d = Design(*DESIGN)
rnd = random.Random(3); keep1 = keep2 = tot1 = tot2 = 0
for _ in range(100):
    v = real_point(rnd)
    base = {w: v[w] for w in d.F + d.B + (d.g,)}
    for w in d.B:
        for i in range(32):
            for mask, single in ((1 << i, True), ((3 << i) & 0xFFFFFFFF, False)):
                s = dict(base); s[w] ^= mask
                ok = d.run(s)[1]
                if single: keep1 += ok; tot1 += 1
                else: keep2 += ok; tot2 += 1
print('single-bit flips of free words keeping the check: %d/%d ; adjacent-pair flips: %d/%d' % (keep1, tot1, keep2, tot2))
