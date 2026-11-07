#!/usr/bin/env python3
"""ref_pf.py - Python reference for perframe.cu (no GPU formula reused for the trial values).

  python3 -B ref_pf.py kat  <kat.json>
  python3 -B ref_pf.py val  <keyhex1> <keyhex2> <val.bin> [...]    every step and trial of GPU val dumps + frame records
  python3 -B ref_pf.py hits <keyhex1> <keyhex2> <hits.bin> [...]   recompute every dumped hit
  python3 -B ref_pf.py cmp  <val.bin> <run.bin> [...]              frame records of the production kernel = val kernel

Reference path (program of entry 9a9f3b7b, research/pkg16/pkg/blake3-r2/experiments/halfsearch.py, imported unchanged):
frame words, the g subspace and the c1 subspace from the generators (written here, Python); step CO =
halfsearch.ctr_outer(C0.d1, g, D2.b1, S11, S4, X9, w6, member); the filter masks by halfsearch.ctr_look on its own
ctr_tables(); step CT = halfsearch.ctr_trial (None = t 0: not valid); both last-chunk blocks compressed in full by
halfsearch.compress2 with counter t and flags 3; tau, eps, beta = XOR differences of E1's a output, c output, first-half
b (E1 = G(y1, y6, y11, y12, w12, w5) on the real round-2 state); eps3, j1, j3 = E3's a output, first-half c, c output
(E3 = G(y3, y4, y9, y14, w15, w8)); h1 = E3's first-half d on A; r = XOR of chaining-value word 1. halfsearch.ctr_lane
(its own complete check of the trial) is run on every trial of a val dump and must hold.
"""
import hashlib
import json
import os
import struct
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "pkg16", "pkg", "blake3-r2", "experiments"))
import halfsearch as H  # noqa: E402

M32 = 0xFFFFFFFF
NE = 6
NREC = 32
GDIM = 19
FQ, FE = H.ctr_tables()
TAUS = H.CTR_TAUS
TH = tuple(H.ctr_g(t) for t in TAUS)
FREE_Q = [i for i in range(32) if not (H.CTR_MASK >> i) & 1]
assert len(FREE_Q) == 21


def philox(c, k):
    c0, c1, c2, c3 = c
    k0, k1 = k
    for _ in range(10):
        p0, p1 = 0xD2511F53 * c0, 0xCD9E8D57 * c2
        c0, c1, c2, c3 = (p1 >> 32) ^ c1 ^ k0, p1 & M32, (p0 >> 32) ^ c3 ^ k1, p0 & M32
        k0, k1 = (k0 + 0x9E3779B9) & M32, (k1 + 0xBB67AE85) & M32
    return [c0, c1, c2, c3]


def gen8(gen, keyhex, arm, block, slot, purpose):
    if gen == 1:
        k = struct.unpack(">2I", bytes.fromhex(keyhex)[:8])
        return philox((slot, block, arm, 2 * purpose), k) + philox((slot, block, arm, 2 * purpose + 1), k)
    d = hashlib.sha256(bytes.fromhex(keyhex) + struct.pack(">IIII", arm, block, slot, purpose)).digest()
    return list(struct.unpack(">8I", d))


def rank(vs):
    rows, r = list(vs), 0
    for bit in range(31, -1, -1):
        piv = next((i for i in range(r, len(rows)) if rows[i] >> bit & 1), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i] >> bit & 1:
                rows[i] ^= rows[r]
        r += 1
    return r


def draw_g(gen, keyhex, arm, block):
    a = 0
    while True:
        w = []
        for q in range(3):
            w += gen8(gen, keyhex, arm, block, 0xFFFFFFFE, 3 * a + q)
        bg, L = w[0], w[1:1 + GDIM]
        a += 1
        if rank(L) == GDIM or a >= 16:
            return bg, L, a


