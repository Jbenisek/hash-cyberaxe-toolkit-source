"""Shared helpers for the s3-chi-transitions scout (SHA3-256, 6-round prefix; 3-round affine fields with free chi
transitions). Lane layout as in research/sha3r6/linstruct/ls.py: bit 64*lane+z, lane = x+5y.
Imports ls (linstruct) for P = pi.rho.theta on (N,25) uint64 arrays and the 1080 free-bit layout."""

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

import sys, json
import numpy as np
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/sha3r6/linstruct'))
import ls

U64 = np.uint64
HERE = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/s3-chi-transitions/')
P = ls.P
rot = ls.rot
RHO = ls.RHO
ALL1 = U64(0xFFFFFFFFFFFFFFFF)


def P_or(A):
    """Union of supports of P(e_q) over the bits q set in A (theta with OR instead of XOR)."""
    C = A[:, 0:5] | A[:, 5:10] | A[:, 10:15] | A[:, 15:20] | A[:, 20:25]
    D = [C[:, (x - 1) % 5] | rot(C[:, (x + 1) % 5], 1) for x in range(5)]
    B = np.zeros_like(A)
    for y in range(5):
        for x in range(5):
            B[:, y + 5 * ((2 * x + 3 * y) % 5)] = rot(A[:, x + 5 * y] | D[x], RHO[x + 5 * y])
    return B


def popc(A):
    """Popcount per row of an (N,25) uint64 array."""
    return np.unpackbits(np.ascontiguousarray(A).view(np.uint8), axis=1).sum(1)


def rows_split(A):
    """Per (N,25) chi input of ONE direction: single-bit rows and multi-bit rows (as lane masks per y)."""
    fixed = np.zeros_like(A); var = np.zeros_like(A)
    for y in range(5):
        L = [A[:, x + 5 * y] for x in range(5)]
        anyr = L[0] | L[1] | L[2] | L[3] | L[4]
        multi = np.zeros_like(anyr)
        for x in range(5):
            for x2 in range(x + 1, 5):
                multi |= L[x] & L[x2]
        single = anyr & ~multi
        for x in range(5):
            s = L[x] & single
            fixed[:, x + 5 * y] |= s
            var[:, (x - 1) % 5 + 5 * y] |= s
            var[:, (x - 2) % 5 + 5 * y] |= s
            var[:, x + 5 * y] |= multi
    return fixed, var


def chi_relax_KN(A2):
    """chi2 relaxed over ALL compatible output differences of one direction.
    Returns K (chi3-input bits active for every chi2 choice) and N (never active)."""
    fixed, var = rows_split(A2)
    Pf = P(fixed); Pv = P_or(var)
    return Pf & ~Pv, ~Pf & ~Pv


SHIFT_PERM = np.array([(x + 1) % 5 + 5 * y for y in range(5) for x in range(5)])


def shiftx(A):
    """Lane array of the right row-neighbour: out[x,y] = A[x+1,y]."""
    return A[..., SHIFT_PERM]


def conflict(Ka, Na, Kb, Nb):
    """True where an adjacent pair of positions has forms (over span{a,b}) that are both fixed, nonzero, different.
    Broadcasts over leading axes. Inputs (...,25) uint64."""
    F10 = Ka & Nb; F01 = Na & Kb; F11 = Ka & Kb
    G10, G01, G11 = shiftx(F10), shiftx(F01), shiftx(F11)
    bad = (F10 & (G01 | G11)) | (F01 & (G10 | G11)) | (F11 & (G10 | G01))
    return bad.any(axis=-1)


def chi5(a):
    o = 0
    for i in range(5):
        ai = (a >> i) & 1; a1 = (a >> ((i + 1) % 5)) & 1; a2 = (a >> ((i + 2) % 5)) & 1
        o |= (ai ^ ((a1 ^ 1) & a2)) << i
    return o


def Uspace(delta):
    """Affine space of chi output differences for row input difference delta: (base, [generators])."""
    S = sorted({chi5(a ^ delta) ^ chi5(a) for a in range(32)})
    base = delta if delta in S else S[0]
    gens = []; piv = {}
    for u in S:
        r = u ^ base
        while r:
            p = r.bit_length() - 1
            if p in piv: r ^= piv[p]
            else: piv[p] = r; gens.append(r); break
    assert len(S) == 1 << len(gens)
    return base, gens


def bits_to_lanes(bits):
    A = np.zeros((1, 25), dtype=U64)
    for b in bits:
        A[0, b // 64] |= U64(1) << U64(b % 64)
    return A


def lanes_to_bits(A):
    return [int(b) for b in np.nonzero(ls.tobits(np.atleast_2d(A))[0])[0]]


def load_cycles():
    """The 1,749 linstruct3 cycle words (cands.json, w1>0): theta1-kernel, stopped chi1 output in theta2 kernel."""
    out = []
    for c in json.load(open(_hca_public_path_text('__HCA_WORKSPACE__/research/sha3r6/linstruct3/cands.json'))):
        if c['w1'] == 0: continue
        s = set()
        for p in c['pairs']:
            for b in p: s ^= {b}
        out.append(tuple(sorted(s)))
    return sorted(set(out))


def colpar(A):
    """(N,25) -> (N,5) column parity lanes."""
    return A[:, 0:5] ^ A[:, 5:10] ^ A[:, 10:15] ^ A[:, 15:20] ^ A[:, 20:25]
