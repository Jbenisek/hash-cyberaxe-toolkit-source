"""Check cvrate's DBG lines: for each printed trial, rebuild the pair with s8_check.build_cv, hash the full
messages with the organizer reference at 2 rounds, and compare the residual (digest XOR, words 1,3,4,6)."""

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

import struct, sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/nb_verify_sidepaths_0'))
from s8_check import build_cv, ref, IV
fn = sys.argv[1]
B1 = None; cv = IV; fl = 11; ok = bad = 0
for line in open(fn):
    p = line.split()
    if line.startswith("first block:"):
        B1 = struct.pack("<16I", *[int(x, 16) for x in p[2:18]])
    elif line.startswith("mode "):
        if p[1] == "iv":
            B1 = None; cv = IV; fl = 11
        else:
            i = p.index("cv:"); cv = tuple(int(x, 16) for x in p[i + 1:i + 9]); fl = 10
    elif line.startswith("DBG"):
        free = [int(x, 16) for x in p[1:9]]; R = tuple(int(x, 16) for x in p[10:14])
        wa, wb = build_cv(cv, fl, *free)
        mA = struct.pack("<16I", *wa)[:55]; mB = struct.pack("<16I", *wb)[:63]
        if B1 is not None:
            mA = B1 + mA; mB = B1 + mB
        dA = struct.unpack("<8I", ref(mA, 2)); dB = struct.unpack("<8I", ref(mB, 2))
        assert all(dA[k] == dB[k] for k in (0, 2, 5, 7))
        RR = tuple(dA[k] ^ dB[k] for k in (1, 3, 4, 6))
        if RR == R: ok += 1
        else: bad += 1; print("MISMATCH", line.strip(), " ".join(f"{x:08x}" for x in RR))
print(f"cvrate DBG residuals equal to organizer-reference residuals: {ok} ok, {bad} bad")
