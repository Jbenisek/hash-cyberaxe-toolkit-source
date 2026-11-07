"""n2_states.py - exact law of test (2) on a walk block (research only).

Along one block of the t_hi walk, omega mod 2^16 is fixed and omega >> 16 runs over all 2^16 values (walk_model C4).
Test (2) is read from the shipped byte automaton (frontline.F2, restricted to S): its state after the two low bytes is
a function of omega mod 2^16 alone, so the number N2 of passing high halves of a block depends only on that state.
This counts, exactly, for every one of the 2^16 low halves: its state, N2, and the 2^32 total (must be E_COUNT).
Also the same for test (1) (frontline.F1) on Y9, for reference.
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
import time
from collections import Counter

sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCM/pkg/blake3-r2/experiments'))
import frontline as F  # noqa: E402


def law(f, name, total_ref):
    t0 = time.time()
    st16 = [f[f[lo & 255] + (lo >> 8)] for lo in range(1 << 16)]
    states = Counter(st16)
    n_of = {}
    for s in states:
        n = 0
        for b2 in range(256):
            s3 = f[s + b2]
            for b3 in range(256):
                n += f[s3 + b3] != 0
        n_of[s] = n
    total = sum(n_of[s] * c for s, c in states.items())
    live_lo = sum(c for s, c in states.items() if n_of[s])
    print("%s: %d states after 16 bits; total passing words %d (reference %d, %s)"
          % (name, len(states), total, total_ref, "EQUAL" if total == total_ref else "DIFFERENT"))
    print("  live low halves (some high half passes): %d of 65536 = %.6f = 2^%.4f"
          % (live_lo, live_lo / 65536, __import__("math").log2(live_lo / 65536) if live_lo else float("-inf")))
    for s, c in sorted(states.items(), key=lambda kv: -n_of[kv[0]]):
        print("  state %6d: low halves %6d, passing high halves N2 = %6d (share within block %.6f)"
              % (s, c, n_of[s], n_of[s] / 65536))
    print("  seconds %.1f" % (time.time() - t0))
    return st16, n_of


if __name__ == "__main__":
    st2, n2 = law(F.F2, "test (2) on omega", F.E_COUNT)
    # mean of N2 over a uniform low half = 2^16 * pi_E
    print("mean N2 per full block %.3f = 2^16 * pi_E %.3f" % (sum(n2[s] for s in st2) / 65536, F.E_COUNT / 65536))
    law(F.F1, "test (1) on Y9 (restricted to S)", -1)
