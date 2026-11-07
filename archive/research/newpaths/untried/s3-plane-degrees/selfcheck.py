"""Self-check of cubes.cu.
(1) Every stage of 64 random native points vs the ORGANIZER reference hash-smash/verifier/keccak.py:
    S_r = permutation(state0, rounds=r) for r = 1..6, digest = sha3_256(135-byte message, rounds=6),
    B_r = theta/rho/pi of S_{r-1} (organizer formula, re-implemented on Python ints) for r = 3..6.
(2) Cube sums of the small GPU runs vs research/sha3r6/lowdegree/cube_degree.cube (independent numpy implementation)."""

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

import sys, struct, importlib.util
import numpy as np
HERE = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/s3-plane-degrees/')
spec = importlib.util.spec_from_file_location('okec', _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/keccak.py'))
okec = importlib.util.module_from_spec(spec); spec.loader.exec_module(okec)
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/sha3r6/lowdegree'))
import cube_degree as cd

M64 = (1 << 64) - 1
def rot(v, r):
    r %= 64
    return ((v << r) | (v >> ((64 - r) % 64))) & M64
def trp(L):
    C = [L[x] ^ L[x + 5] ^ L[x + 10] ^ L[x + 15] ^ L[x + 20] for x in range(5)]
    D = [C[(x - 1) % 5] ^ rot(C[(x + 1) % 5], 1) for x in range(5)]
    B = [0] * 25
    for y in range(5):
        for x in range(5):
            B[y + 5 * ((2 * x + 3 * y) % 5)] = rot(L[x + 5 * y] ^ D[x], okec.RHO_OFFSETS[x + 5 * y])
    return B
def lanes0(s):
    L = [0] * 25
    for k in range(5): L[k] = s[k]; L[10 + k] = s[k]
    L[16] = 0x86 << 56
    return L
def tob(L): return b''.join(l.to_bytes(8, 'little') for l in L)
def fromb(b): return [int.from_bytes(b[8 * i:8 * i + 8], 'little') for i in range(len(b) // 8)]

# (1) point check
lines = open(HERE + 'check_points.txt').read().split('\n')
pts = []; i = 0
while i < len(lines) and lines[i].startswith('P'):
    s = [int(h, 16) for h in lines[i].split()[1:]]
    st = [[int(h, 16) for h in lines[i + 1 + j].split()[1:]] for j in range(10)]
    pts.append((s, st)); i += 11
SIDX = {1: 0, 2: 1, 3: 3, 4: 5, 5: 7, 6: 9}; BIDX = {3: 2, 4: 4, 5: 6, 6: 8}
bad = 0
for s, st in pts:
    L0 = lanes0(s); state0 = tob(L0)
    S = {r: fromb(okec.permutation(state0, rounds=r)) for r in range(1, 7)}
    for r, j in SIDX.items(): bad += S[r] != st[j]
    for r, j in BIDX.items(): bad += trp(S[r - 1]) != st[j]
    msg = tob(L0[:17])[:135]
    bad += okec.sha3_256(msg, rounds=6) != tob(st[9][:4])
print(f'(1) organizer reference: {len(pts)} points x 15 comparisons, mismatches {bad}')

# (2) cube check
def readvec(path):
    b = open(path, 'rb').read()
    magic, k, n, nst = struct.unpack('<4i', b[:16]); off = 16; out = []
    for _ in range(n):
        t = struct.unpack_from('<5Q', b, off); off += 40
        dirs = [struct.unpack_from('<5Q', b, off + 40 * j) for j in range(k)]; off += 40 * k
        co = struct.unpack_from('<%dQ' % k, b, off) if k else (); off += 8 * k
        sums = struct.unpack_from('<%dQ' % (25 * nst), b, off); off += 8 * 25 * nst
        out.append((t, dirs, co, sums))
    return k, out
def as_int(ws): return sum(w << (64 * i) for i, w in enumerate(ws))
tot = 0; badc = 0; badsrc = 0
for name in ('xc_k3', 'xc_k9', 'xc_k6b'):
    k, cubes = readvec(HERE + name + '.vec.bin')
    for t, dirs, co, sums in cubes:
        dv = [as_int(d) for d in dirs]
        for c, d in zip(co, dv):
            v = 0
            for j in range(40):
                if c >> j & 1: v ^= cd.W[j]
            badsrc += v != d
        res, _ = cd.cube(as_int(t), dv)
        want = {2: list(sums[25:50]), 3: list(sums[75:100]), 4: list(sums[125:150]), 5: list(sums[175:200]), 6: list(sums[225:229])}
        for r in (2, 3, 4, 5, 6):
            badc += [int(x) for x in res[r]] != want[r]; tot += 1
print(f'(2) cube sums vs cube_degree.cube: {tot} stage comparisons, mismatches {badc}; direction/source mismatches {badsrc}')
