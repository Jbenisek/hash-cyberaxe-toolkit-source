"""sizecap.py: the method's size limit. What the counter lever is worth when the message length is capped.

A cap of L bytes means t <= (L - 63) / 1024, i.e. t < 2^k. Two ways to meet it (32-bit real arithmetic):
  F (filter): generate cube trials as the lever does and drop those with t >= 2^k;
  I (invert): per outer step, run every t < 2^k backwards through the bijection t -> c1 (about 14 word ops)
     and keep the c1 that fall in the T1 cube.
Part 1 (COMPUTED): over random outer steps, the mean number of cube members with t < 2^k (whole cube, 2^21 per
  outer step, for k = 12..32), and the same count by inversion for k = 12; spread across outer steps.
Part 2 (DERIVED, the one formula of counter\\adjudicate\\adj_check.py with ops GUESSES):
  time_log2 = 84.96 + log2(cost per kept trial / 6.5), against the filed 92.53.
  F: cost = 11 * 2^(32-k) + 6.5 (11 ops to reach t, GUESS); I: cost = (OUTER + 14 * 2^k) * 2^(11-k) + 6.5
  (OUTER = 400 ops per outer step, the census GUESS).
Part 3 (COMPUTED): speed of the organizer's Python _compress (2 rounds), to price a reference check of a pair.
usage: python -B sizecap.py NOUTER SEED
"""
import math
import random
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
import arr
import blake3_ref as V

M = 0xFFFFFFFF
IV = V.IV


def nrol(x, n):
    return (x << np.uint32(n)) | (x >> np.uint32(32 - n))


def cube_all():
    k = np.arange(1 << 21, dtype=np.uint32)
    c1 = np.full(1 << 21, arr.CUBE_VAL, dtype=np.uint32)
    for j, i in enumerate(arr.FREE_CUBE):
        c1 |= ((k >> np.uint32(j)) & np.uint32(1)) << np.uint32(i)
    return c1


def t_of_c1(o, c1):
    u = np.uint32
    with np.errstate(over='ignore'):
        d1 = c1 - u(arr.Y11A)
        a1 = nrol(d1, 16) ^ u(o['Y12'])
        Y6 = a1 - u(o['Y1']) - u(o['w12'])
        Y10 = nrol(Y6, 7) ^ u(o['C2b1'])
        Y14 = Y10 - u(o['C2c1'])
        Y2 = nrol(Y14, 8) ^ u(o['C2d1'])
        w0 = Y2 - u(o['C2a1']) - u(o['C2b1'])
        t = u(arr.rol(o['K0d1'], 16)) ^ (u(IV[0]) + u(IV[4]) + w0)
    return t


def c1_of_t(o, t):
    u = np.uint32
    ror = lambda x, n: (x >> u(n)) | (x << u(32 - n))
    with np.errstate(over='ignore'):
        K0a1 = t ^ u(arr.rol(o['K0d1'], 16))
        w0 = K0a1 - u(IV[0]) - u(IV[4])
        Y2 = w0 + u(o['C2a1']) + u(o['C2b1'])
        Y14 = ror(Y2 ^ u(o['C2d1']), 8)
        Y10 = Y14 + u(o['C2c1'])
        Y6 = ror(Y10 ^ u(o['C2b1']), 7)
        a1 = Y6 + u(o['Y1']) + u(o['w12'])
        d1 = ror(a1 ^ u(o['Y12']), 16)
        c1 = d1 + u(arr.Y11A)
    return c1


def part1(nouter, rng):
    c1 = cube_all()
    ks = [12, 16, 20, 24, 26, 28, 30, 32]
    counts = {k: [] for k in ks}
    inv12 = []
    agree = 0
    for _ in range(nouter):
        o = arr.random_outer(rng)
        t = t_of_c1(o, c1)
        for k in ks:
            counts[k].append(int(np.sum(t < np.uint32(min(2 ** k, 2 ** 32 - 1)))) if k < 32 else len(t))
        ts = np.arange(1 << 12, dtype=np.uint32)
        cc = c1_of_t(o, ts)
        inv = int(np.sum((cc & np.uint32(arr.CUBE_MASK)) == np.uint32(arr.CUBE_VAL)))
        inv12.append(inv)
        agree += inv == counts[12][-1]
        # round trip on a few
        assert np.all(t_of_c1(o, c1_of_t(o, ts[:64])) == ts[:64])
    print(f'Part 1: {nouter} random outer steps; whole T1 cube (2^21 values of c1) each')
    print('  k   mean count of t < 2^k   predicted 2^(k-11)   ratio   outer steps with 0   max in one outer step')
    for k in ks:
        a = np.array(counts[k], dtype=np.float64)
        pred = 2.0 ** (k - 11) if k < 32 else 2.0 ** 21
        print(f'  {k:2d}  {a.mean():14.2f}  {pred:18.2f}  {a.mean() / pred:6.3f}  {int(np.sum(a == 0)):12d}  {int(a.max()):10d}')
    print(f'  inversion of all t < 2^12 per outer step: mean {np.mean(inv12):.2f} cube hits (pred 2.00); '
          f'equal to the forward count in {agree}/{nouter} outer steps')


