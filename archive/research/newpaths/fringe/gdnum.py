"""Numeric check of a guess-and-determine order on the toy (word size w): generates a C program that guesses the
order's words at random, solves every other word in the order's sequence, tests the check equations, and prints
the message words of each member found.  The members are then verified with toyb3 (same effective E0/E2 inputs
and same out0,2,5,7 as the reference message, and different message).
Usage: python gdnum.py <variant> <w> <log2 trials> [seed]      (uses gdv_best_<variant>_len64.txt)
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

import os
import random
import subprocess
import sys

sys.dont_write_bytecode = True
import toyb3 as T  # noqa: E402
from gdv import build  # noqa: E402


def kind(name):
    if ":" in name:
        return name.split(":")[1]
    if name.startswith("sum"):
        return "sum"
    raise ValueError(name)


def forward_values(raw, w, msg):
    m = (1 << w) - 1
    R = T.rots(w)
    val = {f"init{i}": v for i, v in enumerate(T.init_state(w))}
    val.update({f"m{i}": msg[i] for i in range(16)})
    rot = {"d1": R[0], "b1": R[1], "d2": R[2], "b2": R[3]}
    for name, vs in raw:
        k = kind(name)
        o, *a = vs
        if k in ("a1", "a2"):
            val[o] = (val[a[0]] + val[a[1]] + val[a[2]]) & m
        elif k in ("c1", "c2", "sum"):
            val[o] = (val[a[0]] + val[a[1]]) & m
        else:
            val[o] = T.rotr(val[a[0]] ^ val[a[1]], rot[k], w)
    return val


def main():
    variant, w, lt = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    eqs, const, vars_, H, raw = build(variant, "len64", (), want_raw=True)
    rng = random.Random(seed)
    ref = [rng.getrandbits(w) for _ in range(16)]
    val = forward_values(raw, w, ref)
    steps = [ln.split() for ln in open(f"gdv_best_{variant}_len64.txt")]
    R = T.rots(w)
    rot = {"d1": R[0], "b1": R[1], "d2": R[2], "b2": R[3]}
    eq = {name: vs for name, vs in raw}
    idx = {}

    def V(x):
        if x not in idx:
            idx[x] = len(idx)
        return f"v[{idx[x]}]"

    M = f"0x{(1 << w) - 1:x}u"
    lines = []
    for c in sorted(const):
        lines.append(f"  {V(c)} = {val[c]}u;")
    guesses = []
    used = set()
    for st in steps:
        if st[0] == "guess":
            guesses.append(st[1])
            lines.append(f"  {V(st[1])} = rnd() & {M};")
            continue
        name, t = st[1], st[2]
        used.add(name)
        k = kind(name)
        o, *a = eq[name]
        if k in ("a1", "a2"):
            if t == o:
                e = f"({V(a[0])} + {V(a[1])} + {V(a[2])})"
            else:
                rest = [x for x in a if x != t]
                e = f"({V(o)} - {V(rest[0])} - {V(rest[1])})"
        elif k in ("c1", "c2", "sum"):
            e = f"({V(a[0])} + {V(a[1])})" if t == o else f"({V(o)} - {V(a[1] if t == a[0] else a[0])})"
        else:
            r = rot[k]
            if t == o:
                e = f"ROTR({V(a[0])} ^ {V(a[1])}, {r})"
            else:
                e = f"(ROTL({V(o)}, {r}) ^ {V(a[1] if t == a[0] else a[0])})"
        lines.append(f"  {V(t)} = {e} & {M};")
    checks = []
    for name, vs in raw:
        if name in used:
            continue
        k = kind(name)
        o, *a = vs
        if k in ("a1", "a2"):
            e = f"(({V(a[0])} + {V(a[1])} + {V(a[2])}) & {M})"
        elif k in ("c1", "c2", "sum"):
            e = f"(({V(a[0])} + {V(a[1])}) & {M})"
        else:
            e = f"(ROTR({V(a[0])} ^ {V(a[1])}, {rot[k]}) & {M})"
        checks.append(f"{V(o)} == {e}")
    nchk = len(checks)
    src = f"""#include <stdio.h>
#include <stdint.h>
#define W {w}
#define ROTR(z,r) ((((z) >> (r)) | ((z) << (W - (r)))) & {M})
#define ROTL(z,r) ((((z) << (r)) | ((z) >> (W - (r)))) & {M})
static uint64_t s = {seed * 2654435761 + 1}ull;
static inline uint32_t rnd(void) {{ s ^= s << 13; s ^= s >> 7; s ^= s << 17; return (uint32_t)s; }}
int main(void) {{
  static uint32_t v[{len(idx) + 400}];
  long long found = 0;
  for (long long t = 0; t < (1ll << {lt}); t++) {{
{chr(10).join('  ' + ln for ln in lines)}
    if ({' && '.join(checks) if checks else '1'}) {{
      found++;
      if (found <= 20) {{ printf("M"); for (int i = 0; i < 16; i++) printf(" %u", v[IDXM(i)]); printf("\\n"); }}
    }}
  }}
  printf("trials 2^{lt} members %lld checks {nchk}\\n", found);
  return 0;
}}
"""
    for i in range(16):
        V(f"m{i}")
    msgidx = [idx[f"m{i}"] for i in range(16)]
    src = src.replace("v[IDXM(i)]", "v[midx[i]]").replace(
        "int main(void) {", "static const int midx[16] = {" + ",".join(map(str, msgidx)) + "};\nint main(void) {")
    cfn = f"gdnum_{variant}_w{w}.c"
    with open(cfn, "w", newline="\n") as fh:
        fh.write(src)
    print(f"{cfn}: {len(guesses)} guesses, {nchk} check equations; expected members 2^{lt - w * nchk}")
    wd = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/fringe')
    sh = f"gdnum_{variant}_w{w}.sh"
    with open(sh, "w", newline="\n") as fh:
        fh.write(f"#!/bin/bash\ncd {wd}\ngcc -O2 -o gdnum_{variant}_w{w} {cfn} && ./gdnum_{variant}_w{w}\n")
    out = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", f"{wd}/{sh}"], capture_output=True, text=True,
                         timeout=600).stdout
    print(out.strip().splitlines()[-1] if out.strip() else "no output")
    refA = forward_values(build(variant, "len64", (), want_raw=True)[4], w, ref)
    tref = T.trace(ref, w)
    ok = bad = same = moved = 0
    for ln in out.splitlines():
        if not ln.startswith("M "):
            continue
        msg = list(map(int, ln.split()[1:]))
        t = T.trace(msg, w)
        if msg == ref:
            same += 1
            continue
        half_b = variant.endswith("B")
        xw = (12, 15) if half_b else (1, 9)            # E-call x words absorbed with Y1/Y3 or Y0/Y2
        ow = (1, 3, 4, 6) if half_b else (0, 2, 5, 7)
        moved += (msg[xw[0]], msg[xw[1]]) != (ref[xw[0]], ref[xw[1]])
        good = all(t["out"][i] == tref["out"][i] for i in ow)
        mv = forward_values(raw, w, msg)
        good &= all(mv[c] == refA[c] for c in const if not c.startswith("init"))
        ok += good
        bad += not good
    hb = variant.endswith("B")
    print(f"verified with toyb3: {ok} members with equal out{'1,3,4,6' if hb else '0,2,5,7'} and equal family "
          f"constants, {bad} failures, {same} equal to the reference message; {moved} have "
          f"{'(m12, m15)' if hb else '(m1, m9)'} different from the reference, i.e. lie outside the 'fixed' family"
          f"  [COMPUTED]")


if __name__ == "__main__":
    main()
