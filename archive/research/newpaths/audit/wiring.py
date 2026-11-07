"""Audit step 1: every equation of gd_order.build() must hold on real 2-round BLAKE3 values (ref.py naming),
for both variants and both lengths; the constant sets must be what the variant says.
Equation semantics are taken from the name suffix and the tuple order gd_order uses:
  :a1 (a1,a,b,x) a1=a+b+x   :d1 (d1,d,a1) d1=(d^a1)>>>R0   :c1 (c1,c,d1) c1=c+d1   :b1 (b1,b,c1) b1=(b^c1)>>>R1
  :a2 (a2,a1,b1,y) sum      :d2 (d2,d1,a2) >>>R2          :c2 (c2,c1,d2) sum      :b2 (b2,b1,c2) >>>R3
  outI (s_i, s_{i+8}): s_i ^ s_{i+8} == out_i
"""
import random
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, __file__.rsplit("\\", 1)[0] + "\\orig")
from gd_order import build  # noqa: E402  (unmodified copy of newpaths/gd_order.py)
from ref import trace, ror, rots  # noqa: E402


def eq_holds(name, vs, vals, out, w):
    m = (1 << w) - 1
    R = rots(w)
    x = [vals[v] for v in vs]
    if name.startswith("out"):
        i = int(name[3:])
        return (x[0] ^ x[1]) == out[i]
    t = name.split(":")[1]
    if t in ("a1", "a2"):
        return x[0] == (x[1] + x[2] + x[3]) & m
    if t in ("c1", "c2"):
        return x[0] == (x[1] + x[2]) & m
    r = {"d1": R[0], "b1": R[1], "d2": R[2], "b2": R[3]}[t]
    return x[0] == ror(x[1] ^ x[2], r, w)


def check(variant, length, w, n, rng):
    eqs, const, vars_ = build(variant, length)
    allwords = set(const) | set(vars_)
    fails = {}
    blen = 64 if length == "len64" else 55
    for _ in range(n):
        msg = [rng.getrandbits(w) for _ in range(16)]
        if length == "len55":
            msg[14] = msg[15] = 0
            msg[13] &= (1 << (w - 8)) - 1 if w == 32 else (1 << w) - 1
        vals, Y, out = trace(msg, w, blen=blen if w == 32 else blen & ((1 << w) - 1))
        missing = allwords - set(vals)
        if missing:
            return f"names not produced by ref: {sorted(missing)[:10]}"
        for name, vs in eqs:
            if not eq_holds(name, vs, vals, out, w):
                fails[name] = fails.get(name, 0) + 1
    # structural checks on naming
    lines = [f"{variant} {length} w={w}: {len(vars_)} unknowns, {len(eqs)} equations, freedom {len(vars_) - len(eqs)};"
             f" {n} random messages, failing equations: {fails if fails else 'none'}"]
    # which internal words are constants
    nonmsg_const = sorted(c for c in const if not c.startswith("init"))
    lines.append(f"  constants other than init*: {nonmsg_const}")
    return "\n".join(lines), eqs, const


def main():
    rng = random.Random(7)
    log = []
    for variant in ("fixed", "outhalf"):
        for length in ("len64", "len55"):
            for w in (32, 8):
                r, eqs, const = check(variant, length, w, 300 if w == 32 else 300, rng)
                log.append(r)
    # Y naming: the fixed variant's Y constants must equal Y[i] for i in (0,5,10,15,2,7,8,13) of the reference
    eqs, const, _ = build("fixed", "len64")
    yn = {0: "C0.a2", 5: "C1.b2", 10: "C2.c2", 15: "C3.d2", 2: "C2.a2", 7: "C3.b2", 8: "C0.c2", 13: "C1.d2"}
    bad = 0
    for _ in range(200):
        msg = [rng.getrandbits(32) for _ in range(16)]
        vals, Y, out = trace(msg)
        for i, nm in yn.items():
            bad += vals[nm] != Y[i]
        # E0 / E2 inputs per spec (Y0,Y5,Y10,Y15; m1,m11) and (Y2,Y7,Y8,Y13; m9,m14)
        e0 = (Y[0], Y[5], Y[10], Y[15], msg[1], msg[11])
        e2 = (Y[2], Y[7], Y[8], Y[13], msg[9], msg[14])
        a1 = (e0[0] + e0[1] + e0[4]) & 0xFFFFFFFF
        bad += vals["E0.a1"] != a1
        bad += vals["E2.a1"] != (e2[0] + e2[1] + e2[4]) & 0xFFFFFFFF
        bad += vals["E0.a2"] != (vals["E0.a1"] + vals["E0.b1"] + msg[11]) & 0xFFFFFFFF
        bad += vals["E2.a2"] != (vals["E2.a1"] + vals["E2.b1"] + msg[14]) & 0xFFFFFFFF
        # structural fact used by both variants
        bad += out[0] != vals["E0.a2"] ^ vals["E2.c2"]
        bad += out[2] != vals["E2.a2"] ^ vals["E0.c2"]
        bad += out[5] != vals["E0.b2"] ^ vals["E2.d2"]
        bad += out[7] != vals["E2.b2"] ^ vals["E0.d2"]
    want = {f"init{i}" for i in range(16)} | {"m1", "m11", "m9", "m14"} | set(yn.values())
    log.append(f"fixed: constant set == init* + m1,m11,m9,m14 + Y0,5,10,15,2,7,8,13 named {sorted(yn.values())}: "
               f"{const == want}; value/naming mismatches over 200 messages: {bad}")
    eqs, const, _ = build("outhalf", "len64")
    outs = [vs for n, vs in eqs if n.startswith("out")]
    log.append(f"outhalf: constants are only init*: {const == {f'init{i}' for i in range(16)}}; out equations: {outs}")
    # message permutation: which message word feeds each G slot in round 1
    eqs, _, _ = build("outhalf", "len64")
    slots = {n: vs for n, vs in eqs}
    r1 = []
    for j, call in enumerate(("C0", "C1", "C2", "C3", "E0", "E1", "E2", "E3")):
        if f"{call}:a1" in slots:
            r1.append(f"{call}:x={slots[call + ':a1'][3]},y={slots[call + ':a2'][3]}")
    log.append("round-1 message slots in build(outhalf): " + " ".join(r1))
    txt = "\n".join(log)
    print(txt)
    open(__file__.rsplit("\\", 1)[0] + "\\wiring.log", "w").write(txt + "\n")


if __name__ == "__main__":
    main()
