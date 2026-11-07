# r37 "late dense-part variants": flip free bits of E9, E10, E11, E13 (the E bits the characteristic leaves free, same
# in both members), recompute A9..A13 / W9..W13 of both members from the E-parametrisation, keep every cell of rows
# 9..13, then enumerate rows 14 and 15 to get each variant's own L* (set of (W14, W15)).
# Rows 0..8 are untouched, so W0..W8 (thus u = W0 + s0(W1), W6/W7 Step-2 tests and the A0-variant family through W8)
# are shared with S: every first-block good pair would meet sum_l |L*_l| Step-3 candidates instead of |L*_S| = 32.
# Self-check: S itself must give exactly the published L* (W14 = bd1d3f7b, the 32 published W15 values).
# Data source (read only): public package of submission 1f12a09a, imported as tables (no file or network side effects).
# Run: python -B late_variants_r37.py  (one process, pure Python; a few minutes)

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

import importlib.util, itertools, sys, time
P = _hca_public_path_text('__HCA_WORKSPACE__/research/stuck/r37-1f12a09a/pkg/experiments/a0core.py')
spec = importlib.util.spec_from_file_location("a0core", P); a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
M = a.M32; S0, S1, s0, s1, CH, MAJ, K = a.S0, a.S1, a.s0, a.s1, a.CH, a.MAJ, a.K
t0 = time.time()
tx = a.trace(a.CV0, a.MX); ty = a.trace(a.CV0, a.MY)
X0 = (dict(tx[0]), dict(tx[1]), list(tx[2])); Y0 = (dict(ty[0]), dict(ty[1]), list(ty[2]))
for i in range(0, 37):
    assert a.row_ok(tx, ty, i), i          # the published SFS pair follows every cell
def Arow(E, A, i): return (E - A[i-4] + S0(A[i-1]) + MAJ(A[i-1], A[i-2], A[i-3])) & M
def Wrow(A, E, i): return (E[i] - A[i-4] - E[i-4] - S1(E[i-1]) - CH(E[i-1], E[i-2], E[i-3]) - K[i]) & M
def md(x, y): return (y - x) & M
# deterministic expanded-difference terms fixed once W9, W10, W14, W15 are fixed (all other words in them carry no
# difference or a difference fixed by the F6/F7 Step-2 sets and the W6/W8 cells): compare with the published pair
def dW16(X, Y): return (md(s1(X[2][14]), s1(Y[2][14])) + md(X[2][9], Y[2][9])) & M
def dW17(X, Y): return (md(s1(X[2][15]), s1(Y[2][15])) + md(X[2][10], Y[2][10])) & M
def dW25(X, Y): return (md(s0(X[2][10]), s0(Y[2][10])) + md(X[2][9], Y[2][9])) & M
def ds0W9(X, Y): return md(s0(X[2][9]), s0(Y[2][9]))
def dW29(X, Y): return (md(X[2][22], Y[2][22]) + md(s0(X[2][14]), s0(Y[2][14]))) & M   # uses expanded W22
def dW30(X, Y): return (md(s0(X[2][15]), s0(Y[2][15])) + md(X[2][14], Y[2][14])) & M
REF = {f.__name__: f(X0, Y0) for f in (dW16, dW17, dW25, ds0W9, dW30)}
print("published reference differences:", {k: "%08x" % v for k, v in REF.items()})
def x2_rows(X, r): return a.x2_ok(X, r)
def free(i): return (~a.CELLS['E'][i][0]) & M
def subsets(mask):
    bits = [b for b in range(32) if mask >> b & 1]
    for k in range(1 << len(bits)):
        yield sum(1 << bits[j] for j in range(len(bits)) if k >> j & 1)
ED = {i: a.CELLS['E'][i][2] for i in range(-4, 37)}
def rebuild(X, Y, i, flip):
    """Set E_i of both members to the published E_i xor flip (free bits only), recompute A_i and W_i."""
    for T, base in ((X, X0), (Y, Y0)):
        T[1][i] = base[1][i] ^ flip
        T[0][i] = Arow(T[1][i], T[0], i)
        T[2][i] = Wrow(T[0], T[1], i)
