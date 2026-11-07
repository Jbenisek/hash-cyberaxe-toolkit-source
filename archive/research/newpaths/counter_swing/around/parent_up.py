"""parent_up.py - collisions placed at a parent node (item 3): two different child-CV pairs, same parent output.
A parent has cv = IV, counter 0, length 64, flags 4 on both sides, so the only difference is in its message.
Cases: (a) the right child half-collides (its CV words 0,2,5,7 equal, 1,3,4,6 differ: the 55/63 output moved up
one level): parent message words 9, 11, 12, 14 differ; (b) one random right-child word differs (m8);
(c) two words of the left child differ (m2, m3, the pair a column could absorb if there were a d difference).
Prints at w = 32 and w = 8: fraction with the round-0 state equal, mean number of state words that differ after
round 0, and the digest-half equality counts.  Lemma G2 (a G call with equal input state is injective in
(x, y)) predicts round 0 never cancels.
Run: python -B parent_up.py
"""
import numpy as np

from tb3 import Toy

CASES = [('right child half-collides: m9 m11 m12 m14', (9, 11, 12, 14)),
         ('one word of right child: m8', (8,)),
         ('two words of left child: m2 m3', (2, 3))]


def run(w, n, batches, rng):
    toy = Toy(w)
    for name, words in CASES:
        N = r0 = hA = hB = 0
        nd = 0
        for _ in range(batches):
            m = [rng.integers(0, 1 << w, size=n, dtype=np.uint64).astype(np.uint32) for _ in range(16)]
            mo = [x.copy() for x in m]
            for i in words:
                mo[i] = m[i] ^ rng.integers(1, 1 << w, size=n, dtype=np.uint64).astype(np.uint32)
            v = toy.init_state(n, blen=64, flags=4)
            rb, ro = toy.compress(v, m), toy.compress(v, mo)
            dX = np.zeros(n, dtype=np.int64)
            for i in range(16):
                dX += (rb['X'][i] != ro['X'][i])
            r0 += int((dX == 0).sum())
            nd += int(dX.sum())
            ob_, oo = rb['out'], ro['out']
            hA += int(((ob_[0] == oo[0]) & (ob_[2] == oo[2]) & (ob_[5] == oo[5]) & (ob_[7] == oo[7])).sum())
            hB += int(((ob_[1] == oo[1]) & (ob_[3] == oo[3]) & (ob_[4] == oo[4]) & (ob_[6] == oo[6])).sum())
            N += n
        print('w=%2d %-44s N=%d round-0 equal %d | mean words differing after round 0 %.2f | hA %d hB %d'
              % (w, name, N, r0, nd / N, hA, hB))


if __name__ == '__main__':
    rng = np.random.default_rng(99)
    run(32, 1 << 17, 2, rng)
    run(8, 1 << 20, 8, rng)
