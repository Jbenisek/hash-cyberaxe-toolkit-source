"""Export the constraint hypergraph of gd_order.build() for the shape search (shape_any agent).

Usage: python export.py <fixed|outhalf> <out.sys> [promoted,comma,list]
Promoted words become sub-family constants; then constants are propagated (an equation with one unknown fixes it).
Format: "N E F" / N lines name / E lines "eqname k i1..ik" (indices of unknown words).
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
sys.dont_write_bytecode = True            # never write __pycache__ outside this folder
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths'))
from gd_order import build                # noqa: E402


def system(variant, promoted=()):
    eqs, const, vars_ = build(variant, "len64")
    const = set(const) | set(promoted)
    dropped = []
    changed = True
    while changed:
        changed = False
        keep = []
        for name, vs in eqs:
            unk = [v for v in vs if v not in const]
            if len(unk) == 1:
                const.add(unk[0]); changed = True; dropped.append((name, "fixes " + unk[0]))
            elif len(unk) == 0:
                dropped.append((name, "condition on constants"))
            else:
                keep.append((name, vs))
        eqs = keep
    names = sorted({v for _, vs in eqs for v in vs} - const)
    idx = {v: i for i, v in enumerate(names)}
    E = [(name, [idx[v] for v in vs if v not in const]) for name, vs in eqs]
    return names, E, dropped


def main():
    variant, out = sys.argv[1], sys.argv[2]
    prom = [p for p in sys.argv[3].split(",") if p] if len(sys.argv) > 3 else []
    names, E, dropped = system(variant, prom)
    with open(out, "w") as fh:
        fh.write(f"{len(names)} {len(E)} {len(names) - len(E)}\n")
        for n in names:
            fh.write(n + "\n")
        for name, ix in E:
            fh.write(f"{name} {len(ix)} " + " ".join(map(str, ix)) + "\n")
    print(f"{variant} promoted={prom}: N={len(names)} E={len(E)} F={len(names) - len(E)} dropped={len(dropped)}")
    for d in dropped:
        print("  ", d)


if __name__ == "__main__":
    main()