def score(cost):
    return 84.96 + math.log2(cost / 6.5)


def part2():
    print('\nPart 2: time_log2 under a message-length cap (DERIVED; op counts GUESS)')
    print('  cap (bytes)          t < 2^k    F: filter cube trials   I: invert small t   best   vs filed 92.53')
    caps = [('4096 (harness default)', 4096), ('65,536 (harness max)', 65536), ('1 MiB', 2 ** 20),
            ('64 MiB', 2 ** 26), ('1 GiB', 2 ** 30), ('16 GiB', 2 ** 34), ('64 GiB', 2 ** 36),
            ('256 GiB', 2 ** 38), ('1 TiB', 2 ** 40), ('4 TiB (no cap, v13 = 0)', 2 ** 42)]
    for lab, L in caps:
        tmax = (L - 63) // 1024
        k = math.log2(tmax + 1)
        F = score(11 * 2 ** (32 - k) + 6.5) if k < 32 else 84.96
        F = min(F, 84.96 + math.log2((11 * 2 ** max(0.0, 32 - k) + 6.5) / 6.5)) if k < 32 else 84.96
        I = score((400 + 14 * 2 ** k) * 2 ** (11 - k) + 6.5)
        best = min(F, I)
        print(f'  {lab:24s} {k:7.2f}   {F:10.2f}            {I:10.2f}         {best:6.2f}   {best - 92.53:+6.2f}')
    # break-even of F against the filed path
    lo, hi = 1.0, 32.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if score(11 * 2 ** (32 - mid) + 6.5) > 92.53:
            lo = mid
        else:
            hi = mid
    print(f'  break-even with the filed 92.53 (filter F): t < 2^{hi:.2f}, messages up to about 2^{hi + 10:.1f} bytes '
          f'({2 ** (hi + 10) / 2 ** 30:.0f} GiB)')


def part3(rng):
    w = [rng.getrandbits(32) for _ in range(16)]
    n = 20000
    t0 = time.perf_counter()
    for i in range(n):
        V._compress(V.IV, w, i, 64, 0, 2)
    dt = (time.perf_counter() - t0) / n
    comps = (2 ** 31) * 16 + 2 ** 31
    print(f'\nPart 3: organizer Python _compress (2 rounds): {dt * 1e6:.1f} us per call on this machine')
    print(f'  a pair with t = 2^31 needs about {comps:.2e} compressions per message: about {comps * dt / 86400:.1f} days '
          f'per message in the reference code, and blake3() takes the whole message as one bytes object '
          f'(2^41 bytes = 2 TiB of memory)')


def main():
    nouter, seed = int(sys.argv[1]), int(sys.argv[2])
    rng = random.Random(seed)
    part1(nouter, rng)
    part2()
    part3(rng)


def part1b(nouter, k, rng):
    """Inversion count over many outer steps: all t in [1, 2^k) run backwards, cube hits counted."""
    ts = np.arange(1, 1 << k, dtype=np.uint32)
    hits = []
    for _ in range(nouter):
        o = arr.random_outer(rng)
        cc = c1_of_t(o, ts)
        hits.append(int(np.sum((cc & np.uint32(arr.CUBE_MASK)) == np.uint32(arr.CUBE_VAL))))
    h = np.array(hits, dtype=np.float64)
    pred = (2 ** k - 1) / 2 ** 11
    nz = h[h > 0]
    se = h.std() / math.sqrt(len(h))
    print(f'Part 1b: k = {k}: {nouter} outer steps, all t in [1, 2^{k}) inverted; mean cube hits per outer step '
          f'{h.mean():.4f} +- {se:.4f} (uniform prediction {pred:.4f}; ratio {h.mean() / pred:.3f}); '
          f'outer steps with a hit {len(nz)} ({len(nz) / nouter:.4f}); mean hits given a hit '
          f'{(nz.mean() if len(nz) else 0):.1f}; max {int(h.max())}')
    return h


if __name__ == '__main__':
    if len(sys.argv) > 3 and sys.argv[1] == 'inv':
        rng = random.Random(int(sys.argv[4]))
        part1b(int(sys.argv[2]), int(sys.argv[3]), rng)
    else:
        main()
