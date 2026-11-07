import re, sys, random
from poseidon_own import *

# ---- parse PUBLIC upstream test vectors (fp = Pallas base) from upstream/test_vectors.rs
src = open('upstream/test_vectors.rs').read()
fp_src = src[src.index('pub mod fp'):src.index('pub mod fq')]
i_hash = fp_src.index('pub fn hash')
perm_src, hash_src = fp_src[:i_hash], fp_src[i_hash:]

def arrays(s):
    nums = [int(x, 16) for x in re.findall(r'0x([0-9a-fA-F]{2})\b', s)]
    assert len(nums) % 32 == 0
    return [int.from_bytes(bytes(nums[i:i + 32]), 'little') for i in range(0, len(nums), 32)]

pa = arrays(perm_src); ha = arrays(hash_src)
assert len(pa) == 66 and len(ha) == 33, (len(pa), len(ha))
ok_p = ok_h = 0
for v in range(11):
    ini = pa[6 * v:6 * v + 3]; fin = pa[6 * v + 3:6 * v + 6]
    assert all(x < P for x in ini + fin)
    ok_p += (perm(ini, 64) == fin)
    m0, m1, d = ha[3 * v:3 * v + 3]
    ok_h += (hash_prefix(m0, m1, 64) == d) and (
        hash_prefix_bytes(m0.to_bytes(32, 'little') + m1.to_bytes(32, 'little'), 64) == d.to_bytes(32, 'little'))
print(f'permutation vectors {ok_p}/11, hash vectors {ok_h}/11')
assert ok_p == 11 and ok_h == 11
print('hash vector 0: in=(%d,%d) out=0x%064x' % (ha[0], ha[1], ha[2]))
print('hash vector 0 out (LE bytes) =', ha[2].to_bytes(32, 'little').hex())

# negative control: wrong capacity must break the vector
import poseidon_own as po
assert perm([ha[0], ha[1], 3 << 64], 64)[0] != ha[2]
assert perm([ha[0], ha[1], CAPACITY], 63)[0] != ha[2]
print('negative controls (capacity 3<<64, 63 rounds) differ: ok')

# ---- counters: instrumented == analytic; optimized path == faithful digest
random.seed(1)
for r in (1, 2, 3, 4, 5, 10, 63, 64):
    for do in (False, True):
        c = Counter(); perm([5, 7, CAPACITY], r, c, do)
        assert (c.add, c.sqr, c.mul) == expected_counts(r, do), (r, do)
print('instrumented counts == analytic counts')
for r in (1, 2, 3, 5, 64):
    for _ in range(20):
        m0, m1 = random.randrange(P), random.randrange(P)
        assert hash_prefix_opt(m0, m1, r) == hash_prefix(m0, m1, r)
        assert hash_prefix(m0, m1, r, digest_only=True) == hash_prefix(m0, m1, r)
print('optimized / digest_only evaluation == faithful for r in 1,2,3,5,64')

print('\nr | faithful | digest_only | opt (const-fold + row0) | opt one-time precompute')
for r in (1, 2, 3, 4, 64):
    a = Counter(); hash_prefix(1, 2, r, a)
    b = Counter(); hash_prefix(1, 2, r, b, True)
    o = Counter(); pre = Counter(); hash_prefix_opt(1, 2, r, o, pre)
    print(r, '|', a, '|', b, '|', o, '|', pre)
c = Counter(); round_fn([1, 2, 3], 0, c); print('\nper full round   :', c)
c = Counter(); round_fn([1, 2, 3], 10, c); print('per partial round:', c)
c = Counter(); perm([1, 2, 3], 64, c); print('64 rounds        :', c, '(PR claims 816 mult + 576 add)')
