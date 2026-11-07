"""Independent rebuild of the word-level guess-and-determine (GD) hypergraph of 2-round BLAKE3 (one block).
Written from the task spec, not copied from ../gd_order.py; compared against it below.

reference(): standard BLAKE3 compress with r rounds (checked against the official empty-input hash at r = 7).
system(held, variant): variables = message words + the 8 intermediate words of every G call; equations = the 8
  primitive steps of every G call (each links 3 or 4 words and is solvable for any one of them) + one 2-word
  equation out_i = v_i ^ v_{i+8} per held output word.  Round 1 keeps only E0, E2 (the half out0,2,5,7).
Run: python build.py   -> self checks (test vector, wiring vs reference, equality with gd_order.build).
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

import random
import sys

M32 = 0xFFFFFFFF
IV = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAG = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]


def ror(x, r):
    return ((x >> r) | (x << (32 - r))) & M32


def g_vals(a, b, c, d, x, y):
    a1 = (a + b + x) & M32; d1 = ror(d ^ a1, 16); c1 = (c + d1) & M32; b1 = ror(b ^ c1, 12)
    a2 = (a1 + b1 + y) & M32; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M32; b2 = ror(b1 ^ c2, 7)
    return a1, d1, c1, b1, a2, d2, c2, b2


def reference(m, rounds, blen=64, flags=11, counter=0):
    v = IV[:] + IV[:4] + [counter & M32, counter >> 32, blen, flags]
    m = list(m)
    for r in range(rounds):
        for j, idx in enumerate(COLS + DIAG):
            a, b, c, d = (v[i] for i in idx)
            t = g_vals(a, b, c, d, m[2 * j], m[2 * j + 1])
            v[idx[0]], v[idx[1]], v[idx[2]], v[idx[3]] = t[4], t[7], t[6], t[5]
        m = [m[p] for p in PERM]
    return [v[i] ^ v[i + 8] for i in range(8)]


def system(held=("out0", "out2", "out5", "out7"), variant="outhalf", rounds=2, keep_e=(0, 2)):
    """Returns eqs [(name, tuple(vars))], const set.  Variable names follow gd_order: 'K0.a1', 'm3', 'init5'."""
    if variant == "fixed":
        keep_e = ()             # E0, E2 inputs are constants, so E0, E2 (and the held outputs) are constants
    state = [f"init{i}" for i in range(16)]
    const = set(state)
    msgname = [f"m{i}" for i in range(16)]
    eqs = []
    order = list(range(16))
    names = (("K", "D"), ("C", "E"))
    ystate = None
    for r in range(rounds):
        s = [msgname[order[i]] for i in range(16)]
        for j, idx in enumerate(COLS + DIAG):
            if r == rounds - 1 and j == 4:
                ystate = list(state)
            if r == rounds - 1 and rounds == 2 and j >= 4 and (j - 4) not in keep_e:
                continue
            nm = f"{names[r][j // 4]}{j % 4}"
            a, b, c, d = (state[i] for i in idx)
            x, y = s[2 * j], s[2 * j + 1]
            w = {t: f"{nm}.{t}" for t in ("a1", "d1", "c1", "b1", "a2", "d2", "c2", "b2")}
            eqs += [(f"{nm}:a1", (w["a1"], a, b, x)), (f"{nm}:d1", (w["d1"], d, w["a1"])),
                    (f"{nm}:c1", (w["c1"], c, w["d1"])), (f"{nm}:b1", (w["b1"], b, w["c1"])),
                    (f"{nm}:a2", (w["a2"], w["a1"], w["b1"], y)), (f"{nm}:d2", (w["d2"], w["d1"], w["a2"])),
                    (f"{nm}:c2", (w["c2"], w["c1"], w["d2"])), (f"{nm}:b2", (w["b2"], w["b1"], w["c2"]))]
            state[idx[0]], state[idx[1]], state[idx[2]], state[idx[3]] = w["a2"], w["b2"], w["c2"], w["d2"]
        order = [order[p] for p in PERM]
    if variant == "fixed":      # inputs of E0, E2 held (12 words)
        const.update(["m1", "m11", "m9", "m14"])
        const.update(ystate[i] for i in (0, 5, 10, 15, 2, 7, 8, 13))
    else:
        for h in held:
            i = int(h[3:])
            eqs.append((h, (state[i], state[i + 8])))
    return eqs, const, state


def wiring_check(n=200):
    """Evaluate the named system numerically and compare the held out words with reference()."""
    rng = random.Random(5)
    eqs, const, state = system(held=tuple(f"out{i}" for i in range(8)), keep_e=(0, 1, 2, 3))
    bad = 0
    for _ in range(n):
        m = [rng.getrandbits(32) for _ in range(16)]
        val = {f"init{i}": v for i, v in enumerate(IV + IV[:4] + [0, 0, 64, 11])}
        val.update({f"m{i}": m[i] for i in range(16)})
        # evaluate call by call in equation order (forward: first var is the output)
        calls = []
        for name, vs in eqs:
            if ":" in name and name.endswith(":a1"):
                calls.append(name.split(":")[0])
        byname = dict(eqs)
        for cl in calls:
            a, b, x = byname[f"{cl}:a1"][1:]
            d = byname[f"{cl}:d1"][1]; c = byname[f"{cl}:c1"][1]; y = byname[f"{cl}:a2"][3]
            t = g_vals(val[a], val[b], val[c], val[d], val[x], val[y])
            for k, v in zip(("a1", "d1", "c1", "b1", "a2", "d2", "c2", "b2"), t):
                val[f"{cl}.{k}"] = v
        got = [val[state[i]] ^ val[state[i + 8]] for i in range(8)]
        bad += got != reference(m, 2)
    return bad


if __name__ == "__main__":
    empty = reference([0] * 16, 7, blen=0, flags=11)
    hexd = b"".join(w.to_bytes(4, "little") for w in empty).hex()
    print("BLAKE3('') 7 rounds:", hexd, "OK" if hexd ==
          "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262" else "MISMATCH")
    print("wiring check (200 random messages, all 8 out words, 2 rounds): mismatches =", wiring_check())
    sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths'))
    sys.dont_write_bytecode = True
    import gd_order  # read only
    for variant in ("outhalf", "fixed"):
        e1, c1, _ = system(variant=variant)
        e2, c2, _ = gd_order.build(variant, "len64")
        same = sorted((n, tuple(sorted(v))) for n, v in e1) == sorted((n, tuple(sorted(v))) for n, v in e2)
        print(f"{variant}: mine {len(e1)} eqs, gd_order {len(e2)} eqs, identical equation sets: {same}, "
              f"same constants: {c1 == c2}")
