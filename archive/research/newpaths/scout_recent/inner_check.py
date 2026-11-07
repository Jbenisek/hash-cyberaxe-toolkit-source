#!/usr/bin/env python3
"""inner_check.py ORDERFILE [N]  (scout_recent; research only)
For an arrangement whose inner word is E1.d1 (ctr_cone4.sh): hold the other eight basis words fixed (Y4 in the eta
class, E1.d1 varied inside the heavy beta cube of the team's T1 prize, c1 & 0e09818b == 02008000), solve the
whole order for each inner value at 32 bits, and report which words change with the inner word and which inputs
of the per-trial cone stay fixed.  Also runs the real compression for every trial (correctness of all words).
"""
import sys, random, re
sys.argv += [] ; import verify_ctr as V

path = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 200
rng = random.Random(11)
txt = open(path).read().splitlines()
basis = re.search(r'basis = ([^|]*)', txt[0]).group(1).split()
lines = [(l.split('<-')[0].replace('*', ' ').strip(), l.split('<-')[1].split()) for l in txt[1:] if '<-' in l and 'cone of' not in l]
CM, CV = 0x0E09818B, 0x02008000


def cube_d1():
    c1 = (rng.getrandbits(32) & ~CM | CV) & V.MASK
    return (c1 - V.Y11A) & V.MASK          # E1.c1 = Y11 + E1.d1


class FixedRng:
    def __init__(self, vals): self.vals = vals
def solve_with(fixed):
    val = dict(V.PIN); val.update(fixed); V.expand(val)
    for Vn, deps in lines:
        # reuse verify_ctr's line resolver by calling solve_order on a one-off basis dict
        pass
    return None


outer = {b: (V.class_member(rng.randrange(1 << len(V.CFREE))) if b == 'Y4' else rng.getrandbits(32)) for b in basis if b != 'E1.d1'}
runs = []
bad = 0; nohalf = 0; incube = 0
for _ in range(N):
    bv = dict(outer); bv['E1.d1'] = cube_d1()
    r = random.Random(0)
    # solve_order draws basis values from rng; give it a stub rng returning our fixed values in basis order
    vals = [bv[b] for b in basis]
    class Stub:
        def __init__(s): s.i = 0
        def randrange(s, n):
            v = vals[s.i]; s.i += 1
            return v if n == 1 << 32 else None
    st = Stub()
    # Y4: solve_order calls class_member(randrange(2^19)); bypass by patching class_member temporarily
    orig = V.class_member; V.class_member = lambda k: bv['Y4']
    try:
        val = V.solve_order(lines, basis, st)
    finally:
        V.class_member = orig
    wA = [val[f'w{i}'] for i in range(16)]
    wB = list(wA); wB[4] = V.W4B; wB[5] = (wA[5] + V.DELTA) & V.MASK
    recA, dA = V.real_run(wA, val['T0'], V.LEN_A); _, dB = V.real_run(wB, val['T0'], V.LEN_B)
    if any(recA[k] != val[k] for k in val if k in recA): bad += 1
    if any(dA[i] != dB[i] for i in (0, 2, 5, 7)): nohalf += 1
    if (recA['E1.c1'] & CM) == CV: incube += 1
    runs.append(val)
names = sorted(runs[0])
change = [k for k in names if len({r[k] for r in runs}) > 1]
fixedw = [k for k in names if k not in change]
print(f'{path}: basis {basis}, inner E1.d1, {N} inner values')
print(f'  real-compression mismatches {bad}; half-collision failures {nohalf}; E1.c1 in the T1 cube {incube}/{N}')
print(f'  words that change with the inner word ({len(change)}): {" ".join(change)}')
for w in ('Y4', 'Y12', 'Y1', 'w12', 'C2.b1', 'C2.c1', 'Y9', 'w8', 'w5'):
    print(f'  {w}: {"fixed" if w in fixedw else "CHANGES"}')
