"""Export the equation system of gd_order.build() (and the table macros of gd_sat) to a plain file for split.c.

Format: line 1 "N E M F"; next N lines word names; next E lines "name k i1..ik"; next M lines "t j1..jt target".
Usage: python export_sys.py <fixed|outhalf> <tables|plain> <out>
"""

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

import sys

sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths'))
from gd_order import build          # noqa: E402
from gd_sat import table_macros     # noqa: E402


def main():
    variant, mode, out = sys.argv[1], sys.argv[2], sys.argv[3]
    eqs, const, vars_ = build(variant, "len64")
    idx = {v: i for i, v in enumerate(vars_)}
    E = []
    for name, vs in eqs:
        ws = [idx[v] for v in vs if v not in const]
        E.append((name, ws))
    M = []
    if mode == "tables":
        for trig, tgt in table_macros(eqs, const):
            t = [idx[u] for u in trig if u not in const]
            M.append((t, idx[tgt]))
    F = len(vars_) - len(eqs)
    with open(out, "w") as fh:
        fh.write(f"{len(vars_)} {len(E)} {len(M)} {F}\n")
        for v in vars_:
            fh.write(v + "\n")
        for name, ws in E:
            fh.write(f"{name} {len(ws)} " + " ".join(map(str, ws)) + "\n")
        for t, tg in M:
            fh.write(f"{len(t)} " + " ".join(map(str, t)) + f" {tg}\n")
    print(variant, mode, "N", len(vars_), "E", len(E), "M", len(M), "F", F,
          "eq sizes", sorted({len(w) for _, w in E}))


if __name__ == "__main__":
    main()
