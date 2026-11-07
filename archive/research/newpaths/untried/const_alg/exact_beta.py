#!/usr/bin/env python3
r"""exact_beta.py D3 D11 DELTA Y3 Y11 ETA BETA[,BETA..] [TIMEOUT=600]
The atlas calculator (~/hashsmash/h8/bin/h8_pair_calc_batch, executed only; the same call and parse as
research/paths/paths_count.py run_batch / parse_batch, imported unchanged) on the given betas of one pin and class,
one process. Prints part, k and part x 2^k (the counter objective) per beta. Raw output: scratch/exact/ here."""

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
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/paths'))
import paths_lib as L      # noqa: E402
import paths_count as C    # noqa: E402


def main():
    d3, d11, delta, y3, y11, eta = (int(x, 16) for x in sys.argv[1:7])
    betas = [int(b, 16) for b in sys.argv[7].split(',')]
    to = int(sys.argv[8]) if len(sys.argv) > 8 else 600
    p = dict(D3=d3, D11=d11, delta=delta, Y3=y3, Y11=y11, eta=eta)
    s = HERE / 'scratch' / 'exact'
    s.mkdir(parents=True, exist_ok=True)
    tag = f'x{d3:08x}{d11:08x}{eta:08x}'
    rows = [(b, bin(L.rol(b, 12) & 0x7FFFFFFF).count('1')) for b in betas]
    stopped = C.run_batch(p, s, tag, rows, 1, to)
    r = C.parse_batch(s, tag, C.weta(p))
    ok, mask, value, mem = L.class_of(eta, d3)
    for b, k in rows:
        if b in r:
            v = r[b]
            part = float(v['part'])
            rem = f" sampled {v['sampled']}" if v['sampled'] else ''
            print(f"EXACT D3 {d3:08x} D11 {d11:08x} eta {eta:08x} class-ok {int(ok)} 2^{mem} beta {b:08x} k {k} outcomes {v['nz']} "
                  f"part {part:.4f} ctr {part * 2 ** k:.1f}{rem}")
        else:
            print(f"EXACT D3 {d3:08x} D11 {d11:08x} eta {eta:08x} beta {b:08x} k {k} NOT FINISHED (time limit {to} s, stopped {stopped})")


if __name__ == '__main__':
    main()
