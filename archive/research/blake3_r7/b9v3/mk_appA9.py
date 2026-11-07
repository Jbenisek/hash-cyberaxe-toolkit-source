"""Builds appA.py of B3R7d from the B3R7c one (b8v2) and the b4f functions plower/plan_tp/certify."""

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

W = _hca_public_path_text('__HCA_WORKSPACE__/research/blake3_r7')
t = open(W + r"\b8v2\appA.py", encoding="utf-8", newline="").read()
r4 = open(_hca_public_path_text('__HCA_WORKSPACE__/research/blake3_r4/b4f/appA.py'), encoding="utf-8", newline="").read()
assert "\r" not in t and "\r" not in r4
old = "EPS, HZ, GRAIN = 1e-3, 257 / 2, 10 ** 24        # Lemma 2 tail budgets, weight of a squared trail length, B is a multiple of GRAIN\n"
assert t.count(old) == 1
t = t.replace(old, "GRAIN = 10 ** 24                                # B is a multiple of GRAIN\nFINE, COARSE = 20000, 2000                      # bins of the detection-delay sum (last 120 L batches, earlier part)\n")
i = t.index("def zq(")
mark = "lo, hi = 1.0, tmax + 1.0                                       # the largest mean"
j = t.index(mark)
a = r4.index("def plower(")
b = r4.index(mark)
seg = r4[a:b]
key = "min(40 - (Tp - 1).bit_length(), N_BITS - D)"
assert seg.count(key) == 2
seg = seg.replace(key, "min(64 - (Tp - 1).bit_length(), N_BITS - D)")
t = t[:i] + seg + t[j:]
assert "EPS" not in t and "HZ" not in t
open(W + r"\b9v3\appA.py", "w", encoding="utf-8", newline="").write(t)
print("ok")
