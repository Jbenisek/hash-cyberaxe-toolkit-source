"""Full export of gd_order.build(variant) for the toy validator: every equation with its role and all word names
(constants included), in evaluation order.  Line: "<eqname> <type> <rot> <target> <in1> <in2> [<in3>]"
type ADD3 (t=u+v+w), ADD2 (t=u+v), XROT (t=ROR(u^v, rot)).  Also lists the constant names of the variant.
Usage: python export_full.py <fixed|outhalf> <out>
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
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths'))
from gd_order import build   # noqa: E402

ROT = {"d1": 16, "b1": 12, "d2": 8, "b2": 7}


def main():
    variant, out = sys.argv[1], sys.argv[2]
    eqs, const, vars_ = build(variant, "len64")
    with open(out, "w") as fh:
        fh.write("CONST " + " ".join(sorted(const)) + "\n")
        for name, vs in eqs:
            if ":" not in name:
                fh.write(f"{name} XOR 0 {vs[0]} {vs[1]}\n")
                continue
            role = name.split(":")[1]
            if role in ("a1", "a2"):
                fh.write(f"{name} ADD3 0 {' '.join(vs)}\n")
            elif role in ("c1", "c2"):
                fh.write(f"{name} ADD2 0 {' '.join(vs)}\n")
            else:
                fh.write(f"{name} XROT {ROT[role]} {' '.join(vs)}\n")
    print(out, len(eqs))


if __name__ == "__main__":
    main()
