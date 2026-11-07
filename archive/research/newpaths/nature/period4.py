"""Period-k ('tandem repeat') difference subspace of 2-round BLAKE3, XOR-linearised (every + replaced by XOR).

A 32-bit word whose bit pattern repeats every k bits (k | 32) stays such a word under ANY rotation: ROR_r acts as a
rotation of the k-bit pattern by r mod k.  So the carry-free (XOR) model of the compression maps period-k message
differences to period-k state differences.  For k = 4: 4 GF(2) coordinates per word, 64 message coordinates,
output fold out[i] = v[i]^v[i+8] has 32 coordinates.  The kernel = carry-free colliding characteristics inside the
subspace.  This script builds the linear map, the kernel basis, and for each of the 96 additions the linear map to
its two operand patterns; it writes them for the C enumerator (p4enum.c) and prints the kernel dimension.
Usage: python period4.py [k=4]
"""
import sys
import numpy as np

K = int(sys.argv[1]) if len(sys.argv) > 1 else 4
W = 32
ROT = (16, 12, 8, 7)
PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
NIN = 16 * K


def ror(vec, r):
    """vec: (K, NIN) GF(2) rows = pattern bits as linear forms; ROR by r: p'_j = p_{(j+r) mod K}."""
    return vec[[(j + r) % K for j in range(K)], :]


adds = []   # list of (alpha, beta) linear forms (each K x NIN), round index


def add(a, b, rnd):
    adds.append((a.copy(), b.copy(), rnd))
    return a ^ b


def G(a, b, c, d, x, y, rnd):
    t = add(a, b, rnd); a = add(t, x, rnd)
    d = ror(d ^ a, ROT[0])
    c = add(c, d, rnd)
    b = ror(b ^ c, ROT[1])
    t = add(a, b, rnd); a = add(t, y, rnd)
    d = ror(d ^ a, ROT[2])
    c = add(c, d, rnd)
    b = ror(b ^ c, ROT[3])
    return a, b, c, d


def msgword(i):
    m = np.zeros((K, NIN), dtype=np.uint8)
    for j in range(K):
        m[j, i * K + j] = 1
    return m


zero = np.zeros((K, NIN), dtype=np.uint8)
v = [zero.copy() for _ in range(16)]
m = [msgword(i) for i in range(16)]
for rnd in range(2):
    v[0], v[4], v[8], v[12] = G(v[0], v[4], v[8], v[12], m[0], m[1], rnd)
    v[1], v[5], v[9], v[13] = G(v[1], v[5], v[9], v[13], m[2], m[3], rnd)
    v[2], v[6], v[10], v[14] = G(v[2], v[6], v[10], v[14], m[4], m[5], rnd)
    v[3], v[7], v[11], v[15] = G(v[3], v[7], v[11], v[15], m[6], m[7], rnd)
    v[0], v[5], v[10], v[15] = G(v[0], v[5], v[10], v[15], m[8], m[9], rnd)
    v[1], v[6], v[11], v[12] = G(v[1], v[6], v[11], v[12], m[10], m[11], rnd)
    v[2], v[7], v[8], v[13] = G(v[2], v[7], v[8], v[13], m[12], m[13], rnd)
    v[3], v[4], v[9], v[14] = G(v[3], v[4], v[9], v[14], m[14], m[15], rnd)
    m = [m[PERM[i]] for i in range(16)]
out = np.vstack([v[i] ^ v[i + 8] for i in range(8)])  # (8K x NIN)


def nullspace_gf2(A):
    A = A.copy() % 2
    rows, cols = A.shape
    piv = []
    r = 0
    for c in range(cols):
        p = None
        for i in range(r, rows):
            if A[i, c]:
                p = i
                break
        if p is None:
            continue
        A[[r, p]] = A[[p, r]]
        for i in range(rows):
            if i != r and A[i, c]:
                A[i] ^= A[r]
        piv.append(c)
        r += 1
        if r == rows:
            break
    free = [c for c in range(cols) if c not in piv]
    basis = []
    for f in free:
        x = np.zeros(cols, dtype=np.uint8)
        x[f] = 1
        for i, pc in enumerate(piv):
            if A[i, f]:
                x[pc] = 1
        basis.append(x)
    return np.array(basis, dtype=np.uint8), len(piv)


B, rank = nullspace_gf2(out)
print(f"period-{K}: message coords {NIN}, output coords {out.shape[0]}, rank {rank}, kernel dim {len(B)}, additions {len(adds)}")
assert all(((out @ b) % 2 == 0).all() for b in B)
# per basis vector, the operand patterns of every addition
with open(f"p{K}_basis.txt", "w") as f:
    f.write(f"{K} {len(B)} {len(adds)}\n")
    f.write(" ".join(str(r) for _, _, r in adds) + "\n")
    for b in B:
        pats = []
        for a_, b_, _ in adds:
            pa = sum(int((a_[j] @ b) % 2) << j for j in range(K))
            pb = sum(int((b_[j] @ b) % 2) << j for j in range(K))
            pats.append(f"{pa},{pb}")
        msgp = [sum(int(b[i * K + j]) << j for j in range(K)) for i in range(16)]
        f.write(" ".join(str(x) for x in msgp) + " | " + " ".join(pats) + "\n")
print(f"wrote p{K}_basis.txt")
# sanity: the all-ones characteristic of job29 (m3, m10, m14 all-ones) should be in the kernel
allones = np.zeros(NIN, dtype=np.uint8)
for i in (3, 10, 14):
    allones[i * K:(i + 1) * K] = 1
print("job29 all-ones (m3,m10,m14) in kernel:", bool(((out @ allones) % 2 == 0).all()))
