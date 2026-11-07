"""Bit-level Keccak-f[1600] helpers for the s3-tda-sat scout (SHA3-256 r6, prefix rounds 0-5).

Conventions follow verifier/keccak.py: lane index x + 5*y, bit z of a lane is (lane >> z) & 1.
State bit index: i = 64*(x + 5*y) + z.  Round = theta, rho, pi, chi, iota.
Differences are handled as Python sets of bit indices (sparse) or as 25-lane int lists (dense).
"""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import os
import sys

VERIFIER = _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier')
sys.path.insert(0, VERIFIER)
import keccak as K  # organizer reference, read-only use

RHO = K.RHO_OFFSETS
RC = K.ROUND_CONSTANTS
MASK = (1 << 64) - 1


def idx(x, y, z):
    return 64 * (x + 5 * y) + z


def xyz(i):
    lane, z = divmod(i, 64)
    return lane % 5, lane // 5, z


# ---------- message geometry: one 135-byte block, byte 135 = 0x86, capacity 512 zero ----------
def free_bits():
    """Bit indices a 135-byte message controls (lanes 0..15 fully, lane 16 bits 0..55)."""
    out = []
    for lane in range(17):
        top = 56 if lane == 16 else 64
        for z in range(top):
            out.append(64 * lane + z)
    return out


FREE = frozenset(free_bits())


# ---------- sparse linear layer ----------
def theta_set(s):
    par = {}
    for i in s:
        x, y, z = xyz(i)
        par[(x, z)] = par.get((x, z), 0) ^ 1
    eff = {}
    for (x, z), p in par.items():
        if p:
            for col in (((x + 1) % 5, z), ((x - 1) % 5, (z + 1) % 64)):
                eff[col] = eff.get(col, 0) ^ 1
    out = set(s)
    for (x, z), e in eff.items():
        if e:
            for y in range(5):
                out ^= {idx(x, y, z)}
    return out


def odd_columns(s):
    par = {}
    for i in s:
        x, y, z = xyz(i)
        par[(x, z)] = par.get((x, z), 0) ^ 1
    return {c for c, p in par.items() if p}


def rhopi_bit(i):
    x, y, z = xyz(i)
    return idx(y, (2 * x + 3 * y) % 5, (z + RHO[x + 5 * y]) % 64)


RHOPI = [rhopi_bit(i) for i in range(1600)]
RHOPI_INV = [0] * 1600
for _i, _j in enumerate(RHOPI):
    RHOPI_INV[_j] = _i


def rhopi_set(s):
    return {RHOPI[i] for i in s}


def rhopi_inv_set(s):
    return {RHOPI_INV[i] for i in s}


def L_set(s):
    """theta, rho, pi applied to a difference (linear)."""
    return rhopi_set(theta_set(s))


def rows(s):
    """chi rows of a difference: {(y, z): 5-bit value, bit x}."""
    r = {}
    for i in s:
        x, y, z = xyz(i)
        r[(y, z)] = r.get((y, z), 0) | (1 << x)
    return {k: v for k, v in r.items() if v}


def unrows(rw):
    s = set()
    for (y, z), v in rw.items():
        for x in range(5):
            if (v >> x) & 1:
                s.add(idx(x, y, z))
    return s


# ---------- chi on one row ----------
def chi5(v):
    o = 0
    for x in range(5):
        b = ((v >> x) & 1) ^ ((((v >> ((x + 1) % 5)) & 1) ^ 1) & ((v >> ((x + 2) % 5)) & 1))
        o |= b << x
    return o


CHI = [chi5(v) for v in range(32)]
DDT = [[0] * 32 for _ in range(32)]
for _a in range(32):
    for _x in range(32):
        DDT[_a][CHI[_x] ^ CHI[_x ^ _a]] += 1


def wrow(a):
    """restriction weight of a chi row input difference a (= -log2 of any nonzero DDT entry / 32)."""
    if a == 0:
        return 0
    m = max(DDT[a])
    w = 0
    while (32 >> w) != m:
        w += 1
    return w


W = [wrow(a) for a in range(32)]


def weight(s):
    """restriction weight of a chi-input difference given as a bit set."""
    return sum(W[v] for v in rows(s).values())


def out_space(a):
    return [b for b in range(32) if DDT[a][b]]


