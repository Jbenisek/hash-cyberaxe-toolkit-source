"""constraint_check.py: item (1), the zero fill and the forced zero words as constraints.

Part 1 (real 32-bit trials of the counter arrangement, organizer copy as referee):
  1a baseline: CV words 0,2,5,7 equal for the legal pair (B's bytes 55..62 are explicit zeros);
  1b B's tail bytes 55..62 set to nonzero values (the only bytes where B may differ from A's zero fill without
     changing the length): does the free half survive? where does the difference first appear?
Part 2 (word model, copy of counter\\structure\\model.py with the zero-fill words switchable):
  what the forced zeros cost in prescriptions: bases for {Y4, E1.d1, T} with w14 and/or w15 free (t free).
  (w15 is never free in any legal pair: the shorter block is at most 63 bytes. This is a measurement of the
  constraint's price, not a proposal.)
usage: python -B constraint_check.py N SEED
"""
import random
import struct
import sys

sys.dont_write_bytecode = True
import arr
import b3own_copy as O
import model_copy as MC


def part1(N, rng):
    base_half = 0
    tail_half = 0
    tail_r0_equal = 0
    first_diff = {}
    tail_cases = 0
    for _ in range(N):
        o, ii, w, wb, t, A, B = arr.trial(rng)
        cA, _ = arr.cv_last(A, t); cB, _ = arr.cv_last(B, t)
        base_half += all(cA[i] == cB[i] for i in (0, 2, 5, 7))
        # 1b: nonzero tail in B (bytes 55..62); choose 1 random byte or all 8 random
        for mode in ('one', 'all'):
            Bt = bytearray(B)
            if mode == 'one':
                k = rng.randrange(55, 63); Bt[k] = rng.randrange(1, 256)
            else:
                for k in range(55, 63):
                    Bt[k] = rng.randrange(256)
                if Bt[55:63] == bytes(8):
                    Bt[55] = 1
            Bt = bytes(Bt)
            cBt, _ = arr.cv_last(Bt, t)
            tail_cases += 1
            tail_half += all(cA[i] == cBt[i] for i in (0, 2, 5, 7))
            wbt = list(struct.unpack('<16I', Bt.ljust(64, b'\0')))
            _, stA = O.compress_full(O.IV, w, t, 55, 3)
            _, stB = O.compress_full(O.IV, wbt, t, 63, 3)
            tail_r0_equal += stA['S'] == stB['S']
            nX = sum(1 for i in range(16) if stA['X'][i] != stB['X'][i])
            first_diff[nX] = first_diff.get(nX, 0) + 1
    print(f'Part 1 ({N} real trials of the counter arrangement; organizer _chunk_output/_compress, 2 rounds)')
    print(f'  1a legal pair (B bytes 55..62 = 0): CV words 0,2,5,7 equal {base_half}/{N}')
    print(f'  1b B bytes 55..62 nonzero (one byte, or all eight): CV words 0,2,5,7 equal {tail_half}/{tail_cases}')
    print(f'     round-0 column state S equal for A and B: {tail_r0_equal}/{tail_cases} '
          f'(the tail words w13..w15 first enter round 0 at the diagonals D2, D3)')
    print(f'     number of differing words of the round-0 output X (16 words): '
          + ', '.join(f'{k} words: {v}' for k, v in sorted(first_diff.items())))


