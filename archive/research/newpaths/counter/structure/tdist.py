"""Distribution of the counter t over the T1 cube for one outer step: constant bits, top-bit histogram,
and the same for random (uncubed) E1.d1.  usage: python -B tdist.py NOUTER SEED"""
import sys, random
import numpy as np
import arrange_check as AC

rng = random.Random(int(sys.argv[2]))
free_cube = [i for i in range(32) if not AC.CUBE_MASK >> i & 1]
k = np.arange(1 << 21, dtype=np.uint32)
c1 = np.full(1 << 21, AC.CUBE_VAL, dtype=np.uint32)
for j, i in enumerate(free_cube):
    c1 |= ((k >> np.uint32(j)) & np.uint32(1)) << np.uint32(i)
u = np.uint32


def tvec(o, d1):
    a1 = AC.np_rol(d1, 16) ^ u(o['Y12'])
    Y6 = (a1 - u(o['Y1']) - u(o['w12'])).astype(np.uint32)
    Y10 = AC.np_rol(Y6, 7) ^ u(o['C2b1'])
    Y14 = (Y10 - u(o['C2c1'])).astype(np.uint32)
    Y2 = AC.np_rol(Y14, 8) ^ u(o['C2d1'])
    w0 = (Y2 - u(o['C2a1']) - u(o['C2b1'])).astype(np.uint32)
    return (u(AC.rol(o['K0d1'], 16)) ^ (u(AC.IV[0]) + u(AC.IV[4]) + w0)).astype(np.uint32)


for oi in range(int(sys.argv[1])):
    o = AC.outer(*[rng.getrandbits(32) for _ in range(7)], AC.sub_member(rng))
    d1 = (c1 - u(AC.Y11A)).astype(np.uint32)
    t = tvec(o, d1)
    an = int(np.bitwise_and.reduce(t)); orr = int(np.bitwise_or.reduce(t))
    const = ~(an ^ orr) & 0xFFFFFFFF
    # per-bit bias
    bits = [(t >> u(b)) & u(1) for b in range(32)]
    bias = [abs(float(x.mean()) - 0.5) for x in bits]
    strong = [b for b in range(32) if bias[b] > 0.45]
    rnd = np.array([rng.getrandbits(32) for _ in range(1 << 16)], dtype=np.uint32)
    tr = tvec(o, rnd)
    print(f'outer {oi}: constant bits of t over the cube {const:08x} (n={bin(const).count("1")}), '
          f'bits with |P-1/2| > 0.45: {strong}; min t {int(t.min())}; random d1: min t over 2^16 {int(tr.min())}')