def unpack_sub(w):
    F = 0x1FFFFF
    col = [w[1 + i] & F for i in range(7)]
    col += [((w[0] >> 21) | ((w[1] >> 21) << 11)) & F, ((w[2] >> 21) | ((w[3] >> 21) << 11)) & F,
            ((w[4] >> 21) | ((w[5] >> 21) << 11)) & F]
    return w[0] & F, col


def draw_c(gen, keyhex, arm, block):
    a = 0
    while True:
        b, col = unpack_sub(gen8(gen, keyhex, arm, block, 0xFFFFFFFD, a))
        a += 1
        if rank(col) == 10 or a >= 16:
            return b, col, a


def g_of(bg, L, i):
    gi, x = i ^ (i >> 1), bg
    for b in range(GDIM):
        if gi >> b & 1:
            x ^= L[b]
    return x


def c1_of(b, col, j):
    gj, x = j ^ (j >> 1), b
    for i in range(10):
        if gj >> i & 1:
            x ^= col[i]
    return H.CTR_VALUE | sum(((x >> n) & 1) << p for n, p in enumerate(FREE_Q))


def frame_words(gen, keyhex, arm, block, i):
    return gen8(gen, keyhex, 0, block, 0xFFFFFFFF, 0) if arm == 0 else gen8(gen, keyhex, 1, block, i, 0)


def step_ref(ow, g):
    eight = [ow[0], g, ow[1], ow[2], ow[3], ow[4], ow[5], ow[7] % H.CLASS_SIZE]
    o = H.ctr_outer(eight)
    m1 = H.ctr_look(FQ, o["Y9"])
    m2 = H.ctr_look(FE, (H.Y3 + o["Y4"] + o["w8"]) & M32)
    return o, m1, m2, eight[7]


def gfull(a, b, c, d, x, y):
    a = (a + b + x) & M32; d = H.ror(d ^ a, 16); c = (c + d) & M32; b = H.ror(b ^ c, 12)
    a1, b1, c1, d1 = a, b, c, d
    a = (a + b + y) & M32; d = H.ror(d ^ a, 8); c = (c + d) & M32; b = H.ror(b ^ c, 7)
    return a1, b1, c1, d1, a, b, c, d


def trial_ref(o, c1, X, lane=False):
    r = H.ctr_trial(o, c1)
    if r is None:
        return dict(ev=64, t=0, valid=False)
    a, b, t, v = r
    (wa, da, ya), (wb, db, yb) = H.compress2(a[:H.LEN_A], t, H.CTR_FLAGS), H.compress2(b[:H.LEN_B], t, H.CTR_FLAGS)
    E1 = [gfull(y[1], y[6], y[11], y[12], w[12], w[5]) for w, y in ((wa, ya), (wb, yb))]
    E3 = [gfull(y[3], y[4], y[9], y[14], w[15], w[8]) for w, y in ((wa, ya), (wb, yb))]
    tau, eps, beta = E1[0][4] ^ E1[1][4], E1[0][6] ^ E1[1][6], E1[0][1] ^ E1[1][1]
    eps3, j1, j3 = E3[0][4] ^ E3[1][4], E3[0][2] ^ E3[1][2], E3[0][6] ^ E3[1][6]
    h1 = E3[0][3]
    rr = da[1] ^ db[1]
    ev = 0
    if tau in TAUS:
        ev |= 1
        if eps == H.CTR_EPS and beta == H.CTR_BETA:
            ev |= 2
    nomask = 0
    for q, th in enumerate(TH):
        if eps3 == H.CTR_EPS and j1 == th:
            ev |= 4
            nomask += int(not (X >> q & 1))
    if rr & 0xFFFF == 0:
        ev |= 8
    if rr & 0xFFFFFF == 0:
        ev |= 16
    if H.rule_a(h1):
        ev |= 32
    out = dict(ev=ev, t=t, valid=True, tau=tau, eps=eps, beta=beta, eps3=eps3, j1=j1, j3=j3, h1=h1, r=rr,
               r_is_tau_xor_j3=(rr == tau ^ j3), nomask=nomask, cv_xor=[p ^ q for p, q in zip(da, db)])
    if lane:
        good, ra, n = H.ctr_lane(o, c1)
        out["lane_ok"] = bool(good) and ra == int(H.rule_a(h1))
    return out