# digest round: plane y=0 rows, output bits x=0..3 must have zero difference (digest = lanes 0..3)
DIG_MASK = 0b01111
PD = [sum(1 for x in range(32) if ((CHI[x] ^ CHI[x ^ a]) & DIG_MASK) == 0) for a in range(32)]


def digest_cost(a6):
    """-log2 probability that chi6 gives a zero difference on the 256 digest bits, given chi6 input
    difference a6 (bit set).  Returns None if impossible."""
    import math
    tot = 0.0
    for (y, z), v in rows(a6).items():
        if y != 0:
            continue
        if PD[v] == 0:
            return None
        tot += -math.log2(PD[v] / 32)
    return tot


# ---------- dense full permutation (lane ints), used only to verify against keccak.py ----------
def permute(lanes, rounds):
    lanes = list(lanes)
    for c in RC[:rounds]:
        par = [lanes[x] ^ lanes[x + 5] ^ lanes[x + 10] ^ lanes[x + 15] ^ lanes[x + 20] for x in range(5)]
        th = [par[(x - 1) % 5] ^ (((par[(x + 1) % 5] << 1) | (par[(x + 1) % 5] >> 63)) & MASK) for x in range(5)]
        mv = [0] * 25
        for y in range(5):
            for x in range(5):
                v = lanes[x + 5 * y] ^ th[x]
                r = RHO[x + 5 * y] % 64
                mv[y + 5 * ((2 * x + 3 * y) % 5)] = ((v << r) | (v >> ((64 - r) % 64))) & MASK
        for y in range(5):
            for x in range(5):
                lanes[x + 5 * y] = (mv[x + 5 * y] ^ ((~mv[(x + 1) % 5 + 5 * y]) & mv[(x + 2) % 5 + 5 * y])) & MASK
        lanes[0] ^= c
    return lanes


def set_to_lanes(s):
    lanes = [0] * 25
    for i in s:
        lanes[i // 64] |= 1 << (i % 64)
    return lanes


def lanes_to_set(lanes):
    return {64 * l + z for l in range(25) for z in range(64) if (lanes[l] >> z) & 1}


def lin_dense(lanes):
    """theta, rho, pi on lane ints (for cross-checking L_set)."""
    par = [lanes[x] ^ lanes[x + 5] ^ lanes[x + 10] ^ lanes[x + 15] ^ lanes[x + 20] for x in range(5)]
    th = [par[(x - 1) % 5] ^ (((par[(x + 1) % 5] << 1) | (par[(x + 1) % 5] >> 63)) & MASK) for x in range(5)]
    mv = [0] * 25
    for y in range(5):
        for x in range(5):
            v = lanes[x + 5 * y] ^ th[x]
            r = RHO[x + 5 * y] % 64
            mv[y + 5 * ((2 * x + 3 * y) % 5)] = ((v << r) | (v >> ((64 - r) % 64))) & MASK
    return mv


def selftest(seed=1, n=20):
    import random
    rnd = random.Random(seed)
    for _ in range(n):
        st = bytes(rnd.getrandbits(8) for _ in range(200))
        lanes = [int.from_bytes(st[8 * i:8 * i + 8], "little") for i in range(25)]
        for r in (1, 2, 6):
            ref = K.permutation(st, rounds=r)
            mine = b"".join(v.to_bytes(8, "little") for v in permute(lanes, r))
            assert ref == mine, "permute mismatch"
        s = {rnd.randrange(1600) for _ in range(rnd.randrange(1, 40))}
        assert lanes_to_set(lin_dense(set_to_lanes(s))) == L_set(s), "L_set mismatch"
    # sha3_256 r6 path on a 135-byte message uses one permutation of (msg || 0x86 || 0^512)
    m = bytes(rnd.getrandbits(8) for _ in range(135))
    blk = m + b"\x86" + bytes(64)
    lanes = [int.from_bytes(blk[8 * i:8 * i + 8], "little") for i in range(25)]
    out = permute(lanes, 6)
    dig = b"".join(v.to_bytes(8, "little") for v in out)[:32]
    assert dig == K.sha3_256(m, rounds=6), "sha3_256 r6 mismatch"
    return True


if __name__ == "__main__":
    print("selftest", selftest())
    print("free message bits", len(FREE))
