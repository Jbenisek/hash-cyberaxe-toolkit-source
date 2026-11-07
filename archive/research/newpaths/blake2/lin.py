"""XOR-linearised 2-round BLAKE3 (toy width w) for collision-characteristic search with the output fold.

Model (DERIVED, standard: Chabaud-Joux linearisation; Su et al. 2010 and GKNWW14 sec. 6 use it on BLAKE/BLAKE2):
  every modular addition is replaced by XOR; a characteristic is then a linear function of the input
  difference (message difference dM, 16w bits, plus a block-length difference dv14 in the low LW bits).
  Each 2-input addition with input XOR differences (p, q) is passed (output p^q) with probability
  2^-hw((p|q) & ~MSB) (Lipmaa-Moriai, xdp+ for gamma = p^q).  A 3-input add a+b+x is scored as the best of the
  three evaluation orders: min over pairs hw(p|q) + hw((p^q)|r), MSB excluded.
  Collision: dout_i = dv_i ^ dv_{i+8} = 0 for all 8 output words (the fold is part of the linear map).
Positions: one per non-MSB bit of every addition input word.
"""
import numpy as np

PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAG = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]


def rots(w):
    return tuple((r * w) // 32 for r in (16, 12, 8, 7))


class Model:
    def __init__(self, w, lw=7, msg_words=range(16)):
        self.w = w
        self.R = rots(w)
        self.lw = min(lw, w)
        self.nv = 16 * w + self.lw
        self.adds = []          # (round, call, kind, [input words]); kind 'x3' (a+b+msg), 'y3', 'cd'
        zero = [0] * w
        m = []
        for i in range(16):
            if i in msg_words:
                m.append([1 << (i * w + j) for j in range(w)])
            else:
                m.append(list(zero))
        self.m = m
        v14 = [(1 << (16 * w + j)) if j < self.lw else 0 for j in range(w)]
        v = [list(zero) for _ in range(16)]
        v[14] = v14
        for r in range(2):
            s = m if r == 0 else [m[PERM[i]] for i in range(16)]
            names = (["K0", "K1", "K2", "K3"], ["D0", "D1", "D2", "D3"]) if r == 0 else \
                    (["C0", "C1", "C2", "C3"], ["E0", "E1", "E2", "E3"])
            for j, idx in enumerate(COLS):
                o = self.G(r, names[0][j], *(v[i] for i in idx), s[2 * j], s[2 * j + 1])
                for i, t in zip(idx, o):
                    v[i] = t
            if r == 0:
                self.X = [list(t) for t in v]
            else:
                self.Y = [list(t) for t in v]
            for j, idx in enumerate(DIAG):
                o = self.G(r, names[1][j], *(v[i] for i in idx), s[8 + 2 * j], s[9 + 2 * j])
                for i, t in zip(idx, o):
                    v[i] = t
        self.Z = v
        self.out = [[v[i][b] ^ v[i + 8][b] for b in range(w)] for i in range(8)]

    def rotr(self, z, r):
        w = self.w
        return [z[(b + r) % w] for b in range(w)]   # bit b of (z >>> r) is bit b+r of z

    @staticmethod
    def xor(p, q):
        return [a ^ b for a, b in zip(p, q)]

    def G(self, r, name, a, b, c, d, x, y):
        R = self.R
        self.adds.append((r, name, "x3", [a, b, x]))
        a1 = self.xor(self.xor(a, b), x)
        d1 = self.rotr(self.xor(d, a1), R[0])
        self.adds.append((r, name, "cd", [c, d1]))
        c1 = self.xor(c, d1)
        b1 = self.rotr(self.xor(b, c1), R[1])
        self.adds.append((r, name, "y3", [a1, b1, y]))
        a2 = self.xor(self.xor(a1, b1), y)
        d2 = self.rotr(self.xor(d1, a2), R[2])
        self.adds.append((r, name, "cd", [c1, d2]))
        c2 = self.xor(c1, d2)
        b2 = self.rotr(self.xor(b1, c2), R[3])
        return a2, b2, c2, d2

    # ---------------- matrices ----------------
    def forms_to_mat(self, forms):
        nv = self.nv
        M = np.zeros((len(forms), nv), dtype=np.uint8)
        for i, f in enumerate(forms):
            if f:
                bits = bin(f)[2:][::-1]
                idx = [k for k, ch in enumerate(bits) if ch == "1"]
                M[i, idx] = 1
        return M

    def out_matrix(self, words=range(8)):
        forms = [self.out[i][b] for i in words for b in range(self.w)]
        return self.forms_to_mat(forms)

    def positions(self, select=lambda add: True):
        """Return (F, groups): F = position forms matrix (N x nv); groups = per selected addition
        (add_index, kind, [slice per input word]) with w-1 non-MSB bits per input word."""
        forms, groups = [], []
        w = self.w
        for ai, add in enumerate(self.adds):
            if not select(add):
                continue
            sl = []
            for word in add[3]:
                st = len(forms)
                forms.extend(word[: w - 1])   # bits 0..w-2 (MSB excluded)
                sl.append(slice(st, st + w - 1))
            groups.append((ai, add[2], sl))
        return self.forms_to_mat(forms), groups


# ---------------- GF(2) helpers ----------------
def rref(A):
    A = A.copy() & 1
    rows, cols = A.shape
    piv = []
    r = 0
    for c in range(cols):
        if r >= rows:
            break
        nz = np.nonzero(A[r:, c])[0]
        if len(nz) == 0:
            continue
        p = r + nz[0]
        if p != r:
            A[[r, p]] = A[[p, r]]
        mask = A[:, c].astype(bool)
        mask[r] = False
        A[mask] ^= A[r]
        piv.append(c)
        r += 1
    return A[:r], piv


def nullspace(A):
    R, piv = rref(A)
    n = A.shape[1]
    free = [c for c in range(n) if c not in set(piv)]
    B = np.zeros((len(free), n), dtype=np.uint8)
    for k, f in enumerate(free):
        B[k, f] = 1
        for i, p in enumerate(piv):
            if R[i, f]:
                B[k, p] = 1
    return B


def rank(A):
    return len(rref(A)[1])


def exact_weight(img, groups, w):
    """img: 0/1 vector over the positions of `groups` (same layout).  Returns total exact weight."""
    tot = 0
    for ai, kind, sl in groups:
        ws = [img[s] for s in sl]
        if len(ws) == 2:
            tot += int(np.count_nonzero(ws[0] | ws[1]))
        else:
            best = None
            for (i, j, k) in ((0, 1, 2), (0, 2, 1), (1, 2, 0)):
                c = int(np.count_nonzero(ws[i] | ws[j])) + int(np.count_nonzero((ws[i] ^ ws[j]) | ws[k]))
                best = c if best is None else min(best, c)
            tot += best
    return tot
