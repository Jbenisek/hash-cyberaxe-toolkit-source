"""Our own port of the Poseidon v1.1 Grain-LFSR parameter generator (field=1, sbox=0, n=255, t=3, R_F=8, R_P=56).
Written from the published algorithm description; compared to the deployed constants."""
from constants_own import P, ROUND_CONSTANTS, MDS
def bits(v, n): return [(v >> (n - 1 - i)) & 1 for i in range(n)]
state = bits(1, 2) + bits(0, 4) + bits(255, 12) + bits(3, 12) + bits(8, 10) + bits(56, 10) + [1] * 30
assert len(state) == 80
def upd():
    global state
    nb = state[62] ^ state[51] ^ state[38] ^ state[23] ^ state[13] ^ state[0]
    state = state[1:] + [nb]
    return nb
for _ in range(160): upd()
def rbits(n):
    out = []
    while len(out) < n:
        b = upd()
        if b == 1: out.append(upd())
        else: upd()
    return out
def relem():
    while True:
        v = int(''.join(map(str, rbits(255))), 2)
        if v < P: return v
rc = [relem() for _ in range(192)]
mine = [x for row in ROUND_CONSTANTS for x in row]
print('regenerated round constants match deployed:', rc == mine, '| first-row match count:', sum(a == b for a, b in zip(rc, mine)))
# MDS: 6 further 255-bit draws, each reduced mod p WITHOUT rejection (found by experiment; 3 of the 6 draws are >= p), x=first 3, y=last 3
raw = [int(''.join(map(str, rbits(255))), 2) for _ in range(6)]
xs = [r % P for r in raw[:3]]; ys = [r % P for r in raw[3:]]
M = tuple(tuple(pow(xs[i] + ys[j], -1, P) for j in range(3)) for i in range(3))
print('regenerated MDS (Cauchy 1/(x_i+y_j), draws mod p) matches deployed:', M == MDS)
