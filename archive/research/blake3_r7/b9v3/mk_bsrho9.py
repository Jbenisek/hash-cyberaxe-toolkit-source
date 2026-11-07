"""Builds the B3R7d bsrho.py from the B3R7c one: new _lossq (first-collision proof), no _zq, EPS, HZ."""

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

import re
P = _hca_public_path_text('__HCA_WORKSPACE__/research/blake3_r7/b9v3/pkg/blake3/experiments/bsrho.py')
R4 = _hca_public_path_text('__HCA_WORKSPACE__/research/blake3_r4/b4f/pkg/blake3/experiments/bsrho.py')
t = open(P, encoding="utf-8", newline="").read()
r4 = open(R4, encoding="utf-8", newline="").read()
assert "\r" not in t

# new _lossq from b4f
i = r4.index("def _lossq(")
j = r4.index("_B = {}", i)
new = r4[i:j]
old_key = "min(40 - (Tp - 1).bit_length(), 134)"
assert new.count(old_key) == 1
new = new.replace(old_key, "min(64 - (Tp - 1).bit_length(), 134)")

i0 = t.index("def _zq(")
j0 = t.index("_B = {}", i0)
t = t[:i0] + new + t[j0:]

# drop EPS and HZ
for line in ["EPS = 1e-3                         # Lemma 2 (proof 4): tail budget of the finished-trail count and of the trail sums, each\n",
             "HZ = 257 / 2                       # weight of a squared trail length in the trail sums\n"]:
    assert t.count(line) == 1
    t = t.replace(line, "")
assert "EPS" not in t and "HZ" not in t, [m.start() for m in re.finditer("EPS|HZ", t)]
open(P, "w", encoding="utf-8", newline="").write(t)
print(len(t.encode("utf-8")))