def lstar(X, Y):
    """All (W14, W15) for the current rows 0..13: rows 14, 15 cells + deterministic expanded differences."""
    out = []
    m14 = a.CELLS['E'][14][0]; m15 = a.CELLS['E'][15][0]
    for e14 in subsets((~m14) & M):
        X[1][14] = (X0[1][14] & m14) | e14; Y[1][14] = X[1][14] ^ ED[14]
        for T in (X, Y): T[0][14] = Arow(T[1][14], T[0], 14); T[2][14] = Wrow(T[0], T[1], 14)
        if not a.row_ok(X, Y, 14) or not x2_rows(X, 14): continue
        if dW16(X, Y) != REF['dW16']: continue
        w15s = []
        for e15 in subsets((~m15) & M):
            X[1][15] = (X0[1][15] & m15) | e15; Y[1][15] = X[1][15] ^ ED[15]
            for T in (X, Y): T[0][15] = Arow(T[1][15], T[0], 15); T[2][15] = Wrow(T[0], T[1], 15)
            if not a.row_ok(X, Y, 15) or not x2_rows(X, 15): continue
            if dW17(X, Y) != REF['dW17'] or dW30(X, Y) != REF['dW30']: continue
            # W22 = s1(W20) + W15 + s0(W7) + W6 needs W20 (depends on W0..W13, CV-specific); dW29 is checked in the
            # summary only for the published CV, so it is NOT used as a filter here
            # L* (1f12a09a proof s.6.1): the row-16 modular differences of E16 and A16 must equal the published
            # pair's; with W16 difference-free they depend only on rows 12..15 of both members
            if STAR and (dE16(X, Y), dA16(X, Y)) != REF16: continue
            w15s.append(X[2][15])
        if w15s: out.append((X[2][14], sorted(w15s)))
    return out
def dE16(X, Y):
    return (md(X[0][12], Y[0][12]) + md(X[1][12], Y[1][12]) + md(S1(X[1][15]), S1(Y[1][15]))
            + md(CH(X[1][15], X[1][14], X[1][13]), CH(Y[1][15], Y[1][14], Y[1][13]))) & M
def dA16(X, Y):
    return (dE16(X, Y) - md(X[0][12], Y[0][12]) + md(S0(X[0][15]), S0(Y[0][15]))
            + md(MAJ(X[0][15], X[0][14], X[0][13]), MAJ(Y[0][15], Y[0][14], Y[0][13]))) & M
REF16 = (md(X0[1][16], Y0[1][16]), md(X0[0][16], Y0[0][16]))
STAR = '--L' not in sys.argv
X = (dict(X0[0]), dict(X0[1]), list(X0[2])); Y = (dict(Y0[0]), dict(Y0[1]), list(Y0[2]))
ls = lstar(X, Y)
print("self-check S: L* =", [("%08x" % w14, len(w15)) for w14, w15 in ls], " %.1fs" % (time.time() - t0))
pub = sorted(a.LW15)
ok = len(ls) == 1 and ls[0][0] == a.W14X and ls[0][1] == pub
print("matches published (W14X, LW15):", ok)
if not ok:
    extra = [("%08x" % w14, len(w)) for w14, w in ls]
    print("MISMATCH; got", extra, file=sys.stderr)
# late variants: flips of free E bits in rows 9, 10, 11, 13 (row 12 has none); rows 0..8 untouched
rows = [9, 10, 11, 12, 13]
print("free E bits per row:", {i: bin(free(i)).count('1') for i in rows})
survive = []; nodes = 0
def walk(k, X, Y, flips):
    global nodes
    if k == len(rows):
        survive.append(dict(flips)); return
    i = rows[k]
    for f in subsets(free(i)):
        nodes += 1
        rebuild(X, Y, i, f)
        if not a.row_ok(X, Y, i) or not x2_rows(X, i): continue
        if i == 9 and ds0W9(X, Y) != REF['ds0W9']: continue
        if i == 10 and dW25(X, Y) != REF['dW25']: continue
        flips[i] = f; walk(k + 1, X, Y, flips); del flips[i]
    rebuild(X, Y, i, 0)
X = (dict(X0[0]), dict(X0[1]), list(X0[2])); Y = (dict(Y0[0]), dict(Y0[1]), list(Y0[2]))
walk(0, X, Y, {})
print("variants keeping rows 9..13 (incl. S):", len(survive), " nodes", nodes, " %.1fs" % (time.time() - t0))
tot = 0; rows_out = []
CAP = 240
todo = survive if len(survive) <= CAP else [survive[(j * len(survive)) // CAP] for j in range(CAP)]
if len(todo) < len(survive):
    print("L* step on an evenly spaced sample of %d of %d variants (scale the sum by %.3f)" % (len(todo), len(survive), len(survive) / len(todo)))
for fl in todo:
    X = (dict(X0[0]), dict(X0[1]), list(X0[2])); Y = (dict(Y0[0]), dict(Y0[1]), list(Y0[2]))
    for i in rows: rebuild(X, Y, i, fl.get(i, 0))
    ls = lstar(X, Y)
    n = sum(len(w) for _, w in ls); tot += n
    rows_out.append((fl, ls, n))
    print("  flips", {i: "%08x" % v for i, v in fl.items() if v}, "-> W14 count", len(ls), "|L*|", n,
          [("%08x" % w14, len(w)) for w14, w in ls][:4])
scale = len(survive) / max(1, len(todo))
print("sum of |L*| over processed variants:", tot, " scaled to all:", round(tot * scale, 1),
      " (S alone: 32)  ratio %.3f" % (tot * scale / 32.0), " %.1fs" % (time.time() - t0))
print("variants with nonempty L*:", sum(1 for _, ls, n in rows_out if n), "of", len(rows_out), "processed")