def system_ext(counter, w14free, w15free):
    eqs, words = MC.system(counter, w14free)
    if not w15free:
        return eqs, words
    # rebuild with w15 not a constant: same equations as model.system, w15 removed from the constant set
    T0 = 'T0' if counter >= 1 else 'c0'
    T1 = 'T1' if counter >= 2 else 'c0'
    R = []
    g = MC.gcall
    R += g('K0', 'IV0', 'IV4', 'IV0', T0, 'w0', 'w1', 'S0', 'S4', 'S8', 'S12')
    R += g('K1', 'IV1', 'IV5', 'IV1', T1, 'w2', 'w3', 'S1', 'S5', 'S9', 'S13')
    R += g('K2', 'IV2', 'IV6', 'IV2', 'len', 'w4', 'w5', 'S2', 'S6', 'S10', 'S14')
    R += g('K3', 'IV3', 'IV7', 'IV3', 'flags', 'w6', 'w7', 'S3', 'S7', 'S11', 'S15')
    R += g('D0', 'S0', 'S5', 'S10', 'S15', 'w8', 'w9', 'X0', 'X5', 'X10', 'X15')
    R += g('D1', 'S1', 'S6', 'S11', 'S12', 'w10', 'w11', 'X1', 'X6', 'X11', 'X12')
    R += g('D2', 'S2', 'S7', 'S8', 'S13', 'w12', 'w13', 'X2', 'X7', 'X8', 'X13')
    R += g('D3', 'S3', 'S4', 'S9', 'S14', 'w14', 'w15', 'X3', 'X4', 'X9', 'X14')
    R += g('C0', 'X0', 'X4', 'X8', 'X12', 'w2', 'w6', 'Y0', 'Y4', 'Y8', 'Y12')
    R += g('C1', 'X1', 'X5', 'X9', 'X13', 'w3', 'w10', 'Y1', 'Y5', 'Y9', 'Y13')
    R += g('C2', 'X2', 'X6', 'X10', 'X14', 'w7', 'w0', 'Y2', 'Y6', 'Y10', 'Y14')
    R += [('E1.a1', ('Y1', 'Y6', 'w12')), ('E1.d1', ('Y12', 'E1.a1')),
          ('E1.b1', ('Y6', 'E1.d1', 'Y11')), ('E1.a2', ('E1.a1', 'E1.b1', 'w5')),
          ('E3.h1', ('Y14', 'Y3', 'Y4', 'w15')), ('E3.g1', ('Y9', 'E3.h1')),
          ('E3.f1', ('Y4', 'E3.g1')), ('E3.e2', ('Y3', 'Y4', 'w15', 'E3.f1', 'w8'))]
    const = set(MC.IVN) | {'c0', 'len', 'flags', 'X3', 'X7', 'X11', 'X15', 'w4', 'w13', 'Y3', 'Y11'}
    if not w14free:
        const.add('w14')
    const |= {'K2.a1', 'K2.d1', 'K2.c1', 'K2.b1'}
    eqs = []
    for lhs, args in R:
        ws = frozenset([lhs, *args]) - const
        if not ws:
            continue
        eqs.append((lhs, ws))
    words = set().union(*[w for _, w in eqs])
    return eqs, words


def part2():
    print('\nPart 2 (word model; reverse peeling, validated against brute force in counter\\structure)')
    qs = [('Y4', 'E1.d1'), ('Y4', 'E1.d1', 'E3.h1'), ('Y4', 'E1.d1', 'E3.g1'), ('Y4', 'E1.d1', 'E3.f1'),
          ('Y4', 'E1.d1', 'E3.e2'), ('Y4', 'E1.d1', 'Y14'), ('Y4', 'E1.d1', 'E1.b1'), ('Y4', 'E1.d1', 'Y9'),
          ('Y4', 'E1.d1', 'w8'), ('Y4', 'E3.h1'), ('Y4', 'E1.b1')]
    for counter in (0, 1):
        for w14f, w15f in ((False, False), (True, False), (False, True), (True, True)):
            eqs, words = system_ext(counter, w14f, w15f)
            nb = len(words) - len(eqs)
            res = []
            for q in qs:
                if all(x in words for x in q):
                    res.append('+'.join(q) + ':' + ('YES' if MC.peel(eqs, set(q))[0] else 'no'))
            lab = f"counter {'t free' if counter else 'fixed'}, w14 {'free' if w14f else '0'}, w15 {'free' if w15f else '0'}"
            print(f'  [{lab}] basis {nb}: ' + '  '.join(res))


def main():
    N, seed = int(sys.argv[1]), int(sys.argv[2])
    rng = random.Random(seed)
    part1(N, rng)
    part2()


if __name__ == '__main__':
    main()
