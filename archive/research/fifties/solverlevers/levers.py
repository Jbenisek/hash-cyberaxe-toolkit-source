#!/usr/bin/env python3
"""levers.py (research only) - two solver levers measured on real PC steps (pass + pre-check).
(a) in-traversal c1 guards (G7-style, no c1 enumeration): c1 = Y11 + ROR((ROR(((ROL(h,16)^e1)+C)^B,7)+Y1+w12)^Y12,16).
    After h bits 0..j+7 are decided, c1 bits 16..j are exact once the carry into c1[16] is fixed by Q*
    (c1[16]=0; with Y11[15]=0, Q* c1[15]=1 forces that carry to 0). Checks: Q16 at node 24 (carry = 0),
    Q19 at node 27 (c1[19]=0), HA at node 30 (c1[20]!=c1[22]). Units saved = units of nodes/leaves that a check kills.
(b) Y9 score (exact J1 count = Delta f1 DP of newpaths/hotspot/followup.py dp_y9) on PC steps and on root steps.
usage: python3 levers.py OUT.json [procs]"""
import json, os, struct, sys, time
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, "..", ".."))
IMPL = os.path.join(RES, "impl")
RDIR = os.path.join(IMPL, "memberloop", "roots")
sys.path.insert(0, IMPL)
import outer as O  # noqa
import solver as SV  # noqa
import search as S  # noqa

M = 0xFFFFFFFF
Y11 = O.Y11
CHK16 = ((Y11 >> 15) & 1) == 0
TAUS14 = [0x175020a0, 0x175060a0, 0x185020a0, 0x185060a0, 0x275020a0, 0x275060a0, 0x285020a0, 0x285060a0,
          0x385020a0, 0x385060a0, 0x675020a0, 0x675060a0, 0x685020a0, 0x685060a0]
THETA = lambda t: SV.rol(t ^ SV.ror(t, 1), 12)
HOT_TARGETS = sorted({THETA(t) for t in TAUS14})
S_THETAS = [THETA(t) for t in SV.S_TAUS]
CFGS = {"Q16": 1, "Q19": 2, "HA": 4, "Q16+Q19": 3, "all": 7}
_T = None


def init():
    global _T
    _, t1, t2 = O.build_tables()
    _T = (t1, t2)
    SV.arrays()


def j1_count(Q, T):
    cnt = [1, 0, 0, 0]
    for i in range(32):
        x, e, t = (Q >> i) & 1, (SV.ETA >> i) & 1, (T >> i) & 1
        new = [0, 0, 0, 0]
        for st in range(4):
            n = cnt[st]
            if not n:
                continue
            c, cb = st >> 1, st & 1
            if e ^ c ^ cb != t:
                continue
            for yv in (0, 1):
                yb = yv ^ e
                nc = (x & yv) | (x & c) | (yv & c)
                ncb = (x & yb) | (x & cb) | (yb & cb)
                new[2 * nc + ncb] += n
        cnt = new
    return sum(cnt)


def c1_hi(pref, g):
    y14 = SV.rol(pref, 16) ^ g[0]
    s = ((y14 + g[1]) & M) ^ g[2]
    a1 = (SV.ror(s, 7) + g[3]) & M
    d1 = SV.ror(a1 ^ g[4], 16)
    cc16 = ((d1 >> 16) ^ (Y11 >> 16)) & 1          # carry into c1[16] that gives c1[16] = 0
    return cc16, ((Y11 >> 16) + (d1 >> 16) + cc16) & 0xFFFF   # c1 bits 16..31


def check(i, pref, g):
    cc16, hi = c1_hi(pref, g)
    if i == 24:
        return 1 if (CHK16 and cc16) else 0
    if i == 27:
        return 2 if (hi >> 3) & 1 else 0
    if i == 30:
        return 4 if (((hi >> 4) ^ (hi >> 6)) & 1) == 0 else 0
    return 0


def c1_full(v, h):
    y14 = SV.rol(h, 16) ^ ((O.Y3 + v["Y4"]) & M)
    y6 = SV.ror(((y14 + v["C2.c1"]) & M) ^ v["C2.b1"], 7)
    return (Y11 + SV.ror(((y6 + v["Y1"] + v["w12"]) & M) ^ v["Y12"], 16)) & M


