"""Writes the inputs of the large-t run (big.sh): one random 1024-byte chunk, two 55-byte and two 63-byte
last chunks (seeded), as hex files."""
import os, random
H = os.path.dirname(os.path.abspath(__file__))
rng = random.Random(64)
open(os.path.join(H, 'big_chunk.hex'), 'w').write(bytes(rng.getrandbits(8) for _ in range(1024)).hex())
xs = [bytes(rng.getrandbits(8) for _ in range(55)) for _ in range(2)] + \
     [bytes(rng.getrandbits(8) for _ in range(55)) + bytes(8) for _ in range(2)]
open(os.path.join(H, 'big_x.hex'), 'w').write(' '.join(x.hex() for x in xs))
print('ok')
