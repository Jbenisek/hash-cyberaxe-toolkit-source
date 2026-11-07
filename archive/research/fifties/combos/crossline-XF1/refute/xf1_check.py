#!/usr/bin/env python3
"""Independent refutation check of crossline-XF1 (masked partner walk).  CPU, numpy, at most 2 processes.

Independent of XF1's code paths: omega of all 2^19 members by a numpy chain written from the omega-side lines
(spot-checked against F.co_ref, the straight-line step CO); T2 by numpy on F.F2 (spot-checked against F.T2);
alive16 by an exact live-state test on the flat T2 tables (some completion of bits 16..31 gives T2 != 0), not
window14.alive; the carry index by scalar carries, not XF1's packed ix_word; the gate by a vectorised formula
(spot-checked against F.gate).  Only XF1's build_table (the masks and chunks under test) is imported from walk_mask.

  python -B xf1_check.py run LO HI OUT.json     contexts b"xf1-refute-%04d", i = LO..HI-1
  python -B xf1_check.py price OUT1.json ...    reprice from frontline_full constants (own formula) + sweep stats
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

import sys, json, math, time, hashlib, struct, random
import numpy as np
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCJ/work'))
import frontline_full as F

M = 0xFFFFFFFF
U64 = np.uint64


def rol(x, r):
    return ((x << U64(r)) | (x >> U64(32 - r))) & U64(M)


def srol(v, r):
    return ((v << r) | (v >> (32 - r))) & M


# ---- universal member arrays (context-free) ---------------------------------------------------------------------------
G_ = np.arange(1 << 14, dtype=np.int64)[:, None]
J_ = np.arange(32, dtype=np.int64)[None, :]
KK = (G_ & 63) | (J_ << 6) | ((G_ >> 6) << 11)
SPL = np.array(F.SPL, dtype=np.uint64)
SPH = np.array(F.SPH, dtype=np.uint64)
E1 = U64(F.CLASS_VALUE) | SPL[KK & 1023] | SPH[KK >> 10]          # (16384, 32)
Y = (E1 - U64(F.Y3)) & U64(M)
UU = rol(Y, 7)
# sanity against F.cmember on a sample
for _g, _j in [(0, 0), (5, 31), (16383, 17), (1234, 9)]:
    assert (int(E1[_g, _j]), int(Y[_g, _j])) == F.cmember(_g, _j)[:2]
# 2.1 / pack: rol(y_j,7) = rol(y_0,7) + (j << 17) with no wrap, e1_j = e1_0 + (j << 10), for every member
PACK_BAD = int(np.sum((UU != UU[:, :1] + (J_.astype(np.uint64) << U64(17))) |
                      (E1 != E1[:, :1] + (J_.astype(np.uint64) << U64(10)))))

F2 = np.array(F.F2, dtype=np.int64)


def T2v(x):
    x = x.astype(np.int64)
    return F2[F2[F2[F2[x & 255] + (x >> 8 & 255)] + (x >> 16 & 255)] + (x >> 24)]


# exact alive16: the state after the two low bytes has some completion of bits 16..31 with T2 != 0
_x16 = np.arange(1 << 16, dtype=np.int64)
_s2 = F2[F2[_x16 & 255] + (_x16 >> 8)]
_live = {}
_ar = np.arange(256, dtype=np.int64)
for s in np.unique(_s2):
    s3 = F2[s + _ar]
    _live[int(s)] = bool(np.any(F2[s3[:, None] + _ar[None, :]] != 0))
AL16X = np.array([_live[int(s)] for s in _s2], dtype=bool)
S7 = F.S7
S7A = np.array([S7 >> i & 1 for i in range(128)], dtype=np.int64)
OLD_B = [sum(1 << j for j in range(a, min(a + 7, 32))) for a in range(1, 32, 7)]   # today's five partner batches
W2 = np.array([1 << j for j in range(32)], dtype=np.int64)[None, :]


def bits(boolarr):
    return (boolarr.astype(np.int64) * W2).sum(axis=1)


def popcnt(a):
    return np.array([bin(int(v)).count("1") for v in a], dtype=np.int64)


def context(seed, X, rnd):
    sh = hashlib.shake_256(b"frontline context" + seed).digest(160)
    ow = struct.unpack("<7I", sh[:28])
    cx = F.co_ctx(*ow, F.FLAGS)
    b1, c1, d1 = cx["C0_b1"], cx["C0_c1"], cx["C0_d1"]
    A = (cx["C0_b1"] + cx["w6"] + cx["X4"] + cx["w2"]) & M
    S15, nSS = cx["S15"], -(cx["S0"] + cx["S5"]) & M
    nc1, Ap = -c1 & M, -A & M
    Y8 = UU ^ U64(b1)
    Y12 = (Y8 + U64(nc1)) & U64(M)
    Y0 = rol(Y12, 8) ^ U64(d1)
    X0 = (Y0 + U64(Ap)) & U64(M)
    D0d1 = X0 ^ U64(srol(F.X15, 8))
    D0a1 = rol(D0d1, 16) ^ U64(S15)
    w8 = (D0a1 + U64(nSS)) & U64(M)
    om = (E1 + w8) & U64(M)
    r = dict(coref_bad=0, t2_bad=0, gate_bad=0)
    for _ in range(64):                                      # straight-line reference and table spot checks
        g, j = rnd.randrange(1 << 14), rnd.randrange(32)
        rom = F.co_ref(*ow, int(Y[g, j]), F.FLAGS)[0]
        r["coref_bad"] += rom != int(om[g, j])
        r["t2_bad"] += F.T2(rom) != int(T2v(np.array([rom]))[0])
    t2 = T2v(om) != 0                                        # (16384, 32)
    om16 = (om & U64(0xFFFF)).astype(np.int64)
    a16x = AL16X[om16]
    a16w = X.AL16_NP[om16]
    # representative words
    e0, y80, y00, d0a10, w80, om0 = (a[:, 0].astype(np.int64) for a in (E1, Y8, Y0, D0a1, w8, om))
    a = ((y00 >> 16) - (A >> 16)) & 127
    c = (e0 + nSS) & 127
    q = (srol(F.X15, 24) ^ S15) & 127
    opened = (S7A[((a ^ q) + c) & 127] | S7A[((((a - 1) & 127) ^ q) + c) & 127]) == 1
    for _ in range(64):
        g = rnd.randrange(1 << 14)
        key = int(a[g]) | int(c[g]) << 7
        r["gate_bad"] += bool(F.gate(q << 14 | key)) != bool(opened[g])
    fired = ((y00 >> 8) & 255) == (A >> 8 & 255)
    bin10 = ((e0 & 0x3FF) < (F.Y3 & 0x3FF)).astype(np.int64)
    c17 = ((y80 & 0x1FFFF) + (nc1 & 0x1FFFF)) >> 17 & 1
    c25 = ((y00 & 0x1FFFFFF) + (Ap & 0x1FFFFFF)) >> 25 & 1
    c9a = ((d0a10 & 511) + (nSS & 511)) >> 9 & 1
    c9b = ((e0 & 511) + (w80 & 511)) >> 9 & 1
    idx = bin10 | c17 << 1 | c25 << 2 | c9a << 3 | c9b << 4 | (om0 >> 8 & 1) << 5 | S7A[om0 & 127] << 6
    # XF1's table for this context (the object under test)
    v = F.rebuild(ow, *F.member(0)[::-1])
    masks, chunks, tops, perm_ok = X.build_table(v, (v["C0_b1"] + v["w6"] + v["X4"] + v["w2"]) & M)
    MK = np.array(masks, dtype=np.int64)
    CH1 = np.array([sum(1 << j for j in ch[0][0]) if len(ch) > 0 else 0 for ch in chunks], dtype=np.int64)
    CH2 = np.array([sum(1 << j for j in ch[1][0]) if len(ch) > 1 else 0 for ch in chunks], dtype=np.int64)
    N1 = np.array([len(ch[0][0]) if len(ch) > 0 else 0 for ch in chunks], dtype=np.int64)
    N2 = np.array([len(ch[1][0]) if len(ch) > 1 else 0 for ch in chunks], dtype=np.int64)
    NCH = np.array([len(ch) for ch in chunks], dtype=np.int64)
    chunk_bad = sum(int((CH1[i] | CH2[i]) != (masks[i] & ~1) or (CH1[i] & CH2[i]) or len(chunks[i]) > 2
                        or any(len(p) > 7 or len(p) < 1 for p, _, _ in chunks[i])) for i in range(128))
    t2m, a16xm, a16wm = bits(t2), bits(a16x), bits(a16w)
    mk = MK[idx]
    quiet = opened & ~fired
    fo = sum(((t2m & b) != 0).astype(np.int64) for b in OLD_B)
    fn = np.where(fired, fo, ((t2m & CH1[idx]) != 0).astype(np.int64) + ((t2m & CH2[idx]) != 0))
    pre_const = np.all((om & U64(511)) == (om[:, :1] & U64(511)), axis=1)
    part = lambda n: np.where(n == 0, 0, np.where(n > 3, F.U_PART, F.U_PART_TAIL) + X.X_CHUNK)
    u_new = np.where(fired, X.U_FALLBACK, F.U_REP_T2 + F.U_NEST + X.X_IDX + X.X_GUARD
                     + np.where(NCH[idx] > 0, X.X_BCAST, 0) + part(N1[idx]) + part(N2[idx]))
    # rep-batch fills (identical in both layouts): a rep batch fills once if an opened rep lane has T2 != 0
    rf = (opened & t2[:, 0]).astype(np.int64)
    rep_fills = int(np.sum(np.add.reduceat(rf, np.arange(0, 1 << 14, 7)) > 0))
    pc = popcnt(mk[quiet] & ~1)
    r.update(
        opened=int(opened.sum()), fired_all=int(fired.sum()), fallback=int((opened & fired).sum()),
        lost=int(popcnt(t2m[quiet] & ~mk[quiet]).sum()),
        lost_fired_if_masked=int(popcnt(t2m[opened & fired] & ~mk[opened & fired]).sum()),
        mis_exact_alive16=int(np.sum(a16xm[quiet] != mk[quiet])),
        mis_window14_alive16=int(np.sum(a16wm[quiet] != mk[quiet])),
        prefix_split_quiet=int(np.sum(~pre_const[quiet])),
        t2_outside_exact_alive16=int(np.sum(t2 & ~a16x)),
        fills_old=int(fo[opened].sum()) + rep_fills, fills_new=int(fn[opened].sum()) + rep_fills,
        fill_dom_viol=int(np.sum(fn[opened] > fo[opened])),
        units_old=int(opened.sum()) * F.U_OPEN, units_new=int(u_new[opened].sum()),
        u_new_max=int(u_new[quiet].max()) if quiet.any() else 0,
        table_ops=tops, perm_ok=int(perm_ok), chunk_bad=chunk_bad,
        partner_surv_max=int(pc.max()) if len(pc) else 0,
        surv_hist={int(k): int(n) for k, n in zip(*np.unique(popcnt(mk[quiet]), return_counts=True))},
        e_members_opened=int(t2[opened].sum()))
    return r


def run(lo, hi, out):
    sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/combos/crossline-XF1'))
    import walk_mask as X
    X.AL16_NP = np.frombuffer(bytes(X.AL16), dtype=np.uint8).astype(bool)
    t0, per = time.time(), []
    rnd = random.Random(lo)
    for i in range(lo, hi):
        r = context(b"xf1-refute-%04d" % i, X, rnd)
        r["i"] = i
        per.append(r)
        json.dump(dict(range=[lo, i + 1], pack_bad_universal=PACK_BAD, seconds=round(time.time() - t0, 1),
                       per_context=per), open(out, "w"), indent=0)
        print("ctx %d opened %d fired %d fb %d lost %d mis %d/%d fills %d->%d u %.1f %.0fs" % (
            i, r["opened"], r["fired_all"], r["fallback"], r["lost"], r["mis_exact_alive16"],
            r["mis_window14_alive16"], r["fills_old"], r["fills_new"], r["units_new"] / max(1, r["opened"]),
            time.time() - t0), flush=True)


def price(files):
    N0 = ((F.U_REP * (F.REP_BATCHES - 1) + F.U_REP_TAIL) * F.RUN_CONTEXTS + F.U_OPEN * (F.A_BUDGET + 1)
          + F.U_CONTEXT * (F.RUN_CONTEXTS + 1) + F.U_E * (F.E_BUDGET + 1) + F.U_FILL * (F.G_BUDGET + 1)
          + F.U_PASS * (F.PASS_BUDGET + 1) + F.CREDIT + F.ONCE + 16 * 2 ** 20 + 2 ** 27 + 2 ** 34 + F.S_OLD
          + 430 * 2 ** 38)
    out = ["own N recomputed %d; equals F.N %s; equals TEXT N %s" % (N0, N0 == F.N, N0 == F.TEXT["N"])]
    A1, K1 = F.A_BUDGET + 1, F.RUN_CONTEXTS + 1
    lg = lambda n: math.log2(n / 430)
    out.append("baseline time_log2 %.6f" % lg(N0))
    # XF1's charges, recounted: build_table loop counts and the explicit operation lists
    tfix = 20 + 32 * 3 + 2 * 32 * 7 + 2 * 32 * 2 * 6 + 2 * 32 * 4 * 6 + 2 * 32 * 8 * 6 + 2 * 32 * 16 * 5 + 2 * 32 * 32 * 6
    tmax = tfix + 64 * 21 + 64 * 9 * 17
    u_mask = 6 + 56 + 16 + 4 + 6 + 2 * (66 + 8)
    per_ctx = tmax + 19 * 2341 + 128 * (368 + 16 + 4 - u_mask)
    out.append("table max %d, U_mask %d, per-context %d" % (tmax, u_mask, per_ctx))

    def row(u, pc, once=2 ** 20):
        return lg(N0 - 368 * A1 + u * A1 + pc * K1 + once)
    t = row(u_mask, per_ctx)
    out.append("KEY: XF1 decision row reproduced: time_log2 %.6f (claimed 63.313775; diff %.2e)" % (t, t - 63.313775))
    out.append("sensitivity (DERIVED corrections not in XF1's ledger):")
    for lab, du, dpc in (("+8/opened: two more frame words (IX, guard word) at 4 units each", 8, 0),
                         ("+12/opened: broadcast by shifts/ORs (no multiply on the 6.5 machine), 7 ops per word", 12, 0),
                         ("+8 +12 +4 const loads per opened, table x2", 24, tmax),
                         ("+40/opened, +50,000/context (XF1 stress)", 40, 50000),
                         ("+73/opened (XF1 break-even)", 73, 0)):
        out.append("  %-80s %.6f" % (lab, row(u_mask + du, per_ctx + dpc)))
    if files:
        per = []
        hdr = {}
        for f in files:
            d = json.load(open(f))
            per += d["per_context"]
            hdr[f] = d["pack_bad_universal"]
        n = len(per)
        S = lambda k: sum(c[k] for c in per)
        out.append("")
        out.append("SWEEP: %d contexts; pack_bad (universal, all 2^19 members) %s" % (n, sorted(set(hdr.values()))))
        for k in ("opened", "fired_all", "fallback", "lost", "lost_fired_if_masked", "mis_exact_alive16",
                  "mis_window14_alive16", "prefix_split_quiet", "t2_outside_exact_alive16", "fill_dom_viol",
                  "chunk_bad", "coref_bad", "t2_bad", "gate_bad", "e_members_opened"):
            out.append("  %-26s %d" % (k, S(k)))
        out.append("  fired_all values: %s; perm_ok %d of %d; partner survivors max %d; table ops max %d" % (
            sorted({c["fired_all"] for c in per}), S("perm_ok"), n, max(c["partner_surv_max"] for c in per),
            max(c["table_ops"] for c in per)))
        hist = {}
        for c in per:
            for k, v in c["surv_hist"].items():
                hist[k] = hist.get(k, 0) + v
        op = S("opened")
        um = S("units_new") / op
        out.append("  opened/context %.1f (budget A/K %.1f); fallback share %.5f; survivors hist %s" % (
            op / n, F.A_BUDGET / F.RUN_CONTEXTS, S("fallback") / op, hist))
        out.append("  units per opened: old %.2f, new mean %.2f, new max (quiet) %d" % (
            S("units_old") / op, um, max(c["u_new_max"] for c in per)))
        fo, fnw = [c["fills_old"] for c in per], [c["fills_new"] for c in per]
        out.append("  fills/context old %.1f (premise 12466), new %.1f; contexts new > old: %d" % (
            sum(fo) / n, sum(fnw) / n, sum(b > a for a, b in zip(fo, fnw))))
        out.append("  information: row at measured mean %.2f: %.6f" % (um, row(um, per_ctx)))
    return out


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    else:
        o = price(sys.argv[2:])
        print("\n".join(o))
        open(_hca_public_path_text('__HCA_WORKSPACE__/research/fifties/combos/crossline-XF1/refute/price_out.txt'),
             "w").write("\n".join(o) + "\n")
