#!/usr/bin/env python3
"""make_hand_dec.py - write runs/hand_F11.dec.json and runs/hand_C31.dec.json: the hand-derived
round-0 absorption and round-1 column characteristics, in decode.py's json format, so verify.py
can sample them on the real G function.

F11 (flags 11 vs 12, dm6 = dm7 = 1): G3 of round 0 absorbs dv15 = 7; round-1 G0 gets y = 1,
round-1 G2 gets x = 1.  LM weights: r0c3 6, r1c0 2, r1c2 9.
C31 (counter t = 2^31 alone, dm0 = dm1 = 2^31): G0 of round 0 absorbs dv12 = 2^31 for free;
round-1 G2 gets y = 2^31.  LM weights: r0c0 0, r1c2 1.
"""
import json

from decode import lm

K = ('a', 'b', 'c', 'd', 'x', 'y', 'a1', 'd1', 'c1', 'b1', 'a2', 'd2', 'c2', 'b2')


def g(tag, vals, W):
    for k, v in zip(K, vals):
        W[f'{tag}.{k}'] = v


def main():
    # F11
    W = {}
    g('r0c3', (0, 0, 0, 7, 1, 1, 7, 0, 0, 0, 0, 0, 0, 0), W)
    g('r1c0', (0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0x01000000, 0x01000000, 0x00020000), W)
    g('r1c2', (0, 0, 0, 0, 1, 0, 1, 0x00010000, 0x00010000, 0x00000010, 0x00000011,
               0x11000100, 0x11010100, 0x20220202), W)
    per_g = {
        'r0c3': lm(0, 1, 7) + lm(7, 1, 0),                       # (K+m6), (a1+m7)+b1
        'r1c0': lm(0, 1, 1) + lm(0, 0x01000000, 0x01000000),
        'r1c2': lm(0, 1, 1) + lm(0, 0x10000, 0x10000) + lm(1, 0, 1) + lm(1, 0x10, 0x11)
                + lm(0x10000, 0x11000100, 0x11010100),
    }
    json.dump({'total': sum(per_g.values()), 'per_g': per_g, 'words': W, 'dm': []},
              open('runs/hand_F11.dec.json', 'w'))
    print('F11 hand weights', per_g, 'sum', sum(per_g.values()))
    # C31
    W = {}
    T = 0x80000000
    g('r0c0', (0, 0, 0, T, T, T, T, 0, 0, 0, 0, 0, 0, 0), W)
    g('r1c2', (0, 0, 0, 0, 0, T, 0, 0, 0, 0, T, 0x00800000, 0x00800000, 0x00010000), W)
    per_g = {'r0c0': lm(0, T, T) + lm(T, T, 0), 'r1c2': lm(0, T, T) + lm(0, 0x00800000, 0x00800000)}
    per_g = {k: (v if v else 0) for k, v in per_g.items()}
    json.dump({'total': sum(per_g.values()), 'per_g': per_g, 'words': W, 'dm': []},
              open('runs/hand_C31.dec.json', 'w'))
    print('C31 hand weights', per_g)
    # CF31: counter t = 2^31 with flags 3 vs 4; dm0 = dm1 = 2^31, dm6 = dm7 = 1
    W = {}
    g('r0c0', (0, 0, 0, T, T, T, T, 0, 0, 0, 0, 0, 0, 0), W)
    g('r0c3', (0, 0, 0, 7, 1, 1, 7, 0, 0, 0, 0, 0, 0, 0), W)
    g('r1c0', (0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0x01000000, 0x01000000, 0x00020000), W)
    g('r1c2', (0, 0, 0, 0, 1, T, 1, 0x00010000, 0x00010000, 0x00000010, 0x80000011,
               0x11800100, 0x11810100, 0x20230202), W)
    per_g = {
        'r0c0': lm(0, T, T) + lm(T, T, 0),
        'r0c3': lm(0, 1, 7) + lm(7, 1, 0),
        'r1c0': lm(0, 1, 1) + lm(0, 0x01000000, 0x01000000),
        'r1c2': lm(0, 1, 1) + lm(0, 0x10000, 0x10000) + lm(1, T, 0x80000001)
                + lm(0x80000001, 0x10, 0x80000011) + lm(0x10000, 0x11800100, 0x11810100),
    }
    json.dump({'total': sum(per_g.values()), 'per_g': per_g, 'words': W, 'dm': []},
              open('runs/hand_CF31.dec.json', 'w'))
    print('CF31 hand weights', per_g, 'sum', sum(per_g.values()))


if __name__ == '__main__':
    main()
