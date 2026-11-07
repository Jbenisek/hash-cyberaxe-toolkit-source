"""Modular characters (Fourier over Z/2^k) of the residual, against XOR characters (Walsh) and a uniform CONTROL.
Train = rand rows [0,2^19), test = rand rows [2^19,2^20), third set = ctx (2^18 rows). Output: modfourier_out.txt.

A character of Z/2^32 is chi_c(x) = exp(2 pi i c x / 2^32). c = 2^(32-k) u depends on the low k bits only
("low" spectra, exact via a 2^k-bin FFT). Small c depends mainly on the top bits / the signed size of x
("top" spectra, from a 2^k-bin FFT of x >> (32-k); every reported top peak is re-evaluated exactly).
The XOR analogue is the Walsh spectrum of the same bits. Coefficient = |E chi_c(x)|, c != 0.
Also: exact Z/2^32-module (Howell/Hermite) rank of the residual vectors and of the modular E-parts.
"""
import sys
sys.dont_write_bytecode = True
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
W = ("1", "3", "4", "6")
E1IDX = (0, 2, 3, 1); E3IDX = (2, 0, 1, 3)
rng = np.random.default_rng(0x4D4F44554C415202)


def load(name):
    dig = np.fromfile(os.path.join(DATA, name, "dig.u32"), dtype="<u4").reshape(-1, 8)
    eo = np.fromfile(os.path.join(DATA, name, "eout.u32"), dtype="<u4").reshape(-1, 16)
    res = np.fromfile(os.path.join(DATA, name, "res.u32"), dtype="<u4").reshape(-1, 4)
    Rm = (dig[:, :4] - dig[:, 4:]).astype(np.uint32)
    M1 = np.stack([(eo[:, i] - eo[:, 4 + i]).astype(np.uint32) for i in E1IDX], 1)
    M3 = np.stack([(eo[:, 8 + i] - eo[:, 12 + i]).astype(np.uint32) for i in E3IDX], 1)
    return res, Rm, M1, M3


R, Rm, M1, M3 = load("rand"); Rc, Rmc, M1c, M3c = load("ctx")
N = R.shape[0]; H = N // 2
CT = rng.integers(0, 1 << 32, size=(N, 4), dtype=np.uint64).astype(np.uint32)


def fwht(a):
    a = a.astype(np.float64).copy(); n = len(a); h = 1
    while h < n:
        a = a.reshape(-1, 2, h); a = np.stack([a[:, 0] + a[:, 1], a[:, 0] - a[:, 1]], 1).reshape(n); h *= 2
    return a


def spec(idx, nb, kind):
    """|coefficients| / n of the distribution of idx (ints in [0, 2^nb)); kind 'mod' = FFT (nd if tuple), 'xor' = Walsh."""
    n = len(idx)
    if isinstance(nb, tuple):
        h = np.bincount(idx, minlength=int(np.prod(nb))).reshape(nb).astype(np.float64)
        f = np.abs(np.fft.fftn(h)).ravel() / n
    else:
        h = np.bincount(idx, minlength=1 << nb).astype(np.float64)
        f = (np.abs(np.fft.fft(h)) if kind == "mod" else np.abs(fwht(h))) / n
    f[0] = 0
    return f


def run(label, build, nb, kind, top=3):
    """train: find the top coefficients; test + ctx: same coefficients; control: max on uniform words."""
    ftr = spec(build(R, Rm, slice(0, H)), nb, kind)
    fte = spec(build(R, Rm, slice(H, N)), nb, kind)
    fcx = spec(build(Rc, Rmc, slice(None)), nb, kind)
    fct = spec(build(CT, CT, slice(H, N)), nb, kind)
    order = np.argsort(ftr)[::-1][:top]
    ctl = fct.max()
    s = "  %-34s ctrl max %.4f | " % (label, ctl)
    s += " ; ".join("c=%d tr %.4f te %.4f ctx %.4f" % (c, ftr[c], fte[c], fcx[c]) for c in order)
    nsig = int((fte > 2 * ctl).sum())
    s += " | #test coefs > 2*ctrl max: %d" % nsig
    print(s)
    return ftr, fte, fct


