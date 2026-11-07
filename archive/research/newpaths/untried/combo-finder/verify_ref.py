"""Verify a 64-byte message pair with the organizer reference hash-smash/verifier/blake3.py (rounds=2).
Usage: python verify_ref.py "w0 .. w15" "w0' .. w15'"   (hex 32-bit words, little-endian message words)"""

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

import sys, struct, importlib.util
spec = importlib.util.spec_from_file_location('b3', _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/blake3.py'))
b3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(b3)
def msg(s):
    w = [int(x, 16) for x in s.split()]
    assert len(w) == 16
    return struct.pack('<16I', *w)
m1, m2 = msg(sys.argv[1]), msg(sys.argv[2])
h1, h2 = b3.blake3(m1, rounds=2), b3.blake3(m2, rounds=2)
print('distinct:', m1 != m2, 'len', len(m1), len(m2))
print('H(m) =', h1.hex()); print("H(m')=", h2.hex())
print('COLLISION (rounds=2):', h1 == h2)
print('rounds=3 equal:', b3.blake3(m1, rounds=3) == b3.blake3(m2, rounds=3))
