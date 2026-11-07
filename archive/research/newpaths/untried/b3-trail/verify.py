#!/usr/bin/env python3
"""verify.py - sample a decoded characteristic (runs/NAME.dec.json) on the real G function.

For every active G call, draw N random value tuples with the characteristic's input XOR
differences, run G (blake3.py semantics) on both sides and count how often all eight
intermediate differences (a1 d1 c1 b1 a2 d2 c2 b2) follow the characteristic.
Round-0 column calls use the real state constants (IV, counter, block length, flags) on
both sides and random message words only.  Prints measured log2 P next to the LM weight.

usage: verify.py NAME [--n LOG2N] [--ctr T] [--flags F0,F1]
"""
import argparse
import json
import math

import numpy as np

IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
      0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)


def ror(x, r):
    return (x >> np.uint32(r)) | (x << np.uint32(32 - r))


def G(a, b, c, d, x, y):
    a = a + b + x
    d = ror(d ^ a, 16)
    c = c + d
    b = ror(b ^ c, 12)
    a1, d1, c1, b1 = a, d, c, b
    a = a + b + y
    d = ror(d ^ a, 8)
    c = c + d
    b = ror(b ^ c, 7)
    return a1, d1, c1, b1, a, d, c, b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('name')
    ap.add_argument('--n', type=int, default=22)
    ap.add_argument('--ctr', type=lambda s: int(s, 0), default=0, help='chunk-side counter (parent side 0)')
    ap.add_argument('--flags', default='11,12', help='chunk-side,parent-side flags')
    args = ap.parse_args()
    dec = json.load(open(f'runs/{args.name}.dec.json'))
    W = dec['words']
    per_g = dec['per_g']
    f0, f1 = (int(t) for t in args.flags.split(','))
    # real round-0 input state, chunk side (s0) and parent side (s1)
    s0 = list(IV) + list(IV[:4]) + [args.ctr & 0xFFFFFFFF, args.ctr >> 32, 64, f0]
    s1 = list(IV) + list(IV[:4]) + [0, 0, 64, f1]
    rng = np.random.default_rng(20261010)
    N = 1 << args.n
    tags = [t for t in per_g if per_g[t] > 0 or t.startswith('r0')]
    idx = {'c0': (0, 4, 8, 12), 'c1': (1, 5, 9, 13), 'c2': (2, 6, 10, 14), 'c3': (3, 7, 11, 15)}
    print(f'samples per call: 2^{args.n}')
    for t in sorted(tags):
        din = [W[f'{t}.{k}'] for k in 'abcdxy']
        want = [W[f'{t}.{k}'] for k in ('a1', 'd1', 'c1', 'b1', 'a2', 'd2', 'c2', 'b2')]
        if t.startswith('r0c'):
            ii = idx[t[2:]]
            P = [np.full(N, s1[i], dtype=np.uint32) for i in ii]
            Q = [np.full(N, s0[i], dtype=np.uint32) for i in ii]
            # sanity: constants must carry exactly the modelled differences
            for k in range(4):
                assert (s0[ii[k]] ^ s1[ii[k]]) == din[k], (t, k)
        else:
            P = [rng.integers(0, 1 << 32, N, dtype=np.uint32) for _ in range(4)]
            Q = [p ^ np.uint32(dd) for p, dd in zip(P, din[:4])]
        xs = rng.integers(0, 1 << 32, N, dtype=np.uint32)
        ys = rng.integers(0, 1 << 32, N, dtype=np.uint32)
        o1 = G(*P, xs, ys)
        o2 = G(*Q, xs ^ np.uint32(din[4]), ys ^ np.uint32(din[5]))
        ok = np.ones(N, dtype=bool)
        for u, v, w in zip(o1, o2, want):
            ok &= (u ^ v) == np.uint32(w)
        hits = int(ok.sum())
        meas = (math.log2(hits / N) if hits else float('-inf'))
        print(f'  {t}: LM weight {per_g[t]:3d}   measured log2 P = {meas:7.2f}  ({hits} hits)')


if __name__ == '__main__':
    main()
