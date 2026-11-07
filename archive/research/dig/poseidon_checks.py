#!/usr/bin/env python3
"""poseidon_checks.py - exact integer checks used by the Poseidon grid records (2026-10-12). Pure Python, no inputs.
Reproduces: exponent popcounts, divisibility of p-1, dimensions n, NTT lengths, buffer words of the P3.4/P3.7 powering schedule,
the 3*2^a length lever, the evaluation-based build sizes, and the six-term Bonferroni lower bound for the odd-part method."""
from fractions import Fraction
from math import comb, gcd, log2
p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
pm1 = p - 1
def v2(x):
    k = 0
    while x % 2 == 0:
        x //= 2; k += 1
    return k
print('p mod 5 =', p % 5, ' gcd(5,p-1) =', gcd(5, pm1), ' v2(p-1) =', v2(pm1), ' (p-1) mod 3 =', pm1 % 3, ' (p-1) mod 5 =', pm1 % 5)
e5 = (4 * pm1 + 1) // 5
assert (5 * e5) % pm1 == 1
print('e5 = 5^-1 mod (p-1): bits', e5.bit_length(), 'popcount', bin(e5).count('1'))
e = pm1 // 2
print('(p-1)/2: bits', e.bit_length(), 'popcount', bin(e).count('1'), ' p-2: bits', (p - 2).bit_length(), 'popcount', bin(p - 2).count('1'))
C = lambda r: 216 + 21 * r
for r in (1, 2):
    D = 5 ** (6 + r); n = (D - 1) // 2
    need = 2 * n - 1
    L2 = 1 << (need - 1).bit_length()
    a = 0
    while 3 * (1 << a) < need: a += 1
    L3 = 3 * (1 << a)
    words2 = 4 * n + 5 * L2; words3 = 4 * n + 5 * L3
    print('r=%d D=%d n=%d C=%d  product length 2n-1=%d  L2=%d L3=3*2^%d=%d (ratio %.4f)' % (r, D, n, C(r), need, L2, a, L3, L3 / L2))
    print('   pow-phase words 4n+5L: L2 -> %d (%d B)  L3 -> %d (%d B)  memory ratio %.4f = %.4f bits' % (words2, words2 * 32, words3, words3 * 32, words3 / words2, log2(words2 / words3)))
    H = 1
    while H < n + 1: H *= 2
    H3 = 3 * (1 << 0)
    while H3 < n + 1: H3 *= 2
    print('   evaluation-based build: H >= n+1=%d -> H=%d (2^) or %d (3*2^a); evaluations 2H=%d or %d; inverse-NTT array %d B or %d B; 2H divides p-1: %s %s'
          % (n + 1, H, H3, 2 * H, 2 * H3, H * 32, H3 * 32, pm1 % (2 * H) == 0, pm1 % (2 * H3) == 0))
    for peak, name in ((34083264 if r == 1 else 157832000, 'Luna3 composition peak'), (4 * n * 32 + 5 * L2 * 32, 'pow-phase 4n+5L')):
        print('   %s = %d B  (log2 %.4f, penalty %.4f)' % (name, peak, log2(peak), max(0, log2(peak) - 20)))
    pk = 34083264 if r == 1 else 157832000
    print('   gain if the peak falls from the composition peak to the pow-phase peak: %.4f bits' % log2(pk / (words2 * 32)))
# six-term Bonferroni lower bound for P[K>=1], K = number of roots among a = (p-1)/2 candidate squares, factorial moments C(a,k)/p^k
a = (p - 1) // 2
s = Fraction(0)
for k in range(1, 7):
    s += (-1) ** (k + 1) * Fraction(comb(a, k), p ** k)
print('six-term Bonferroni lower bound (odd part, a=(p-1)/2): %.12f  margin over 0.39: %.6f' % (float(s), float(s) - 0.39))
a = p - 1
s = Fraction(0)
for k in range(1, 7):
    s += (-1) ** (k + 1) * Fraction(comb(a, k), p ** k)
print('six-term Bonferroni lower bound (fixed value, a=p-1): %.12f' % float(s))
print('Poisson: 1-exp(-1/2) = %.12f  1-exp(-1) = %.12f' % (1 - 2.718281828459045 ** -0.5, 1 - 2.718281828459045 ** -1))
