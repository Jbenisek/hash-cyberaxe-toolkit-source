"""tree_align.py - where can ONE colliding compression sit in a full collision of two messages with different
chunk counts?  Own code; the organizer's verifier (copied as org_blake3.py) is the referee.

Part 1  own recursive tree (largest power-of-two left subtree) == organizer blake3(), rounds 2, n = 1..40 chunks.
Part 2  enumerate, for chunk counts n1, n2 <= N, every node pair (u1 in tree 1, u2 in tree 2) such that ONE
        compression collision at (u1, u2), with every other aligned subtree identical, gives equal digests.
        Classify each: leaf-leaf same index / leaf-leaf DIFFERENT index (a pure counter difference) /
        leaf-parent / parent-parent; root or not; leaf = last chunk (can be one block, cv = IV) or a full chunk.
Part 3  planted leaf-vs-parent collisions on the organizer verifier: M1 = P||X (t chunks + 64-byte X),
        M2 = P||(q chunks); the organizer's _compress is patched so that ONLY the last-chunk call of M1 returns the
        output of M2's parent node over the q chunks. Digests must be equal iff q <= lowbit(t).
Run: python -B tree_align.py [N]
"""
import os
import random
import struct
import sys

import org_blake3 as ob

R = 2


def shape(lo, hi):
    n = hi - lo
    if n == 1:
        return ('L', lo)
    left = 1 << ((n - 1).bit_length() - 1)      # largest power of two strictly below n
    return ('P', shape(lo, lo + left), shape(lo + left, hi))


def own_cv(data, node, n, root):
    if node[0] == 'L':
        i = node[1]
        out = ob._chunk_output(data[i * 1024:(i + 1) * 1024], i, R)
    else:
        out = ob._parent_output(own_cv(data, node[1], n, False), own_cv(data, node[2], n, False))
    cv, words, ctr, blen, flags = out
    if root:
        return ob._compress(cv, words, 0, blen, flags | ob.ROOT, R)[:8]
    return ob._compress(cv, words, ctr, blen, flags, R)[:8]


