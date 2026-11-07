"""upfront-G50-Y1: the yield4_seed contexts with the REAL CK2 opening gate, exact full-class counts, and the solver.

Same rng consumption as yield4_seed.py (sample 2^15, pilot 1024, then 7 words per context), so contexts c of a
seed are the same contexts as in check/run_s<seed>.txt.  Per context, over the whole 2^19-member class:
  opened   clusters whose representative opens F.gate (key built as walk() builds it, lines 1171-1174, 1254, 1261)
  hits     members with T2(omega) != 0              (= E lanes; yield4_seed "hits")
  passes   members with T1(Y9) & T2(omega) != 0     (joint passes; exact, not a sample)
  calls    passes with T = x & VMASK[nu] != 0       (T-nonzero solver calls)
  fills    G_cluster: used CK2 batches (rep batches + 5 partner batches of each opened cluster) with an E lane
  pilot    T2 hits on the 1024 pilot members (yield4_seed "pilot")
  spass    joint passes on the 2^15 sample (yield4_seed "passes")
and the solver F.solve(rebuild, rows_of(T), G15) on every call: roots, leaves, ledger units U, metered debit,
and the CF 6 predicate pieces of every root.
Checks: vector omega/Y9/C2 vs F.co_full; vector T1/T2 vs F.T1/F.T2; vector gate vs F.gate and vs F.prefixes
(either 9-bit prefix mod 128 in S7); closed cluster => no T2-positive member; columns vs the baseline run file.
usage: python screen_ck2.py SEED CTX
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

import json
import os
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCJ/work'))
import frontline_full as F  # noqa: E402

M = F.M
U64 = np.uint64
SEED, CTX = int(sys.argv[1]), int(sys.argv[2])
NCHECK = int(sys.argv[3]) if len(sys.argv) > 3 else 16      # contexts with the scalar gate/prefix cross-check

# ---- member arrays (member number k, Section 8 mapping, same as outer.member_y / F.member) ----
KK = np.arange(1 << 19, dtype=np.uint64)
SPL = np.array(F.SPL, dtype=np.uint64)
SPH = np.array(F.SPH, dtype=np.uint64)
E1 = U64(F.CLASS_VALUE) | SPL[KK & U64(1023)] | SPH[KK >> U64(10)]
YY = (E1 - U64(F.Y3)) & U64(M)

# ---- step CO restricted to what we need, compiled for numpy arrays ----
NEED = F.closure(["Y9", "w8", "C2.c1", "C2.b1", "Y0"])
LINES = [n for n, _ in F.LINES if n in NEED]
RET = "Y0, w8, Y9, C2_c1, C2_b1, C0_b1, C0_c1, C0_d1, w6, X4, w2, S0, S5, S15"
vecf = F.compile_lines("vecf", F.ARGS + ["Y4", "fl"], LINES, RET)

F1A = np.array(F.F1, dtype=np.int64)
F2A = np.array(F.F2, dtype=np.int64)
VMASK = np.array(F.VMASK, dtype=np.int64)
S7A = np.array([F.S7 >> i & 1 for i in range(128)], dtype=np.int64)


def tlook(f, x):
    x = x.astype(np.int64)
    s = f[x & 255]
    s = f[s + (x >> 8 & 255)]
    s = f[s + (x >> 16 & 255)]
    return f[s + (x >> 24)]


# cluster layout: k = g & 63 | j << 6 | (g >> 6) << 11  ->  reshape (256, 32, 64) = [g >> 6, j, g & 63]
G_IDX = np.arange(1 << 14, dtype=np.int64)
K_REP = (G_IDX & 63) | ((G_IDX >> 6) << 11)
PBATCH = [(1, 8), (8, 15), (15, 22), (22, 29), (29, 32)]

rng = random.Random(SEED)
sample = np.array([rng.randrange(1 << 19) for _ in range(1 << 15)], dtype=np.int64)
pilot = np.array([rng.randrange(1 << 19) for _ in range(1024)], dtype=np.int64)

rows, chk = [], dict(vec_mm=0, vec_n=0, t_mm=0, t_n=0, gate_mm=0, pref_mm=0, gate_n=0, closed_hits=0,
                     rebuild_mm=0, notes=0)
t0 = time.time()
for c in range(CTX):
    ow = [rng.getrandbits(32) for _ in range(7)]
    Y0, w8, Y9, C2c, C2b, C0b1, C0c1, C0d1, w6, X4, w2, S0, S5, S15 = vecf(*ow, YY, F.FLAGS)
    om = (U64(F.Y3) + YY + w8) & U64(M)
    m2 = tlook(F2A, om)
    m1 = tlook(F1A, Y9)
    x = m1 & m2
    # nu_of(Q=Y9, e1, C=C2_c1, B=C2_b1)
    Q = Y9.astype(np.int64)
    e1i = E1.astype(np.int64)
    r = (((Q >> 16) ^ e1i) & 4) ^ 7
    nu = ((((r + C2c.astype(np.int64)) & M) ^ C2b.astype(np.int64)) ^ 1) & 7
    T = x & VMASK[nu]

    # ---- real CK2 gate on the 16384 representatives (walk lines 1171-1174, 1254, 1261) ----
    A = (C0b1 + w6 + X4 + w2) & M
    nA = (-(A >> 16)) & 127
    P15 = (-(S0 + S5)) & M
    q = (F.rol(F.X15, 24) ^ S15) & 127
    y0r = Y0[K_REP].astype(np.int64)
    a = ((y0r >> 16 & 127) + nA) & 127
    cc = (e1i[K_REP] + P15) & 127
    opened = (S7A[((a ^ q) + cc) & 127] | S7A[((((a - 1) & 127) ^ q) + cc) & 127]).astype(bool)

    E = (m2 != 0).reshape(256, 32, 64).transpose(0, 2, 1).reshape(1 << 14, 32)    # [cluster g, j]
    clusterE = E.any(axis=1)
    chk["closed_hits"] += int((clusterE & ~opened).sum())
    repE = E[:, 0] & opened
    pad = np.zeros(7 * 2341, dtype=bool)
    pad[:1 << 14] = repE
    g_rep = int(pad.reshape(2341, 7).any(axis=1).sum())
    g_part = int(sum((E[:, lo:hi].any(axis=1) & opened).sum() for lo, hi in PBATCH))

    # ---- scalar cross-checks ----
    rs = random.Random(SEED * 1000 + c)
    for _ in range(32):
        kk = rs.randrange(1 << 19)
        e1s, ys = F.member(kk)
        v = F.rebuild(tuple(ow), ys, e1s)
        chk["vec_n"] += 1
        chk["vec_mm"] += (v["omega"], v["Y9"], v["C2_c1"], v["C2_b1"], v["Y0"]) != (
            int(om[kk]), int(Y9[kk]), int(C2c[kk]), int(C2b[kk]), int(Y0[kk]))
        chk["t_n"] += 1
        chk["t_mm"] += (F.T2(v["omega"]), F.T1(v["Y9"])) != (int(m2[kk]), int(m1[kk]))
    if c < NCHECK:
        e1s, ys = F.member(0)
        v = F.rebuild(tuple(ow), ys, e1s)
        cw = (v["C0_b1"], v["C0_c1"], v["C0_d1"], v["C0_b1"] + v["w6"] + v["X4"] + v["w2"] & M,
              F.rol(F.X15, 24) ^ v["S15"], v["S0"] + v["S5"])
        Pq = ((F.rol(F.X15, 24) ^ v["S15"]) & 127) << 14
        nAs = (-((v["C0_b1"] + v["w6"] + v["X4"] + v["w2"] & M) >> 16)) & 127
        Pc = (-(v["S0"] + v["S5"])) & M
        for g in range(1 << 14):
            e1g, yg, kg = F.cmember(g, 0)
            Y0g = int(Y0[kg])
            key = ((Y0g >> 16 & 127) + nAs & 127) | ((e1g + Pc) & 127) << 7
            gs = F.gate(Pq | key)
            W = F.prefixes(cw, yg, e1g)
            ps = int(any(F.S7 >> (w & 127) & 1 for w in W))
            chk["gate_n"] += 1
            chk["gate_mm"] += gs != int(opened[g])
            chk["pref_mm"] += ps != int(opened[g])
            chk["pref_dead_gate_open"] = chk.get("pref_dead_gate_open", 0) + (ps == 0 and gs == 1)
            chk["pref_alive_gate_closed"] = chk.get("pref_alive_gate_closed", 0) + (ps == 1 and gs == 0)

    # ---- solver on every T-nonzero pass of the full class ----
    calls = np.nonzero(T)[0]
    sol = dict(calls=0, roots=0, leaves=0, units=0, debit=0, p_t=0, p_q=0, p_a=0, p_c=0, p_full=0,
               rows=0)
    for kk in calls:
        kk = int(kk)
        e1s, ys = int(E1[kk]), int(YY[kk])
        v = F.rebuild(tuple(ow), ys, e1s)
        chk["rebuild_mm"] += (v["omega"], v["Y9"]) != (int(om[kk]), int(Y9[kk]))
        Tk = int(T[kk])
        rws = F.rows_of(Tk)
        Aunits = F.U_GLOBAL + F.U_FAMILY * F.families(rws) + F.U_ROW * len(rws)
        cnt, notes = [0] * 8, []
        roots = F.solve(v, rws, True, cnt, notes)
        chk["notes"] += len(notes)
        sol["calls"] += 1
        sol["rows"] += len(rws)
        sol["roots"] += len(roots)
        sol["leaves"] += cnt[6]
        sol["debit"] += Aunits + 1 + cnt[7]
        sol["units"] += (Aunits + F.U_FORCED * cnt[0] + F.U_SELECTED * cnt[1] + F.U_G15 * cnt[2]
                         + F.U_FREE * cnt[4] + F.U_LEAF * cnt[6] + F.U_ROOT * len(roots))
        for h, tau in roots:
            t, cv, av, bv, sv, dv, zv = F.pvals(v, h)
            pt = t != 0
            pq = cv & F.QSTAR_MASK == F.QSTAR_VALUE
            pa = F.test_a(av, sv, tau)
            pc = F.test_c(cv, zv, tau)
            sol["p_t"] += pt
            sol["p_q"] += pq
            sol["p_a"] += pa
            sol["p_c"] += pc
            sol["p_full"] += pt and pq and pa and pc

    row = dict(c=c, ow=ow, opened=int(opened.sum()), opened_with_E=int(clusterE.sum()),
               s7_low7_reps=int(S7A[(om[K_REP].astype(np.int64)) & 127].sum()), hits=int((m2 != 0).sum()), passes=int((x != 0).sum()),
               fills=g_rep + g_part, fills_rep=g_rep, fills_part=g_part,
               pilot=int((m2[pilot] != 0).sum()), spass=int((x[sample] != 0).sum()),
               pilot_pass=int((x[pilot] != 0).sum()), **sol)
    rows.append(row)
    print("c", c, "opened", row["opened"], "hits", row["hits"], "passes", row["passes"], "calls", row["calls"],
          "roots", row["roots"], "fills", row["fills"], "pilot", row["pilot"], "spass", row["spass"],
          "sec", round(time.time() - t0, 1), flush=True)

print("checks", chk)
print("sec", round(time.time() - t0, 1))
with open(os.path.join(HERE, "rows_s%d.json" % SEED), "w") as fh:
    json.dump(dict(seed=SEED, ctx=CTX, checks=chk, rows=rows), fh)
