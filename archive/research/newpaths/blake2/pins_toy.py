"""Pinnable output patterns of one G call (COMPUTED, toy widths).  The board pins all six inputs of C3 so that a
message difference in x (m4) leaves only outputs a, c different - a value-dependent transition that no XOR-linear
characteristic has (board_lin.txt).  Here: for a modular difference delta in x only, in y only, or in both, the
frequency over random inputs of every zero-pattern of the output difference (which of a2, b2, c2, d2 are equal).
A pattern with frequency > 0 can be pinned (choose constants from a hit); frequency 0 over many samples and an
exact argument = impossible.  Usage: python -B pins_toy.py N"""
import sys
import numpy as np
sys.dont_write_bytecode = True
U = np.uint64


def rots(w):
    return tuple((r * w) // 32 for r in (16, 12, 8, 7))


def vrotr(z, r, w):
    m = U((1 << w) - 1)
    return ((z >> U(r)) | (z << U(w - r))) & m if r % w else z & m


def vG(a, b, c, d, x, y, w):
    R = rots(w)
    m = U((1 << w) - 1)
    a = (a + b + x) & m; d = vrotr(d ^ a, R[0], w); c = (c + d) & m; b = vrotr(b ^ c, R[1], w)
    a = (a + b + y) & m; d = vrotr(d ^ a, R[2], w); c = (c + d) & m; b = vrotr(b ^ c, R[3], w)
    return a, b, c, d


def main(N):
    rng = np.random.default_rng(3)
    lines = []
    for w in (8, 12, 16):
        mk = U((1 << w) - 1)
        for name, dx, dy in (("x+8 (board C3)", 8, 0), ("x-8", (1 << w) - 8, 0), ("y+1 (flags C0)", 0, 1),
                             ("y random", None, "r"), ("x random (flags C2)", "r", None)):
            a, b, c, d, x, y = (rng.integers(0, 1 << w, size=N, dtype=np.int64).astype(U) for _ in range(6))
            ddx = U(0) if dx is None else (rng.integers(1, 1 << w, size=N, dtype=np.int64).astype(U) if dx == "r" else U(dx))
            ddy = U(0) if dy is None else (rng.integers(1, 1 << w, size=N, dtype=np.int64).astype(U) if dy == "r" else U(dy))
            o1 = vG(a, b, c, d, x, y, w)
            o2 = vG(a, b, c, d, (x + ddx) & mk, (y + ddy) & mk, w)
            eq = [o1[i] == o2[i] for i in range(4)]
            code = eq[0].astype(int) + 2 * eq[1].astype(int) + 4 * eq[2].astype(int) + 8 * eq[3].astype(int)
            cnt = np.bincount(code, minlength=16)
            pats = []
            for k in range(16):
                lab = "".join(("0" if (k >> i) & 1 else "*") for i in range(4))   # order a b c d; 0 = no difference
                pats.append(f"{lab}:{cnt[k]}")
            lines.append(f"w={w:2d} N={N} d={name:20s} " + " ".join(pats))
            print(lines[-1], flush=True)
    with open("pins_toy.txt", "w") as fh:
        fh.write(__doc__ + "\npattern = a b c d of the output; '0' = equal, '*' = differs; counts over N random inputs\n")
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main(int(sys.argv[1]))