def own_digest(data):
    n = max(1, (len(data) + 1023) // 1024)
    return struct.pack('<8I', *own_cv(data, shape(0, n), n, True))


def part1(rnd):
    bad = 0
    cases = 0
    for n in range(1, 41):
        for last in (1, 55, 63, 64, 65, 700, 1024):
            data = bytes(rnd.getrandbits(8) for _ in range((n - 1) * 1024 + last))
            cases += 1
            bad += own_digest(data) != ob.blake3(data, R)
    return cases, bad


def ident(u, v):
    return u == v


def singles(u1, u2, out):
    out.append((u1, u2))
    if u1[0] == 'P' and u2[0] == 'P':
        if ident(u1[2], u2[2]):
            singles(u1[1], u2[1], out)
        if ident(u1[1], u2[1]):
            singles(u1[2], u2[2], out)


def classify(u1, u2, n1, n2, is_root):
    def kind(u, n):
        if u[0] == 'L':
            return 'leafLast' if u[1] == n - 1 else 'leafFull'
        return 'parent'
    k1, k2 = kind(u1, n1), kind(u2, n2)
    if u1[0] == 'L' and u2[0] == 'L':
        t = 'leaf-leaf same index' if u1[1] == u2[1] else 'leaf-leaf DIFFERENT index'
    elif u1[0] == 'P' and u2[0] == 'P':
        t = 'parent-parent'
    else:
        t = 'leaf-parent'
    return t, k1, k2, is_root


def size(u):
    return 1 if u[0] == 'L' else size(u[1]) + size(u[2])


def lowbit(t):
    return t & -t


def part2(N):
    from collections import Counter
    types = Counter()
    lp = []          # leaf-parent placements with details
    llx = 0
    for n1 in range(1, N + 1):
        T1 = shape(0, n1)
        for n2 in range(1, N + 1):
            if n2 == n1:
                continue
            T2 = shape(0, n2)
            out = []
            singles(T1, T2, out)
            for (u1, u2) in out:
                is_root = (u1 is T1)
                t, k1, k2, r = classify(u1, u2, n1, n2, is_root)
                types[(t, k1, k2, 'root' if r else 'nonroot')] += 1
                if t == 'leaf-leaf DIFFERENT index':
                    llx += 1
                if t == 'leaf-parent' and u1[0] == 'L' and n1 < n2:
                    lp.append((n1, n2, u1[1], k1, size(u2), r))
    return types, lp, llx


def part3(rnd):
    lines = []
    ok = 0
    tot = 0
    for t in (1, 2, 3, 4, 5, 6, 8, 12, 16, 24, 32, 48, 64):
        for q in (2, 3, 4, 5, 8):
            if q > 2 * max(1, lowbit(t)) and q not in (2, 3):
                continue
            P = bytes(rnd.getrandbits(8) for _ in range(t * 1024))
            X = bytes(rnd.getrandbits(8) for _ in range(64))
            tail_last = rnd.randint(1, 1024)
            Q = bytes(rnd.getrandbits(8) for _ in range((q - 1) * 1024 + tail_last))
            M1, M2 = P + X, P + Q
            # M2's subtree over chunks t..t+q-1, as a non-root node: its CV (a parent compression for q >= 2)
            nodeQ = shape(t, t + q)
            # its parent compression output (16 words), computed with organizer functions
            left = own_cv(M2, nodeQ[1], t + q, False)
            right = own_cv(M2, nodeQ[2], t + q, False)
            target = ob._compress(*ob._parent_output(left, right), R)
            xw = struct.unpack('<16I', X)
            orig = ob._compress

            def patched(cv, words, counter, block_len, flags, rounds, _o=orig):
                if tuple(words) == xw and counter == t and block_len == 64 and flags == 3:
                    return target
                return _o(cv, words, counter, block_len, flags, rounds)
            ob._compress = patched
            try:
                d1 = ob.blake3(M1, R)
            finally:
                ob._compress = orig
            d2 = ob.blake3(M2, R)
            pred = q <= max(1, lowbit(t)) if t >= 1 else False
            got = (d1 == d2)
            tot += 1
            ok += (got == pred)
            lines.append('t=%3d q=%d lowbit(t)=%2d  predicted equal=%-5s  organizer digests equal=%-5s  %s'
                         % (t, q, lowbit(t), pred, got, 'ok' if got == pred else 'MISMATCH'))
    return tot, ok, lines


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 128
    rnd = random.Random(20261008)
    cases, bad = part1(rnd)
    print('PART 1  own recursive tree == organizer blake3 (rounds 2): %d cases, %d mismatches' % (cases, bad))
    types, lp, llx = part2(N)
    print('\nPART 2  single-collision placements, n1 != n2 <= %d (ordered pairs; counts of placements)' % N)
    for k in sorted(types):
        print('  %-26s tree1 node %-8s tree2 node %-8s %-7s : %d' % (k[0], k[1], k[2], k[3], types[k]))
    print('  placements that are a pure counter difference (leaf-leaf, different index): %d' % llx)
    one_block = [x for x in lp if x[3] == 'leafLast']
    print('  leaf-parent with tree-1 leaf = LAST chunk (can be a single block, cv = IV): %d' % len(one_block))
    rule_ok = all(x[1] == x[0] - 1 + x[4] and (x[4] <= max(1, lowbit(x[0] - 1)) or x[0] == 1) for x in one_block)
    print('  every such case has n2 = t + q with t = n1 - 1 and 2 <= q <= lowbit(t) (or t = 0, the root): %s' % rule_ok)
    print('  first cases (n1, n2, leaf index t, q, leaf is root):',
          [(a, b, c, e, f) for (a, b, c, d, e, f) in one_block[:14]])
    full = [x for x in lp if x[3] == 'leafFull']
    print('  leaf-parent with tree-1 leaf = a FULL chunk (16 blocks, chained cv): %d' % len(full))
    tot, ok, lines = part3(rnd)
    print('\nPART 3  planted leaf-vs-parent on the organizer verifier: %d cases, %d as predicted' % (tot, ok))
    for s in lines:
        print('  ' + s)


if __name__ == '__main__':
    main()