def traverse_g(row, Q, y, E, Ep, kappa, e1, h, states, cnt, g, acc, v, vc):
    u = SV.bit(e1, 21)
    free = set(row.free_positions(True))
    keys = {}
    for i in range(7, 32):
        keys[i] = SV.descriptor(row, Q, y, E, Ep, kappa, i, 1, h[i]) if i in h else \
            SV.descriptor(row, Q, y, E, Ep, kappa, i, 0, 0)
    pref0 = 0
    for i in range(7):
        pref0 |= h[i] << i
    roots = []
    stack = [(7, uu, aa, pref0, 0, 0) for (uu, aa) in states]
    while stack:
        i, uu, aa, pref, e29, fm = stack.pop()
        if i in (24, 27, 30):
            fm |= check(i, pref, g)
        if i == 32:
            cnt["leaves"] += 1
            isr = SV.is_joint_root(Q, y, E, pref, row.tau)
            unit = SV.U_LEAF + (SV.U_ROOT if isr else 0)
            if isr:
                cnt["roots"] += 1
                roots.append(pref)
            acc["leaf_units"] += unit
            for k, c in CFGS.items():
                if fm & c:
                    acc["saved"][k] += unit
                    acc["saved_leaves"][k] += 1
            # validation on every leaf
            ff = check(24, pref, g) | check(27, pref, g) | check(30, pref, g)
            vc["leaves"] += 1
            vc["path_vs_full_mismatch"] += ff != fm
            c1 = c1_full(v, pref)
            vc["c1_vs_search_mismatch"] += c1 != S.c1_of(v, pref)
            keep_req = ((c1 >> 15) & 3) == 1 and ((c1 >> 19) & 1) == 0 and ((c1 >> 20) ^ (c1 >> 22)) & 1
            vc["leaves_keep_required"] += bool(keep_req)
            vc["keep_required_but_killed"] += bool(keep_req and fm)
            full = (c1 & S.CTR_MASK) == S.CTR_VALUE and ((c1 >> 11) ^ (c1 >> 12)) & 1 and ((c1 >> 20) ^ (c1 >> 22)) & 1
            vc["leaves_qstar_ha"] += bool(full)
            vc["qstar_ha_killed"] += bool(full and fm)
            if isr:
                vc["roots"] += 1
                vc["roots_killed_all"] += bool(fm & 7)
                vc["roots_killed_Q"] += bool(fm & 3)
                vc["roots_qstar"] += (c1 & S.CTR_MASK) == S.CTR_VALUE
                vc["roots_qstar_ha"] += bool(full)
                vc["roots_qstar_ha_killed"] += bool(full and fm)
            continue
        cp = (uu << 1) | aa
        if i in free:
            cnt["free"] += 1
            unit = SV.U_FREE
            w = SV.DUAL[(keys[i] << 2) | cp]
            arcs = [w & 0x1F, (w >> 5) & 0x1F]
        else:
            cnt["forced"] += 1
            unit = SV.U_FORCED
            if i == 20:
                cnt["selected"] += 1
                unit += SV.U_SELECTED_EXTRA
                want = SV.bit(pref, 8)
                arcs = [SV.SELECTED[(((keys[i] << 2) | cp) << 1) | want]]
            elif i == 25 or i == 29:
                gv = (SV.bit(pref, 6) ^ SV.bit(pref, 13) ^ u) if i == 25 else (1 ^ e29)
                key = keys[i] | (1 << 3) | (gv << 2)
                arcs = [SV.FORCED[(key << 2) | cp]]
            else:
                arcs = [SV.FORCED[(keys[i] << 2) | cp]]
        acc["node_units"] += unit
        if i >= 24:
            acc["node_units_ge24"] += unit
        for k, c in CFGS.items():
            if fm & c:
                acc["saved"][k] += unit
        for arc in arcs:
            if not arc:
                continue
            vb = (arc >> 1) & 1
            ne29 = (arc & 1) if i == 9 else e29
            stack.append((i + 1, (arc >> 3) & 1, (arc >> 2) & 1, pref | (vb << i), ne29, fm))
    return roots


def static_cap(rows):
    if not rows:
        return 0
    tr = [SV.ROWS[t].static_tree(True) for t in rows]
    F = len({SV.ROWS[t].family for t in rows})
    return (SV.U_STEP + SV.U_FAMILY * F + SV.U_ROW_G7 * len(rows) +
            sum(SV.U_FORCED * x["forced"] + SV.U_FREE * x["free_nodes"] + SV.U_SELECTED_EXTRA * x["selected"] +
                (SV.U_LEAF + SV.U_ROOT) * x["leaves"] for x in tr))


