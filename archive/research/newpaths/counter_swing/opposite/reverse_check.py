"""reverse_check.py: item (4), freedom in the PREFIX chunks or on the ROOT side instead of the last chunk.

Part 1: the last chunk's compression does not read the prefix content: for real arrangement blocks A, the
  organizer's last-chunk descriptor (cv, words, counter, length, flags), built exactly as blake3() line 82
  builds it, is the same for P1||A and P2||A, for random different prefixes of 1..3 chunks.
Part 2: the root parent of a two-chunk message, root(L, R) = compress(IV, L || R, 0, 64, PARENT | ROOT), with
  R = CV of a half-colliding pair (words 0,2,5,7 equal, words 1,3,4,6 different) and L = CV of chunk 0 for
  random prefix contents. Counts: differing words of the parent's state after round-0 columns, after round 0,
  after round-1 columns; equal digest words. Also a non-root parent (flags 4) one level up.
Part 3: the single-message-word lemma used in the text: a G call whose four state inputs are equal for the two
  messages and exactly one message word differs always has a differing output (exhaustive at W = 8 for one
  differing word in x or y; real 32-bit random samples).
usage: python -B reverse_check.py N SEED
"""
import random
import struct
import sys

sys.dont_write_bytecode = True
import arr
import b3own_copy as O
import blake3_ref as V

M = 0xFFFFFFFF


def part1(N, rng):
    same = half = 0
    for _ in range(N):
        o, ii, w, wb, t, A, B = arr.trial(rng)
        P1 = bytes(rng.getrandbits(8) for _ in range(1024 * (t % 3 + 1)))
        P2 = bytes(rng.getrandbits(8) for _ in range(1024 * (t % 3 + 1)))
        # the organizer's last chunk output descriptor of P||A: the counter is the number of prefix chunks
        d1 = V._chunk_output((P1 + A)[1024 * (len(P1) // 1024):], len(P1) // 1024, 2)
        d2 = V._chunk_output((P2 + A)[1024 * (len(P2) // 1024):], len(P2) // 1024, 2)
        same += d1 == d2
    print(f'Part 1: organizer last-chunk descriptor (cv, words, counter, len, flags) of P1||A equals that of '
          f'P2||A for random different prefixes of equal length: {same}/{N}')


def state_after(cv, words, counter, blen, flags, nsteps):
    v = list(cv) + list(V.IV[:4]) + [counter & M, counter >> 32, blen, flags]
    m = list(words)
    calls = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
             (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
    step = 0
    for r in range(2):
        for half in range(2):
            if step == nsteps:
                return v
            for i in range(4):
                a, b, c, d = calls[4 * half + i]
                V._g(v, a, b, c, d, m[8 * half + 2 * i], m[8 * half + 2 * i + 1])
            step += 1
        m = [m[i] for i in V.PERMUTATION]
    return v


def part2(N, rng):
    hist = {1: {}, 2: {}, 3: {}}
    eq_words = [0] * 8
    eq_any = 0
    eq_parent = [0] * 8
    for _ in range(N):
        o, ii, w, wb, t, A, B = arr.trial(rng)
        RA, _ = arr.cv_last(A, t); RB, _ = arr.cv_last(B, t)
        assert all(RA[i] == RB[i] for i in (0, 2, 5, 7))
        L = tuple(V._compress(*V._chunk_output(bytes(rng.getrandbits(8) for _ in range(1024)), 0, 2), 2)[:8])
        mA, mB = L + RA, L + RB
        for ns in (1, 2, 3):
            sa = state_after(V.IV, mA, 0, 64, V.PARENT | V.ROOT, ns)
            sb = state_after(V.IV, mB, 0, 64, V.PARENT | V.ROOT, ns)
            k = sum(1 for i in range(16) if sa[i] != sb[i])
            hist[ns][k] = hist[ns].get(k, 0) + 1
        dA = V._compress(V.IV, mA, 0, 64, V.PARENT | V.ROOT, 2)[:8]
        dB = V._compress(V.IV, mB, 0, 64, V.PARENT | V.ROOT, 2)[:8]
        for i in range(8):
            eq_words[i] += dA[i] == dB[i]
        eq_any += any(dA[i] == dB[i] for i in range(8))
        pA = V._compress(V.IV, mA, 0, 64, V.PARENT, 2)[:8]
        pB = V._compress(V.IV, mB, 0, 64, V.PARENT, 2)[:8]
        for i in range(8):
            eq_parent[i] += pA[i] == pB[i]
    print(f'\nPart 2 ({N} real half-colliding last-chunk CV pairs as the right child; random chunk-0 CVs as the left)')
    print('  message difference sits in parent words m9, m11, m12, m14 (right CV words 1, 3, 4, 6)')
    for ns, lab in ((1, 'after round-0 columns'), (2, 'after round 0'), (3, 'after round-1 columns')):
        print(f'  differing state words {lab}: ' + ', '.join(f'{k}: {v}' for k, v in sorted(hist[ns].items())))
    print(f'  root digest words equal (per word, of {N}): {eq_words}; any digest word equal: {eq_any}/{N} '
          f'(random: about {8 * N / 2**32:.1e})')
    print(f'  non-root parent CV words equal (per word): {eq_parent}')


def part3(N, rng):
    # exhaustive at W = 8: for every state (a,b,c,d) sample and every x != x', y: outputs differ
    W, Mk = 8, 0xFF
    R = (4, 3, 2, 1)
    ror8 = lambda x, n: ((x >> n) | (x << (W - n))) & Mk

    def g8(a, b, c, d, x, y):
        a = (a + b + x) & Mk; d = ror8(d ^ a, R[0]); c = (c + d) & Mk; b = ror8(b ^ c, R[1])
        a = (a + b + y) & Mk; d = ror8(d ^ a, R[2]); c = (c + d) & Mk; b = ror8(b ^ c, R[3])
        return a, b, c, d
    bad = 0
    cases = 0
    for _ in range(200):
        a, b, c, d, y = (rng.randrange(256) for _ in range(5))
        outs = {g8(a, b, c, d, x, y) for x in range(256)}
        bad += len(outs) != 256; cases += 1
        x = rng.randrange(256)
        outs = {g8(a, b, c, d, x, yy) for yy in range(256)}
        bad += len(outs) != 256; cases += 1
    # 32-bit samples
    bad32 = 0
    for _ in range(N):
        a, b, c, d, x, y = (rng.getrandbits(32) for _ in range(6))
        x2 = rng.getrandbits(32) or 1
        y2 = rng.getrandbits(32) or 1
        g = lambda xx, yy: O.G(a, b, c, d, xx, yy)
        bad32 += g(x, y) == g(x ^ x2, y)
        bad32 += g(x, y) == g(x, y ^ y2)
    print(f'\nPart 3: G with equal state and one differing message word: W=8 exhaustive over x (or y) for 200 random '
          f'states each: {cases - bad}/{cases} injective; W=32 random: equal outputs {bad32} of {2 * N}')


def main():
    N, seed = int(sys.argv[1]), int(sys.argv[2])
    rng = random.Random(seed)
    part1(min(N, 200), rng)
    part2(N, rng)
    part3(N, rng)


if __name__ == '__main__':
    main()
