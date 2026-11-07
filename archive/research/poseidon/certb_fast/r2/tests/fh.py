
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

import flint, subprocess, os, sys, json, random
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
R = flint.fmpz_mod_poly_ctx(P)
X = R.gen()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WSLROOT = _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/certb_fast/r2')
def write_poly(path, coeffs):
    with open(path, 'wb') as f:
        for c in coeffs: f.write(int(c).to_bytes(32, 'little'))
def read_poly(path):
    raw = open(path, 'rb').read()
    return [int.from_bytes(raw[i:i+32], 'little') for i in range(0, len(raw), 32)]
def to_poly(coeffs): return R([int(c) for c in coeffs])
def coeffs(poly):
    n = poly.degree()
    return [int(poly[i]) for i in range(n + 1)]
def run_wsl(args, log=None):
    """run certb_fast via a script file; args: list of strings with paths relative to certb_fast (WSL view)"""
    sh = os.path.join(HERE, '_run.sh')
    open(sh, 'w', newline='\n').write('#!/bin/bash\ncd %s\nnice -n 10 ./certb_fast %s\n' % (WSLROOT, ' '.join(args)))
    r = subprocess.run(['wsl', 'bash', WSLROOT + '/tests/_run.sh'], capture_output=True, text=True)
    return r.stdout, r.stderr, r.returncode
def rand_poly(rng, d, monic=True):
    c = [rng.randrange(P) for _ in range(d)] + [1]
    return R(c)
