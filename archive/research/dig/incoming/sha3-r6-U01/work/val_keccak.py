import hashlib, os, sha3lab as L
for n in (0, 5, 64, 135, 136, 200):
    m = os.urandom(n); assert L.sponge_sha3_256(m) == hashlib.sha3_256(m).digest(), n
print('keccak 24 rounds matches hashlib (6 lengths)')
