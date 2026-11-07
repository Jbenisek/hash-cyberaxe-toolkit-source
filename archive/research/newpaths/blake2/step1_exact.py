"""TEST C (exact, linear model): dimension of the probability-one / zero-weight collision subspaces.
For every toy width and both settings (equal length; block-length difference in low 7 bits of v14):
  K = {(dM, dv14) : dout = 0}  (fold included)
  dim of the subspace of K whose addition inputs carry no non-MSB difference in:
     ALL additions (prob-1 characteristic; AGKMM10 Prop. 5/7 style), round 1 only (round 0 left to
     message modification), round-1 diagonals E only, round-1 columns C only.
Also half-collisions (only out0,2,5,7 or only out1,3,4,6).
Self-check: linear model == concrete XOR-linearised BLAKE3 difference on random inputs.
"""
import sys, random
import numpy as np
sys.dont_write_bytecode = True
from lin import Model, nullspace, rank, PERM, COLS, DIAG

IV32 = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]


def lin_compress(msg, w, v14):
    """concrete BLAKE3 with every + replaced by XOR (affine map)."""
    R = tuple((r * w) // 32 for r in (16, 12, 8, 7))
    mk = (1 << w) - 1
    rot = lambda z, r: ((z >> r) | (z << (w - r))) & mk if r % w else z
    v = [x & mk for x in IV32] + [x & mk for x in IV32[:4]] + [0, 0, v14 & mk, 11]
    for r in range(2):
        s = msg if r == 0 else [msg[PERM[i]] for i in range(16)]
        for grp, off in ((COLS, 0), (DIAG, 8)):
            for j, (ia, ib, ic, id_) in enumerate(grp):
                a, b, c, d = v[ia], v[ib], v[ic], v[id_]
                x, y = s[off + 2 * j], s[off + 2 * j + 1]
                a = a ^ b ^ x; d = rot(d ^ a, R[0]); c = c ^ d; b = rot(b ^ c, R[1])
                a = a ^ b ^ y; d = rot(d ^ a, R[2]); c = c ^ d; b = rot(b ^ c, R[3])
                v[ia], v[ib], v[ic], v[id_] = a, b, c, d
    return [v[i] ^ v[i + 8] for i in range(8)]


def selfcheck(md, w, n=50):
    rng = random.Random(5)
    for _ in range(n):
        msg = [rng.getrandbits(w) for _ in range(16)]
        dm = [rng.getrandbits(w) for _ in range(16)]
        dl = rng.getrandbits(md.lw)
        o1 = lin_compress(msg, w, 16)
        o2 = lin_compress([a ^ b for a, b in zip(msg, dm)], w, 16 ^ dl)
        var = 0
        for i in range(16):
            var |= dm[i] << (i * w)
        var |= dl << (16 * w)
        for i in range(8):
            pred = 0
            for b in range(w):
                pred |= (bin(md.out[i][b] & var).count("1") & 1) << b
            assert pred == o1[i] ^ o2[i], (w, i)
    return True


def main():
    lines = []
    for w in (8, 12, 16, 32):
        md = Model(w)
        selfcheck(md, w)
        nv = md.nv
        lenrows = np.zeros((md.lw, nv), dtype=np.uint8)
        for j in range(md.lw):
            lenrows[j, 16 * w + j] = 1
        sel = {
            "all": lambda a: True,
            "round1": lambda a: a[0] == 1,
            "E": lambda a: a[0] == 1 and a[1][0] == "E",
            "C": lambda a: a[0] == 1 and a[1][0] == "C",
            "round0": lambda a: a[0] == 0,
        }
        for target, words in (("full", range(8)), ("halfA_0257", (0, 2, 5, 7)), ("halfB_1346", (1, 3, 4, 6))):
            A = md.out_matrix(words)
            for setting in ("equal_len", "len_diff"):
                AA = np.vstack([A, lenrows]) if setting == "equal_len" else A
                K = nullspace(AA)
                k = K.shape[0]
                res = [f"w={w:2d} {target:10s} {setting:9s} dimK={k:4d}"]
                for nm, f in sel.items():
                    F, _ = md.positions(f)
                    img = (K.astype(np.int64) @ F.T.astype(np.int64)) & 1
                    rk = rank(img.astype(np.uint8))
                    res.append(f"{nm}:zero-dim={k - rk}")
                lines.append("  ".join(res))
                print(lines[-1], flush=True)
    with open("step1_exact.txt", "w") as fh:
        fh.write("TEST C, exact GF(2) ranks (COMPUTED by step1_exact.py). zero-dim = dimension of the subspace of\n"
                 "collision (or half-collision) characteristics with NO non-MSB difference on any addition input in\n"
                 "the named set (= probability one there, in the XOR-linear model).  selfcheck: linear model ==\n"
                 "concrete XOR-linearised BLAKE3 on 50 random (M, dM, dlen) per width: passed.\n\n")
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