# ---- val -------------------------------------------------------------------------------------------------------------
def read_val(path):
    b = open(path, "rb").read()
    hdr = struct.unpack("<8I", b[:32])
    assert hdr[0] == 0x46524650 and hdr[7] == NREC
    arm, gen, b0, nb, G, k = hdr[1:7]
    off = 32
    rec = struct.unpack("<%dQ" % (NREC * nb), b[off:off + 8 * NREC * nb]); off += 8 * NREC * nb
    sd = struct.unpack("<%dI" % (24 * nb * G), b[off:off + 4 * 24 * nb * G]); off += 4 * 24 * nb * G
    td = struct.unpack("<%dI" % (10 * k * nb * G), b[off:off + 4 * 10 * k * nb * G]); off += 4 * 10 * k * nb * G
    assert off == len(b)
    return dict(arm=arm, gen=gen, b0=b0, nb=nb, G=G, k=k, rec=rec, sd=sd, td=td)


def _val_frame(a):
    'One frame (block) of a val dump: every step and trial, and the frame record.'
    arm, gen, keyhex, block, G, k, rec, sd, td = a
    fails = {}

    def bad(name, n=1):
        fails[name] = fails.get(name, 0) + n
    bg, L, ag = draw_g(gen, keyhex, arm, block)
    cb, col, ac = draw_c(gen, keyhex, arm, block)
    c1s = [c1_of(cb, col, j) for j in range(k)]
    if len(set(c1s)) != k or any((c & H.CTR_MASK) != H.CTR_VALUE for c in c1s):
        bad("c1_set")
    gs = [g_of(bg, L, i) for i in range(G)]
    if len(set(gs)) != G:
        bad("g_set")
    n, Ws = [0] * NE, [0] * NE
    pc = [[0] * k for _ in range(NE)]
    T2 = P = t0 = nomask = beta_bad = e1lra = e3pra = 0
    st = dict(trials=0, valid=0, r_identity=0, lane_ok=0, ev=[0] * NE)
    for i in range(G):
        row = sd[24 * i:24 * i + 24]
        ow = frame_words(gen, keyhex, arm, block, i)
        o, m1, m2, mnum = step_ref(ow, gs[i])
        if list(row[0:8]) != ow:
            bad("frame_words")
        if row[8] != gs[i]:
            bad("g")
        if row[9] != mnum:
            bad("member")
        if (row[10], row[11]) != (m1, m2):
            bad("masks")
        if row[23] != (o["Y1"] + o["w12"]) & M32:
            bad("KY")
        if (row[19], row[20], row[21], row[22]) != (block, arm, gen, i):
            bad("ids")
        X = m1 & m2
        T2 += int(m2 != 0); P += int(X != 0)
        ns, t0s = [0] * NE, 0
        for j in range(k):
            t = trial_ref(o, c1s[j], X, lane=True)
            g = td[10 * (i * k + j):10 * (i * k + j) + 10]
            st["trials"] += 1
            if g[0] != c1s[j]:
                bad("c1")
            if g[9] != t["ev"]:
                bad("event_bits")
            if not t["valid"]:
                t0s += 1
                if g[8] != 0:
                    bad("t")
                continue
            st["valid"] += 1
            st["r_identity"] += t["r_is_tau_xor_j3"]
            st["lane_ok"] += t["lane_ok"]
            if g[8] != t["t"]:
                bad("t")
            for name, q in (("tau", 1), ("eps", 2), ("beta", 3), ("eps3", 4), ("j1", 5), ("j3", 6), ("h1", 7)):
                if g[q] != t[name]:
                    bad(name)
            beta_bad += int(t["beta"] != H.CTR_BETA)
            nomask += t["nomask"]
            for e in range(NE):
                if t["ev"] >> e & 1:
                    ns[e] += 1
                    pc[e][j] += 1
                    st["ev"][e] += 1
            e1lra += int(t["ev"] & 34 == 34)
            e3pra += int(t["ev"] & 36 == 36)
        if list(row[12:18]) != ns or row[18] != t0s:
            bad("step_counts")
        t0 += t0s
        for e in range(NE):
            n[e] += ns[e]
            Ws[e] += ns[e] * (ns[e] - 1) if ns[e] else 0
    Wc = [sum(c * (c - 1) for c in pc[e]) for e in range(NE)]
    want = [T2, P] + n + Ws + Wc + [beta_bad, nomask, t0, ag - 1, ac - 1, G * k, G, e1lra, e3pra, 0, 0, 0]
    if list(rec) != want:
        bad("frame_record")
    return block, fails, st, n, Ws, Wc