def step(eight):
    t1, t2 = _T
    v = O.scalar_outer(eight)
    Q, y, E, e1, C, B = v["Y9"], v["Y4"], v["omega"], v["e1"], v["C2.c1"], v["C2.b1"]
    X = O.look(t1, Q) & O.look(t2, E)
    nu = SV.nu_of(Q, e1, C, B)
    T = X & SV.VMASK[nu]
    rows = [t for j, t in enumerate(SV.OLD_TAUS) if (T >> j) & 1 and t in SV.S_TAUS]
    g = (e1, C, B, (v["Y1"] + v["w12"]) & M, v["Y12"])
    acc = dict(node_units=0, node_units_ge24=0, leaf_units=0, saved={k: 0 for k in CFGS},
               saved_leaves={k: 0 for k in CFGS})
    vc = {k: 0 for k in ("leaves", "path_vs_full_mismatch", "c1_vs_search_mismatch", "leaves_keep_required",
                         "keep_required_but_killed", "leaves_qstar_ha", "qstar_ha_killed", "roots", "roots_killed_all",
                         "roots_killed_Q", "roots_qstar", "roots_qstar_ha", "roots_qstar_ha_killed")}
    cnt = dict(forced=0, selected=0, free=0, leaves=0, roots=0)
    Ep = (E + SV.DY3) & M
    roots = []
    fixed = 0
    if rows:
        fams = {SV.ROWS[t].family for t in rows}
        fixed = SV.U_STEP + SV.U_FAMILY * len(fams) + SV.U_ROW_G7 * len(rows)
        for t in rows:
            row = SV.ROWS[t]
            kappa = row.sigma ^ SV.EPS ^ E ^ Ep
            res = SV.row_setup(row, Q, y, E, Ep, e1, kappa, True, C, B, [])
            if res is None:
                continue
            h, states = res
            for r in traverse_g(row, Q, y, E, Ep, kappa, e1, h, states, cnt, g, acc, v, vc):
                roots.append((r, t))
    ref = SV.solve(Q, y, E, C=C, B=B, X=X, g7=True, precheck=True)
    same = (ref["counts"] == cnt) and (sorted(roots) == ref["roots"])
    jc = [j1_count(Q, th) for th in HOT_TARGETS]
    hot = sum(jc)
    sc = {th: j1_count(Q, th) for th in S_THETAS}
    scoreS = sum(sc.values())
    scoreT = sum(sc[THETA(t)] for t in rows)
    # sanity: J1 count > 0 iff j1_exists
    j1ok = all((sc[THETA(t)] > 0) == SV.j1_exists(Q, THETA(t)) for t in SV.S_TAUS)
    return dict(Y9=Q, nrows=len(rows), units=ref["units"], fixed=fixed, cap=static_cap(rows), acc=acc, vc=vc,
                same=same, j1ok=j1ok, hot=hot, scoreS=scoreS, scoreT=scoreT, nroots=len(roots),
                X=X, nu=nu)


def load_val(tag):
    with open(os.path.join(RDIR, "val_%s.bin" % tag), "rb") as f:
        n = struct.unpack("<I", f.read(4))[0]
        data = f.read()
    out = []
    for i in range(n):
        d = struct.unpack_from("<32I", data, 128 * i)
        out.append(list(d[1:9]))
    return out


def load_root_steps(tag):
    with open(os.path.join(RDIR, "prod", tag + ".roots"), "rb") as f:
        data = f.read()
    steps = {}
    for i in range(len(data) // 64):
        d = struct.unpack_from("<16I", data, 64 * i)
        steps.setdefault((d[0], d[1]), list(d[2:10]))
    return list(steps.values())


def work(chunk):
    return [step(e) for e in chunk]


def run(items, procs):
    chunks = [items[i:i + 500] for i in range(0, len(items), 500)]
    out = []
    with Pool(procs, initializer=init) as p:
        for part in p.imap(work, chunks):
            out.extend(part)
    return out


def main():
    outp = sys.argv[1]
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    lim = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    t0 = time.time()
    pc = load_val("ctx") + load_val("ctrl")
    rs = load_root_steps("ctx") + load_root_steps("ctrl")
    if lim:
        pc, rs = pc[:lim], rs[:lim]
    rpc = run(pc, procs)
    rrs = run(rs, procs)
    res = {"seconds": None, "CHK16": CHK16, "Y11": "%08x" % Y11}
    for tag, R in (("pc", rpc), ("rootsteps", rrs)):
        agg = dict(steps=len(R), same_as_solver=sum(r["same"] for r in R), j1ok=sum(r["j1ok"] for r in R),
                   units=sum(r["units"] for r in R), fixed=sum(r["fixed"] for r in R),
                   node_units=sum(r["acc"]["node_units"] for r in R),
                   node_units_ge24=sum(r["acc"]["node_units_ge24"] for r in R),
                   leaf_units=sum(r["acc"]["leaf_units"] for r in R),
                   saved={k: sum(r["acc"]["saved"][k] for r in R) for k in CFGS},
                   saved_leaves={k: sum(r["acc"]["saved_leaves"][k] for r in R) for k in CFGS},
                   vc={k: sum(r["vc"][k] for r in R) for k in R[0]["vc"]},
                   cap=sum(r["cap"] for r in R), roots=sum(r["nroots"] for r in R),
                   steps_with_root=sum(r["nroots"] > 0 for r in R))
        res[tag] = agg
        with open(os.path.join(HERE, "scores_%s.txt" % tag), "w") as f:
            for r in R:
                f.write("%08x %d %d %d %d %d %d\n" % (r["Y9"], r["hot"], r["scoreS"], r["scoreT"], r["cap"],
                                                      r["nroots"], r["nrows"]))
    res["seconds"] = time.time() - t0
    json.dump(res, open(outp, "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
