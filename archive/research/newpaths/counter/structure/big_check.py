"""Large t (v13 != 0): compare the C program's digest of P||X (P = t copies of the chunk) with the digest
formed by the ORGANIZER's own internals (_chunk_output with counter t, _compress, _parent_output, ROOT) from
the C program's prefix stack, and with the own Python code.  The prefix stack itself can only come from the C
program (2^36 compressions); the C program was validated against the organizer for 25 values of t up to 1025
(tree_check.txt, check (e)), including its SIMD/thread path.
usage: python -B big_check.py OUTFILE"""

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

import sys, struct
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
import blake3 as V
import b3own as O

lines = open(sys.argv[1]).read().splitlines()
t = int([ln for ln in lines if ln.startswith('t ')][0].split()[1])
stack = [tuple(int(h, 16) for h in ln.split()[1:]) for ln in lines if ln.startswith('stack') and not ln.startswith('stack ')]
xs = open(__file__.replace('big_check.py', 'big_x.hex')).read().split()
cdig = [tuple(int(h, 16) for h in ln.split()[1:]) for ln in lines if ln.startswith('digest_words')]
ccv = [tuple(int(h, 16) for h in ln.split()[1:]) for ln in lines if ln.startswith('cvx')]
print(f't = {t} = 2^32 * {t >> 32} + {t & 0xFFFFFFFF}; v12 = {t & 0xFFFFFFFF:08x}, v13 = {t >> 32:08x}; '
      f'stack entries {len(stack)}; message lengths {1024 * t + 55} / {1024 * t + 63} bytes')
ok = 0
for k, xh in enumerate(xs):
    x = bytes.fromhex(xh)
    out = V._chunk_output(x, t, 2)
    desc_ok = out[0] == V.IV and out[2] == t and out[3] == len(x) and out[4] == 3
    cv_org = tuple(V._compress(*out, 2)[:8])
    st = list(stack)
    while st:
        out = V._parent_output(st.pop(), V._compress(*out, 2)[:8])
    cv, words, _, blen, flags = out
    dig_org = tuple(V._compress(cv, words, 0, blen, flags | V.ROOT, 2)[:8])
    dig_own = struct.unpack('<8I', O.root_from_stack(stack, O.chunk_cv(x, t)))
    good = desc_ok and cv_org == ccv[k] and dig_org == cdig[k] and dig_own == cdig[k]
    ok += good
    print(f'  X{k} ({len(x)} bytes): organizer descriptor (IV, words, t, len, 3) {desc_ok}; CV_t equal C/organizer '
          f'{cv_org == ccv[k]}; digest C == organizer-internals {dig_org == cdig[k]}; == own {dig_own == cdig[k]}')
print(f'all agree: {ok}/{len(xs)}')
