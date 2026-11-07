"""walk_model.py - the t_hi walk on the shipped front-line construction (research only, nothing filed).

Step CO of pkgCM proof.md Section 8 is taken from the shipped program experiments/frontline.py (its LINES), with ONE
change: the line K1.a1 = ROL(K1.d1,16) becomes K1.a1 = ROL(K1.d1,16) XOR thi, thi = the high counter word v[13].
Step CT is frontline.step_ct; the trial's counter is t = thi * 2^32 + t_lo.  Checks (all against the organizer's
hash-smash/verifier/blake3.py _compress, imported unchanged):
  C1  half-collision (CV words 0,2,5,7 equal) and state consistency (frontline.chart cons) at t = thi*2^32 + t_lo
  C2  C0 and D1 (all their values, Y0 Y4 Y8 Y12 X1 X6 X12 ...) constant along the walk of one (context, y)
  C3  omega = e1 - S0 - S5 + (ROR(X0,16) XOR S15'), X0 = C0.a1 - X4 - w2(thi): closed form vs the lines
  C4  omega mod 2^16 constant on blocks of X0 >> 16; X0 walks an interval of 2^19 values
  C5  the (2)-passing steps of a full block = the inverse images of the listed passing omegas (list method exact)
  C6  which names change along the walk (the per-step lines)
usage: python -B walk_model.py [nsamples] [seed]
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

import importlib.util
import random
import struct
import sys
import time

EXP = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCM/pkg/blake3-r2/experiments')
REF = _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/blake3.py')
sys.path.insert(0, EXP)
import frontline as F  # noqa: E402

spec = importlib.util.spec_from_file_location("b3ref", REF)
B3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B3)

M = 0xFFFFFFFF
ror, rol = F.ror, F.rol

# step CO with the t_hi change: exactly one line differs from the shipped LINES
LINES_W = []
for n, e in F.LINES:
    if n == "K1.a1":
        assert e == F.L("K1.d1", 16)
        e = F.X(F.L("K1.d1", 16), "thi")
    LINES_W.append((n, e))


def ev(e, env):
    if isinstance(e, int):
        return e
    if isinstance(e, str):
        return env[e]
    if e[0] == "sum":
        s = 0
        for t in e[1]:
            s += -ev(t[1], env) if type(t) is tuple and t[0] == "neg" else ev(t, env)
        return s & M
    if e[0] == "xor":
        return ev(e[1], env) ^ ev(e[2], env)
    if e[0] == "ror":
        return ror(ev(e[1], env), e[2])
    raise ValueError(e)


def co_walk(ow, y, thi, fl=F.FLAGS):
    env = dict(zip(F.OUTER_WORDS, ow))
    env.update(Y4=y, fl=fl, thi=thi)
    for n, e in LINES_W:
        env[n] = ev(e, env)
    v = {k.replace(".", "_"): val for k, val in env.items()}
    v["e1"] = (F.Y3 + y) & M
    v["omega"] = (F.Y3 + y + v["w8"]) & M
    return v


def ref_cv(block, t, n):
    words = struct.unpack("<16I", block + bytes(64 - len(block)))
    return B3._compress(B3.IV, words, t, n, 3, 2)[:8]


def qstar(j):
    c, k = F.QSTAR_VALUE, 0
    for i in range(32):
        if not F.QSTAR_MASK >> i & 1:
            c |= (j >> k & 1) << i
            k += 1
    return c


def main():
    ns = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 20261010)
    t0 = time.time()
    # sanity: thi = 0 reproduces the shipped co_full
    for _ in range(20):
        ow = [rng.getrandbits(32) for _ in range(7)]
        e1, y = F.member(rng.getrandbits(19))
        a, b = co_walk(ow, y, 0), F.co_full(*ow, y, F.FLAGS)
        assert all(a[k.replace(".", "_")] == b[k.replace(".", "_")] for k, _ in F.LINES)
    c1_ok = c1_bad = 0
    const_bad = 0
    form_bad = 0
    changed = set()
    C0D1 = ["C0_a1", "C0_b1", "C0_c1", "C0_d1", "Y0", "Y4", "Y8", "Y12", "D1_a1", "D1_b1", "D1_c1", "D1_d1", "X1",
            "X6", "X12", "w10", "w11"]
    tmax = 0
    for s in range(ns):
        ow = [rng.getrandbits(32) for _ in range(7)]
        e1, y = F.member(rng.getrandbits(19))
        base = co_walk(ow, y, 0)
        for r in range(8):
            thi = rng.getrandbits(19) if r else (1 << 19) - 1
            v = co_walk(ow, y, thi)
            for k in C0D1:
                const_bad += v[k] != base[k]
            for k in v:
                if v[k] != base[k]:
                    changed.add(k)
            # C3 closed form of omega
            S15p = v["S15"] ^ ror(F.X15, 8)
            om = (v["e1"] - v["S0"] - v["S5"] + (ror(v["X0"], 16) ^ S15p)) & M
            form_bad += om != v["omega"]
            form_bad += v["X0"] != (v["C0_a1"] - v["X4"] - v["w2"]) & M
            form_bad += v["w2"] != ((rol(v["K1_d1"], 16) ^ thi) - F.IV[1] - F.IV[5]) & M
            # C1 half-collision on the reference at t = thi*2^32 + t_lo
            c1 = qstar(rng.getrandbits(21))
            u = F.step_ct(v, c1)
            t = (thi << 32) | u["t"]
            tmax = max(tmax, t)
            u["t"] = t
            r_ = F.chart(u)
            cva, cvb = ref_cv(u["A"], t, F.LEN_A), ref_cv(u["B"], t, F.LEN_B)
            ok = (r_["cons"] and list(cva) == list(r_["cva"]) and list(cvb) == list(r_["cvb"])
                  and all(cva[i] == cvb[i] for i in (0, 2, 5, 7)) and r_["ea"][2] == c1
                  and (r_["ea"][1] ^ r_["eb"][1]) == F.BETA)
            c1_ok += ok
            c1_bad += not ok
    import math
    print("C1 half-collision + cons + E1.c1 + beta* on the reference, t = thi*2^32 + t_lo: %d ok, %d bad (max t %d = 2^%.6f)"
          % (c1_ok, c1_bad, tmax, math.log2(tmax)))
    print("C2 C0 and D1 values constant along the walk: %d mismatches over %d x 8 x %d names" % (const_bad, ns, len(C0D1)))
    print("C3 omega closed form, X0 and w2 lines: %d mismatches" % form_bad)
    print("C6 names that change along the walk (%d): %s" % (len(changed), " ".join(sorted(changed))))
    # C4, C5 on full walks of a few groups (2^19 steps each), closed form checked against the lines above
    T2 = F.T2
    blk_counts = []
    c5_bad = 0
    for s in range(3):
        ow = [rng.getrandbits(32) for _ in range(7)]
        e1, y = F.member(rng.getrandbits(19))
        v = co_walk(ow, y, 0)
        K1d = v["K1_d1"]
        hi13 = rol(K1d, 16) & ~((1 << 19) - 1) & M
        S15p = v["S15"] ^ ror(F.X15, 8)
        A = (v["e1"] - v["S0"] - v["S5"]) & M
        Cc = (v["C0_a1"] - v["X4"] + F.IV[1] + F.IV[5]) & M  # X0 = Cc - K1.a1
        x0s, blocks = [], {}
        for j in range(1 << 19):
            k1a = hi13 | j
            x0 = (Cc - k1a) & M
            om = (A + (ror(x0, 16) ^ S15p)) & M
            blocks.setdefault(x0 >> 16, set()).add(om & 0xFFFF)
            x0s.append(x0)
        span = (x0s[0] - x0s[-1]) & M
        print("C4 group %d: X0 interval span %d (= 2^19 - 1: %s), %d blocks of X0>>16, omega mod 2^16 values per block %s"
              % (s, span, span == (1 << 19) - 1, len(blocks), sorted(len(b) for b in blocks.values())))
        # C5: list method for every block: passing steps by enumeration vs by inverting listed omegas
        for xh, lows in blocks.items():
            (olo,) = lows
            dlo = (xh ^ S15p) & 0xFFFF
            direct = {x0 for x0 in x0s if x0 >> 16 == xh and T2((A + (ror(x0, 16) ^ S15p)) & M)}
            listed = set()
            for ohi in range(1 << 16):
                om = olo | ohi << 16
                if T2(om):
                    d0a1 = (om - A) & M
                    x0 = rol(d0a1 ^ S15p, 16)
                    if x0 >> 16 == xh and ((Cc - x0) & M) & ~((1 << 19) - 1) & M == hi13:
                        listed.add(x0)
            c5_bad += direct != listed
            blk_counts.append((len(direct), sum(1 for x0 in x0s if x0 >> 16 == xh)))
            assert (A + dlo) & 0xFFFF == olo
    tot_pass = sum(a for a, b in blk_counts)
    tot = sum(b for a, b in blk_counts)
    print("C5 list method = enumeration on %d blocks: %d mismatches; (2)-passing steps %d of %d = %.6f (pi_E %.6f)"
          % (len(blk_counts), c5_bad, tot_pass, tot, tot_pass / tot, F.E_COUNT / 2 ** 32))
    print("seconds %.1f" % (time.time() - t0))


if __name__ == "__main__":
    main()
