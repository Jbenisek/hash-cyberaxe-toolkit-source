
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

base = _hca_public_path_text('__HCA_WORKSPACE__/research/')
old = open(base + "blake3_r6/b8r6/appA.py", encoding="utf-8", newline="").read()
ref = open(base + "blake3_r4/b4f/appA.py", encoding="utf-8", newline="").read()
# functions from b4f
a = ref.index("def plower(")
b = ref.index("lo, hi = 1.0, tmax + 1.0                                       # the largest mean")
funcs = ref[a:b]
assert funcs.count("40 - (Tp - 1).bit_length()") == 2
funcs = funcs.replace("40 - (Tp - 1).bit_length()", "64 - (Tp - 1).bit_length()")
# old pieces
s = old.index("def zq(")
e = old.index("lo, hi = 1.0, tmax + 1.0                                       # the largest mean")
new = old[:s] + funcs + old[e:]
old_hdr = "EPS, HZ, GRAIN = 1e-3, 257 / 2, 10 ** 24        # Lemma 2 tail budgets, weight of a squared trail length, B is a multiple of GRAIN\n"
assert old_hdr in new
new = new.replace(old_hdr, "GRAIN = 10 ** 24                                # B is a multiple of GRAIN\nFINE, COARSE = 20000, 2000                      # bins of the detection-delay sum (last 120 L batches, earlier part)\n")
assert "N_BITS, S1, W, KAPPA = 256, 32, 90, 13" in new
new = new.replace("N_BITS, S1, W, KAPPA = 256, 32, 90, 13", "N_BITS, S1, W, KAPPA = 256, 32, 90, 14")
open(base + "blake3_r6/b9r6/appA.py", "w", encoding="utf-8", newline="").write(new)