def sec(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


print("rand train %d / test %d, ctx %d; control uniform (seed 0x4D4F44554C415202), n = test size" % (H, N - H, Rc.shape[0]))

sec("A. single word, low 20 bits: modular characters of Rm (FFT) vs XOR characters of R (Walsh)")
for i in range(4):
    for kind, nm in (("mod", "Rm"), ("xor", "R")):
        run("w%s low20 %s %s" % (W[i], nm, kind), lambda a, b, sl, i=i, nm=nm: ((b if nm == "Rm" else a)[sl, i] & 0xFFFFF).astype(np.int64), 20, kind)

sec("B. single word, top 20 bits: low-frequency modular characters of Rm (size/sign structure), exact re-check")
for i in range(4):
    ftr, fte, fct = run("w%s top20 Rm mod" % W[i], lambda a, b, sl, i=i: (b[sl, i] >> 12).astype(np.int64), 20, "mod")
    c = int(np.argsort(ftr)[::-1][0])
    cs = c - (1 << 20) if c >= (1 << 19) else c          # top-20 index c <-> full character with signed c
    ph = ((cs * Rm[H:, i].astype(np.int64)) % (1 << 32)).astype(np.float64) / 2.0 ** 32
    exact = abs(np.exp(2j * np.pi * ph).mean())
    print("      exact |E chi_c| at signed c=%d (full 32-bit character) on test: %.4f" % (cs, exact))

sec("C. pairs of words, low 10 bits and top 10 bits each: (Z/1024)^2 modular vs Walsh on the same 20 bits")
for a in range(4):
    for b in range(a + 1, 4):
        for part in ("low", "top"):
            def bld(x, y, sl, a=a, b=b, part=part, src="m"):
                v = y if src == "m" else x
                f = (lambda z: (z & 1023)) if part == "low" else (lambda z: (z >> 22))
                return (f(v[sl, a]).astype(np.int64) << 10) | f(v[sl, b]).astype(np.int64)
            run("w%s,w%s %s10 Rm mod" % (W[a], W[b], part), bld, (1024, 1024), "mod", top=2)
            run("w%s,w%s %s10 R  xor" % (W[a], W[b], part), lambda x, y, sl, bld=bld: bld(x, y, sl, src="x"), 20, "xor", top=2)

sec("D. all four words, low 5 / top 5 bits each: (Z/32)^4 modular vs Walsh")
for part in ("low", "top"):
    def bld4(x, y, sl, part=part, src="m"):
        v = y if src == "m" else x
        f = (lambda z: (z & 31)) if part == "low" else (lambda z: (z >> 27))
        o = np.zeros(v[sl].shape[0], np.int64)
        for i in range(4):
            o = (o << 5) | f(v[sl, i]).astype(np.int64)
        return o
    run("4 words %s5 Rm mod" % part, bld4, (32, 32, 32, 32), "mod")
    run("4 words %s5 R  xor" % part, lambda x, y, sl, bld4=bld4: bld4(x, y, sl, src="x"), 20, "xor")

sec("E. sum of squared coefficients (= 2^n * collision prob of the n bits; coordinate-specific) on TEST, low 20 bits per word")
for i in range(4):
    out = []
    for nm, arr in (("R", R), ("Rm", Rm), ("ctrl", CT)):
        v = (arr[H:, i] & 0xFFFFF).astype(np.int64)
        c = np.bincount(v, minlength=1 << 20).astype(np.float64)
        n = c.sum(); coll = (c * (c - 1)).sum() / (n * (n - 1))
        out.append("%s H2(low20) %.3f" % (nm, -np.log2(coll)))
    print("  word %s: " % W[i] + " | ".join(out))


# ---------------------------------------------------------------------------------------------- module rank
sec("F. exact Z/2^32-module spanned by (affine) differences of rows: pivot exponents e_j (module index = sum e_j bits)")
MOD = 1 << 32


def v2(x):
    return (x & -x).bit_length() - 1 if x else 32


def insert(basis, r):
    """basis: dict col -> row (pivot entry exactly 2^e). Howell-style insertion over Z/2^32."""
    stack = [r]
    while stack:
        r = [x % MOD for x in stack.pop()]
        for j in range(len(r)):
            if r[j] == 0:
                continue
            e = v2(r[j]); u = r[j] >> e; uinv = pow(u, -1, MOD)
            if j in basis:
                b = basis[j]; eb = v2(b[j])
                if e >= eb:
                    f = r[j] >> eb
                    r = [(x - f * y) % MOD for x, y in zip(r, b)]
                    continue
                # new row has the smaller valuation: it becomes the pivot, the old pivot row is re-inserted
                nr = [(x * uinv) % MOD for x in r]
                basis[j] = nr
                stack.append(b)
                if e:
                    stack.append([(x << (32 - e)) % MOD for x in nr])
                r = None
                break
            nr = [(x * uinv) % MOD for x in r]
            basis[j] = nr
            if e:
                stack.append([(x << (32 - e)) % MOD for x in nr])
            r = None
            break


def module_report(label, rows, max_rows=4096):
    d = rows.shape[1]; basis = {}
    r0 = [int(x) for x in rows[0]]
    full_at = None
    for t in range(1, min(max_rows, rows.shape[0])):
        insert(basis, [int(x) - y for x, y in zip(rows[t], r0)])
        ex = [v2(basis[j][j]) if j in basis else 32 for j in range(d)]
        if sum(ex) == 0 and full_at is None:
            full_at = t
            break
    ex = [v2(basis[j][j]) if j in basis else 32 for j in range(d)]
    print("  %-40s cols %2d rows used %5d  pivot exponents %s  index %d bits  %s" % (
        label, d, t, ex, sum(ex), "FULL (no affine Z/2^32 relation)" if sum(ex) == 0 else "PROPER submodule/coset"))


module_report("Rm (4 words)", Rm)
module_report("CONTROL uniform (4 words)", CT)
module_report("M1 (4 words)", M1)
module_report("M3 (4 words)", M3)
module_report("M1 | M3 (8 words)", np.concatenate([M1, M3], 1))
module_report("Rm | M1 | M3 (12 words)", np.concatenate([Rm, M1, M3], 1))
module_report("Rm on ctx (4 words)", Rmc)
module_report("M1 | M3 on ctx (8 words)", np.concatenate([M1c, M3c], 1))