def cmd_val(keyhex, paths, procs=22):
    out = {"files": [], "fails": {}, "frames": 0, "steps": 0, "trials": 0, "valid": 0, "r_identity": 0, "lane_ok": 0,
           "events": [0] * NE, "pairs_within": [0] * NE, "pairs_same_c1": [0] * NE}
    jobs = []
    for path in paths:
        d = read_val(path)
        arm, gen, b0, nb, G, k = d["arm"], d["gen"], d["b0"], d["nb"], d["G"], d["k"]
        for bl in range(nb):
            jobs.append((arm, gen, keyhex[gen], b0 + bl, G, k, d["rec"][NREC * bl:NREC * bl + NREC],
                         d["sd"][24 * G * bl:24 * G * (bl + 1)], d["td"][10 * k * G * bl:10 * k * G * (bl + 1)]))
            out["steps"] += G
        out["files"].append(dict(path=os.path.basename(path), arm=arm, gen=gen, b0=b0, nb=nb, G=G, k=k,
                                 sha256=hashlib.sha256(open(path, "rb").read()).hexdigest()))
    with Pool(procs) as p:
        for block, fails, st, n, Ws, Wc in p.imap_unordered(_val_frame, jobs, chunksize=1):
            out["frames"] += 1
            for kk, vv in fails.items():
                out["fails"][kk] = out["fails"].get(kk, 0) + vv
            for q in ("trials", "valid", "r_identity", "lane_ok"):
                out[q] += st[q]
            for e in range(NE):
                out["events"][e] += st["ev"][e]
                out["pairs_within"][e] += Ws[e] // 2
                out["pairs_same_c1"][e] += Wc[e] // 2
    out["mismatches"] = sum(out["fails"].values()) + (out["valid"] - out["r_identity"]) + (out["valid"] - out["lane_ok"])
    out["event_names"] = ["E1a", "E1L", "E3P", "R16", "R24", "RA"]
    return out


# ---- hits ------------------------------------------------------------------------------------------------------------
def _hit_job(a):
    keyhex, h = a
    arm, gen, block, i, g, j, c1, ev, tau, eps, eps3, j1, j3, X, h1, KY = h
    bg, L, _ = draw_g(gen, keyhex, arm, block)
    cb, col, _ = draw_c(gen, keyhex, arm, block)
    gr, c1r = g_of(bg, L, i), c1_of(cb, col, j)
    o, m1, m2, _ = step_ref(frame_words(gen, keyhex, arm, block, i), gr)
    t = trial_ref(o, c1r, m1 & m2)
    ok = (gr == g and c1r == c1 and t["valid"] and t["ev"] == ev and t["tau"] == tau and t["eps"] == eps
          and t["eps3"] == eps3 and t["j1"] == j1 and t["j3"] == j3 and t["h1"] == h1 and (m1 & m2) == X
          and (o["Y1"] + o["w12"]) & M32 == KY and t["r_is_tau_xor_j3"] and t["nomask"] == 0)
    zero_words = sum(int(x == 0) for x in t.get("cv_xor", [1] * 8))
    return ok, ev, zero_words


