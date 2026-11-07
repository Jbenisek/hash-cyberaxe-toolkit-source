
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
base = _hca_public_path_text('__HCA_WORKSPACE__/research/')
old = open(base + "blake3_r6/b9r6/pkg/blake3/experiments/bsrho.py", encoding="utf-8", newline="").read()
ref = open(base + "blake3_r4/b4f/pkg/blake3/experiments/bsrho.py", encoding="utf-8", newline="").read()
a = ref.index("def _lossq(")
b = ref.index("_B = {}", a)
new_loss = ref[a:b].replace("40 - (Tp - 1).bit_length()", "64 - (Tp - 1).bit_length()")
assert "64 - (Tp - 1)" in new_loss
s = old.index("def _zq(")
e = old.index("_B = {}", s)
old = old[:s] + new_loss + old[e:]
# drop EPS, HZ lines
lines = old.split("\n")
out = []
i = 0
while i < len(lines):
    ln = lines[i]
    if ln.startswith("EPS = ") or ln.startswith("HZ = "):
        i += 1
        continue
    out.append(ln)
    i += 1
old = "\n".join(out)
open(base + "blake3_r6/b9r6/pkg/blake3/experiments/bsrho.py", "w", encoding="utf-8", newline="").write(old)
print(len(old))
