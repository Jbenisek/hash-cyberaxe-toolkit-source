
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

import os, re
os.chdir(_hca_public_path_text('__HCA_WORKSPACE__/research/blake3_r7/b9v4'))
# sec4: the b4f cold-read version, plus the two leftover rho in Step 6 (ii)
s = open("sec4_t9_new.md", encoding="utf-8").read()
for a, b in [("rho is a function of the lottery, so it is determined by G", "sigma is a function of the lottery, so it is determined by G"),
             ("(E rho = L)", "(E sigma = L)")]:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open("sec4_t9.md", "w", encoding="utf-8", newline="\n").write(s)
# scripts of this folder
for src, dst, pairs in [
    ("stage_run9.sh", "stage_run9.sh", [("b9v3", "b9v4"), ("B3R7D", "B3R7D2"), ("pos_b3r7d", "pos_b3r7d2")]),
    ("rc_run9.sh", "rc_run9.sh", [("b9v3", "b9v4")]),
]:
    t = open(src, encoding="utf-8", newline="").read()
    for a, b in pairs:
        assert a in t, (src, a)
        t = t.replace(a, b)
    open(dst, "w", encoding="utf-8", newline="").write(t)
print(open("stage_run9.sh").read())