def cmd_hits(keyhex, paths, procs=22):
    res = {"files": [], "hits": 0, "ok": 0, "by_event_bit": [0] * 7, "fail_examples": [],
           "cv_zero_words_hist_E1L": {}, "cv_zero_words_hist_E3P": {}}
    for path in paths:
        b = open(path, "rb").read()
        n = struct.unpack("<I", b[:4])[0]
        recs = [struct.unpack("<16I", b[4 + 64 * i:4 + 64 * i + 64]) for i in range(n)]
        with Pool(procs) as p:
            for i, (ok, ev, zw) in enumerate(p.imap(_hit_job, [(keyhex[r[1]], r) for r in recs], chunksize=8)):
                res["hits"] += 1
                res["ok"] += ok
                for q in range(7):
                    res["by_event_bit"][q] += ev >> q & 1
                for name, bit in (("E1L", 2), ("E3P", 4)):
                    if ev & bit:
                        hh = res["cv_zero_words_hist_" + name]
                        hh[str(zw)] = hh.get(str(zw), 0) + 1
                if not ok and len(res["fail_examples"]) < 5:
                    res["fail_examples"].append(list(recs[i]))
        res["files"].append(dict(path=os.path.basename(path), records=n, sha256=hashlib.sha256(b).hexdigest()))
    return res


def read_rec(path):
    b = open(path, "rb").read()
    hdr = struct.unpack("<8I", b[:32])
    assert hdr[0] == 0x46524650
    nb, nrec = hdr[4], hdr[7]
    return hdr, struct.unpack("<%dQ" % (nrec * nb), b[32:32 + 8 * nrec * nb])


def cmd_cmp(pairs):
    out = {"pairs": [], "all_equal": True}
    for vpath, rpath in pairs:
        hv, rv = read_rec(vpath)
        hr, rr = read_rec(rpath)
        eq = hv[1:] == hr[1:] and rv == rr
        out["pairs"].append(dict(val=os.path.basename(vpath), run=os.path.basename(rpath), header=list(hr[1:7]),
                                 equal=eq))
        out["all_equal"] &= eq
    return out


def cmd_kat(path):
    g = json.load(open(path))
    vec = [((0, 0, 0, 0), (0, 0)), ((M32,) * 4, (M32, M32)),
           ((0x243f6a88, 0x85a308d3, 0x13198a2e, 0x03707344), (0xa4093822, 0x299f31d0))]
    known = [["6627e8d5", "e169c58d", "bc57ac4c", "9b00dbd8"], ["408f276d", "41c83b0e", "a20bc7c6", "6d5451fd"],
             ["d16cfe09", "94fdcceb", "5001e420", "24126ea1"]]
    py = [["%08x" % x for x in philox(c, k)] for c, k in vec]
    keyhex = "".join("%08x" % i for i in range(1, 9))
    sha = ["%08x" % x for x in gen8(2, keyhex, 1, 2, 3, 4)]
    return dict(python=py, gpu_mine=g["philox_mine"], gpu_curand=g["philox_curand"], random123_kat=known,
                philox_all_equal=(py == g["philox_mine"] == g["philox_curand"] == known),
                sha_python=sha, sha_gpu=g["sha48_prefix_1to8_args_1_2_3_4"],
                sha_equal=(sha == g["sha48_prefix_1to8_args_1_2_3_4"]))


def main():
    mode = sys.argv[1]
    if mode == "kat":
        print(json.dumps(cmd_kat(sys.argv[2])))
    elif mode == "val":
        print(json.dumps(cmd_val({1: sys.argv[2], 2: sys.argv[3]}, sys.argv[4:])))
    elif mode == "hits":
        print(json.dumps(cmd_hits({1: sys.argv[2], 2: sys.argv[3]}, sys.argv[4:])))
    elif mode == "cmp":
        a = sys.argv[2:]
        print(json.dumps(cmd_cmp(list(zip(a[0::2], a[1::2])))))
    else:
        raise SystemExit("unknown mode")


if __name__ == "__main__":
    main()
