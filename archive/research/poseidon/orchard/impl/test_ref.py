"""Validate poseidon_ref.py against PUBLIC halo2_poseidon-0.2.0 test vectors (fp = Pallas base)."""
import re, random, os
from poseidon_ref import *

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'upstream', 'test_vectors.rs')).read()
fp_src = src[src.index('pub mod fp'):src.index('pub mod fq')]
i_hash = fp_src.index('pub fn hash')
perm_src, hash_src = fp_src[:i_hash], fp_src[i_hash:]

def arrays(s):
    nums = [int(x, 16) for x in re.findall(r'0x([0-9a-fA-F]{2})\b', s)]
    assert len(nums) % 32 == 0
    return [int.from_bytes(bytes(nums[i:i + 32]), 'little') for i in range(0, len(nums), 32)]

pa, ha = arrays(perm_src), arrays(hash_src)
assert len(pa) == 66 and len(ha) == 33, (len(pa), len(ha))
okp = okh = okb = 0
for v in range(11):
    ini, fin = pa[6*v:6*v+3], pa[6*v+3:6*v+6]
    assert all(x < P for x in ini + fin)
    okp += perm(ini, 56) == fin
    nk, rho, out = ha[3*v:3*v+3]
    okh += hash_full(nk, rho) == out and hash_reduced(nk, rho, 56) == out
    okb += digest_bytes(nk.to_bytes(32, 'little') + rho.to_bytes(32, 'little'), 56) == out.to_bytes(32, 'little')
print(f'permutation vectors {okp}/11, hash vectors {okh}/11, byte-level digest {okb}/11')
assert okp == okh == okb == 11
print('hash vector 0: nk=%d rho=%d out=0x%064x' % (ha[0], ha[1], ha[2]))
print('hash vector 0 out LE bytes:', ha[2].to_bytes(32, 'little').hex())

# negative controls: wrong capacity / 63 partial rounds / swapped inputs must NOT match vector 0
nk, rho, out = ha[0:3]
assert perm([nk, rho, 3 << 64], 56)[0] != out
assert perm([nk, rho, CAPACITY], 55)[0] != out
assert hash_full(rho, nk) != out
print('negative controls differ: ok')

# structural consistency: reduced schedule vs. independent 64-round loop at r=56; r<56 prefix property
random.seed(12345)
for _ in range(20):
    a, b = random.randrange(P), random.randrange(P)
    assert hash_reduced(a, b, 56) == hash_full(a, b)
print('hash_reduced(r=56) == hash_full on 20 random inputs')
print('schedule(1) =', schedule(1), ' schedule(2) =', schedule(2))
# aliasing/noncanonical rejected
for bad in (P, P + 1, -1):
    try: hash_reduced(bad, 0, 1); raise SystemExit('accepted noncanonical')
    except ValueError: pass
print('noncanonical inputs rejected: ok')
