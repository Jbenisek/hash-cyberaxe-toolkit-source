#!/usr/bin/env python3
"""walk_mask.py - crossline-XF1: the masked partner walk inside opened clusters (CPU, standard library only).

Claim under test: inside an opened cluster whose borrow guard is quiet, alive-16 of automaton (2) restricted to S is a
function of omega bit 8 and omega bits 9..13 only, and bits 9..13 are a bijective 5-bit function of the cluster bits
j = e1[10..14] driven by the representative's carries (bin10, c17, c25, c9a, c9b).  A 128-entry per-context table
(index bits: 0 bin10, 1 c17, 2 c25, 3 c9a, 4 c9b, 5 omega bit 8, 6 alive9 of the shared 9-bit prefix) gives a 32-bit
survivor mask; members outside the mask are skipped.  Guard: the cluster falls back to today's 31-partner walk when
Y0 bits 8..15 of the representative equal bits 8..15 of A = C0.b1 + w6 + X4 + w2 (the only case in which the two
borrow candidates h = H, H-1 of F.prefixes can give different X0 bits 16..25; see RESULT.md section 2).

  python -B walk_mask.py facts OUT.json            exhaustive LUT facts and the counted table cost
  python -B walk_mask.py sweep LO HI OUT.json      full contexts xf1-LO .. xf1-(HI-1): all 16384 clusters, no halts
  python -B walk_mask.py trial LO HI OUT.json      organizer trial shape: F.walk vs walk_x on the same seeds
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

import sys, json, time, hashlib, struct
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCJ/work'))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/combos/grok_xfer/claude_check'))
import frontline_full as F
from frontline_full import *                     # the names used by the copied walk()
from window14 import alive

M, LB, ONES = F.M, F.LB, F.ONES
ONES_N = [sum(1 << LB * i for i in range(n)) for n in range(8)]

# ---- universal tables (context-free, built once) ---------------------------------------------------------------------
AL16 = bytearray(alive(x, 16) for x in range(1 << 16))            # alive-16 of (2) restricted to S, by omega mod 2^16
A9 = [F.S7 >> (p & 127) & 1 for p in range(512)]                  # alive-9 = four copies of S7 (CI 1.3)
PX = [(p >> 8 & 1) << 5 | A9[p] << 6 for p in range(512)]        # index bits 5, 6 from the shared 9-bit prefix
LW = [[AL16[next(p for p in range(512) if A9[p] and p >> 8 & 1 == b8) | w << 9] for w in range(32)] for b8 in (0, 1)]
BIN10 = [int((F.member(k)[0] & 0x3FF) < (F.Y3 & 0x3FF)) for k in range(64)]   # borrow into y bit 10, by g mod 64
E9 = F.CLASS_VALUE >> 9 & 1                                       # e1 bit 9 (class-fixed)

# ---- machine units charged by the masked layout (per event; RESULT.md section 3 lists the operations) ---------------
X_IX = 19          # per representative batch: four packed carry words (8) and their 4-bit packed index word (11)
X_IDX = 16         # per opened cluster: lane extract 2, prefix extract+PX load 3, BIN10 load 3, combine 2,
                   # table address 2, mask/chunk-pointer load 2, chunk-count test 2
X_GUARD = 4        # per opened cluster: Y0 bits 8..15 extract 2, compare with resident A bits 8..15, branch
X_BCAST = 6        # per masked cluster: representative U and E lanes extracted (4) and broadcast to 7 lanes (2)
X_CHUNK = 8        # per masked batch: JU and JE address+load (4), two adds (2), chunk loop control (2)
U_MASK_WORST = U_REP_T2 + U_NEST + X_IDX + X_GUARD + X_BCAST + 2 * (U_PART + X_CHUNK)   # two full 7-lane batches
U_FALLBACK = U_OPEN + X_IDX + X_GUARD                              # guard fired: today's walk plus the tests
FALLBACK_MAX = 128                                                 # clusters per context that can fire (DERIVED)


def context(seed):
    sh = hashlib.shake_256(b"frontline context" + seed).digest(160)
    return sh, struct.unpack("<7I", sh[:28])


def ctx_words(ow):
    e1, y = F.member(0)
    v = F.rebuild(ow, y, e1)
    cw = (v["C0_b1"], v["C0_c1"], v["C0_d1"], v["C0_b1"] + v["w6"] + v["X4"] + v["w2"] & M,
          F.rol(F.X15, 24) ^ v["S15"], v["S0"] + v["S5"])
    return v, cw


def build_table(v, A):
    """The per-context survivor table by the window model.  Returns (masks[128], chunks[128], ops, perm_ok).
    chunks[idx] = list of (js, JU, JE): partner members j != 0 of the mask in increasing order, in batches of 7, with
    the packed lane offsets JU = sum (j << 17) << 36 lane and JE = sum (j << 10) << 36 lane.  ops counts one unit per
    arithmetic/logic/load/store and two per loop iteration (control)."""
    ops = 20                                                     # context constants: negations, sums, 7 window cuts
    nC0c1, Ap, nS0S5 = -v["C0_c1"] & M, -A & M, -(v["S0"] + v["S5"]) & M
    y3w, b1w, c1w = F.Y3 >> 10 & 31, v["C0_b1"] >> 17 & 31, nC0c1 >> 17 & 31
    d1w, apw, sw = v["C0_d1"] >> 25 & 31, Ap >> 25 & 31, nS0S5 >> 9 & 31
    kx = (F.rol(F.X15, 8) >> 25 & 31) ^ (v["S15"] >> 9 & 31)
    ej = [E9 | (j & 15) << 1 for j in range(32)]
    ops += 32 * 3
    masks = [0] * 128
    images = {}
    for bin10 in (0, 1):
        for j in range(32):
            ops += 2 + 5
            t1 = (((j - y3w - bin10) & 31) ^ b1w) + c1w
            for c17 in (0, 1):
                ops += 2 + 4
                t2 = (((t1 + c17) & 31) ^ d1w) + apw
                for c25 in (0, 1):
                    ops += 2 + 4
                    t3 = (((t2 + c25) & 31) ^ kx) + sw
                    for c9a in (0, 1):
                        ops += 2 + 4
                        s1 = ((t3 + c9a) & 31) + ej[j]
                        for c9b in (0, 1):
                            ops += 2 + 3
                            w = (s1 + c9b) & 31
                            base = bin10 | c17 << 1 | c25 << 2 | c9a << 3 | c9b << 4
                            images.setdefault(base, set()).add(w)
                            for b8 in (0, 1):
                                ops += 2 + 4
                                masks[base | b8 << 5 | 64] |= LW[b8][w] << j
    perm_ok = all(len(s) == 32 for s in images.values()) and len(images) == 32
    chunks = [[] for _ in range(128)]
    for idx in range(64, 128):
        ops += 2 + 9 + 10                                        # entry loop, chunk stores and count, argmax of 5
        js = [j for j in range(1, 32) if masks[idx] >> j & 1]
        ops += 17 * len(js)                                      # ctz, clear, two shifted lane offsets, adds, counters,
        #                                                          old-batch number load and count (3), partition (2)
        if len(js) <= 7:
            groups = [js] if js else []
        else:                                                    # GROUP CHUNKING (RESULT.md 2.4): the old batch with
            cnt = [sum((j - 1) // 7 == k for j in js) for k in range(5)]   # most survivors is one chunk, the rest the
            k = max(range(5), key=lambda k: (cnt[k], -k))                    # other; pigeonhole gives both <= 7
            groups = sorted([[j for j in js if (j - 1) // 7 == k], [j for j in js if (j - 1) // 7 != k]], key=min)
        for part in groups:
            assert 1 <= len(part) <= 7
            JU = sum(j << 17 << LB * t for t, j in enumerate(part))
            JE = sum(j << 10 << LB * t for t, j in enumerate(part))
            chunks[idx].append((part, JU, JE))
    return masks, chunks, ops, perm_ok


def ix_word(Y8, Y12, Y0, X0, D0a1, w8, om, E, P, ApP):
    'Packed 4-bit carry index per lane: c17 | c25 << 1 | c9a << 2 | c9b << 3 (the X_IX charge).'
    return ((Y12 ^ Y8 ^ P[1]) >> 17 & ONES | (X0 ^ Y0 ^ ApP) >> 24 & 2 * ONES
            | (w8 ^ D0a1 ^ P[15]) >> 7 & 4 * ONES | (om ^ E ^ w8) >> 6 & 8 * ONES)


def omega_x(U, E, P):
    'F.omega_side, line for line, also returning the words whose carries the index reads.'
    C0b1, nC0c1, C0d1, nC0b1w6, _, _, _, nX4w2, _, S15, _, _, _, _, _, nS0S5 = P
    Y8 = U ^ C0b1
    Y12 = Y8 + nC0c1
    Y0 = F.pror(Y12, 24) ^ C0d1
    C0a1 = Y0 + nC0b1w6
    X0 = C0a1 + nX4w2
    D0d1 = X0 ^ F.RX15
    D0a1 = F.pror(D0d1, 16) ^ S15
    w8 = D0a1 + nS0S5
    om = E + w8
    return Y8, Y12, Y0, C0a1, X0, D0d1, D0a1, w8, om


# ---- mode facts -------------------------------------------------------------------------------------------------------
def facts(out):
    r = {}
    r["alive16_bits14_15_free"] = sum(AL16[x] != AL16[x & 0x3FFF] for x in range(1 << 16))      # 0 expected
    r["alive16_bits0_7_free_given_alive9"] = sum(
        AL16[x] != LW[x >> 8 & 1][x >> 9 & 31] for x in range(1 << 16) if A9[x & 511])          # 0 expected
    r["alive16_zero_off_alive9"] = sum(AL16[x] for x in range(1 << 16) if not A9[x & 511])      # 0 expected
    r["LW_popcounts"] = [sum(LW[0]), sum(LW[1])]                                                  # 8, 9 expected
    r["alive16_implied_by_T2_sample"] = 0
    import random
    rnd = random.Random(20261009)
    for _ in range(200000):
        x = rnd.getrandbits(32)
        r["alive16_implied_by_T2_sample"] += bool(F.T2(x)) and not AL16[x & 0xFFFF]              # 0 expected
    tops, perms = [], 0
    for i in range(64):
        _, ow = context(b"xf1-facts-%d" % i)
        v, cw = ctx_words(ow)
        masks, chunks, ops, ok = build_table(v, cw[3])
        tops.append(ops)
        perms += ok
        r.setdefault("mask_popcounts", set()).update(bin(m).count("1") for m in masks[64:])
        r.setdefault("chunks_per_entry", set()).update(len(c) for c in chunks[64:])
    r["mask_popcounts"] = sorted(r["mask_popcounts"])
    r["chunks_per_entry"] = sorted(r["chunks_per_entry"])
    r["table_ops_min_max"] = [min(tops), max(tops)]
    r["window_map_bijective_contexts"] = "%d of 64" % perms
    r["units"] = dict(X_IX=X_IX, X_IDX=X_IDX, X_GUARD=X_GUARD, X_BCAST=X_BCAST, X_CHUNK=X_CHUNK,
                      U_MASK_WORST=U_MASK_WORST, U_FALLBACK=U_FALLBACK, FALLBACK_MAX=FALLBACK_MAX)
    json.dump(r, open(out, "w"), indent=1)
    print(json.dumps(r))


# ---- mode sweep: complete contexts, no halts --------------------------------------------------------------------------
def sweep_context(seed):
    _, ow = context(seed)
    cx = F.co_ctx(*ow, F.FLAGS)
    P = F.operands(cx)
    nA = (-((cx["C0_b1"] + cx["w6"] + cx["X4"] + cx["w2"] & M) >> 16) & 127) * ONES
    Pq = ((F.rol(F.X15, 24) ^ cx["S15"]) & 127) << 14
    v, cw = ctx_words(ow)
    masks, chunks, tops, perm_ok = build_table(v, cw[3])
    ApP, Ahi = (-cw[3] & M) * ONES, cw[3] >> 8 & 255
    s = dict(opened=0, closed=0, fired_all=0, fallback=0, fallback_exact=0, fired_exact_all=0, exact_not_cheap=0,
             members_opened=0, e_lanes=0, lost=0, mismatch=0, prefix_split=0, pack_bad=0, coref_checked=0,
             coref_bad=0, fallback_wouldlose=0, fallback_wouldmis=0, alive9_dead_opened=0,
             fills_old=0, fills_new=0, fills_rep=0, units_old=0, units_new_mean=0, units_new_worst=0,
             table_ops=tops, perm_ok=int(perm_ok), surv_hist={}, partner_hist={}, t2_hist={})
    for rb in range(F.REP_BATCHES):
        reps = [F.cmember(g, 0) for g in range(7 * rb, min(7 * rb + 7, 1 << 14))]
        U, E = F.pack(reps)
        Y8, Y12, Y0, C0a1, X0, D0d1, D0a1, w8, om = omega_x(U, E, P)
        key = ((Y0 >> 16 & F.R7) + nA & F.R7) | (E + P[15] & F.R7) << 7
        IX = ix_word(Y8, Y12, Y0, X0, D0a1, w8, om, E, P, ApP)
        rep_fill = False
        for i in range(len(reps)):
            g, sh = 7 * rb + i, LB * i
            fired = (Y0 >> sh + 8 & 255) == Ahi
            s["fired_all"] += fired
            W = F.prefixes(cw, *reps[i][1::-1])
            s["fired_exact_all"] += len(W) == 2
            s["exact_not_cheap"] += len(W) == 2 and not fired          # 0 expected: the cheap guard covers the exact one
            if not F.gate(Pq | key >> sh & 0x3FFF):
                s["closed"] += 1
                continue
            s["opened"] += 1
            omr = om >> sh & M
            idx = BIN10[g & 63] | (IX >> sh & 15) << 1 | PX[omr & 511]
            mk = masks[idx]
            s["alive9_dead_opened"] += not A9[omr & 511]
            # truth: all 32 members by the packed omega side, today's consecutive partner batches
            oms = [omr]
            fo = 0
            for j0 in range(1, 32, 7):
                ms = [F.cmember(g, j) for j in range(j0, min(j0 + 7, 32))]
                pom = F.omega_side(*F.pack(ms), P)[2]
                po = [pom >> LB * t & M for t in range(len(ms))]
                oms += po
                fo += any(F.T2(o) for o in po)
            if s["opened"] % 64 == 1:                                    # straight-line reference, all 32 members
                for j in range(32):
                    s["coref_checked"] += 1
                    s["coref_bad"] += F.co_ref(*ow, F.cmember(g, j)[1], F.FLAGS)[0] != oms[j]
            t2 = [F.T2(o) != 0 for o in oms]
            a16 = [AL16[o & 0xFFFF] for o in oms]
            ne = sum(t2)
            s["members_opened"] += 32
            s["e_lanes"] += ne
            s["t2_hist"][ne] = s["t2_hist"].get(ne, 0) + 1
            rep_fill |= t2[0]
            s["fills_old"] += fo
            s["units_old"] += F.U_OPEN
            lost = sum(t2[j] and not mk >> j & 1 for j in range(32))
            mis = sum(a16[j] != (mk >> j & 1) for j in range(32))
            if fired:
                s["fallback"] += 1
                s["fallback_exact"] += len(W) == 2
                s["fallback_wouldlose"] += lost
                s["fallback_wouldmis"] += mis
                s["fills_new"] += fo
                s["units_new_mean"] += U_FALLBACK
                s["units_new_worst"] += U_FALLBACK
                continue
            s["lost"] += lost
            s["mismatch"] += mis
            s["prefix_split"] += len({o & 511 for o in oms}) != 1
            pc = bin(mk).count("1")
            s["surv_hist"][pc] = s["surv_hist"].get(pc, 0) + 1
            npart = bin(mk & ~1).count("1")
            s["partner_hist"][npart] = s["partner_hist"].get(npart, 0) + 1
            u = U_REP_T2 + U_NEST + X_IDX + X_GUARD
            if chunks[idx]:
                u += X_BCAST
            ub, eb = F.rol(reps[i][1], 7), reps[i][0]
            fn = 0
            for js, JU, JE in chunks[idx]:
                n = len(js)
                u += (U_PART if n > 3 else U_PART_TAIL) + X_CHUNK
                fn += any(t2[j] for j in js)
                if s["opened"] % 16 == 1:                                # broadcast pack equals the member pack
                    s["pack_bad"] += (ub * ONES_N[n] + JU, eb * ONES_N[n] + JE) != F.pack([F.cmember(g, j) for j in js])
            s["fills_new"] += fn
            s["fill_dom_viol"] = s.get("fill_dom_viol", 0) + (fn > fo)       # pointwise G_mask <= G_cluster: 0 expected
            s["chunks_max"] = max(s.get("chunks_max", 0), len(chunks[idx]))
            s["units_new_mean"] += u
            s["units_new_worst"] += U_MASK_WORST
        s["fills_rep"] += rep_fill
    s["fills_old"] += s["fills_rep"]
    s["fills_new"] += s["fills_rep"]
    return s


def merge(tot, s):
    for k, x in s.items():
        if isinstance(x, dict):
            d = tot.setdefault(k, {})
            for a, b in x.items():
                d[str(a)] = d.get(str(a), 0) + b
        elif k in ("chunks_max", "table_ops_max"):
            tot[k] = max(tot.get(k, 0), x)
        else:
            tot[k] = tot.get(k, 0) + x


def sweep(lo, hi, out):
    t0 = time.time()
    per, tot = [], {}
    for i in range(lo, hi):
        s = sweep_context(b"xf1-%04d" % i)
        per.append(dict(i=i, opened=s["opened"], fired_all=s["fired_all"], fallback=s["fallback"],
                        fills_old=s["fills_old"], fills_new=s["fills_new"], lost=s["lost"], mismatch=s["mismatch"],
                        e_lanes=s["e_lanes"], units_old=s["units_old"], units_new_mean=s["units_new_mean"],
                        table_ops=s["table_ops"], fill_dom_viol=s.get("fill_dom_viol", 0),
                        chunks_max=s.get("chunks_max", 0), fills_rep=s["fills_rep"]))
        s["table_ops_max"] = s["table_ops"]
        merge(tot, s)
        json.dump(dict(range=[lo, i + 1], seconds=round(time.time() - t0, 1), total=tot, per_context=per),
                  open(out, "w"), indent=0)
        print("ctx %d opened %d fired %d fallback %d lost %d mis %d fills %d->%d  %.0fs" % (
            i, s["opened"], s["fired_all"], s["fallback"], s["lost"], s["mismatch"], s["fills_old"], s["fills_new"],
            time.time() - t0), flush=True)


# ---- mode trial: a faithful copy of F.walk with the masked partner walk ------------------------------------------------
def walk_x(seed, nr=TRIAL_REPS, n_e=0, n_p=0, n_a=0, n_g=0, credit=CREDIT, t2_every=T2_EVERY, gate=gate):
    'F.walk (frontline_full.py line 1163) with the opened branch replaced by the guarded masked partner walk.'
    sh = hashlib.shake_256(b"frontline context" + seed).digest(160)
    ow = struct.unpack("<7I", sh[:28])                                # word 7 of the fresh word is unused
    draws = [QSTAR_VALUE | w & ~QSTAR_MASK & M for w in struct.unpack("<32I", sh[32:])]   # c1 in Q* for charts
    o = dict.fromkeys(OBS + ("lost", "fallback", "masked_members", "table_ops"), 0)
    o["units"] = U_CONTEXT
    first, bad, chk = None, 0, 0
    cx = co_ctx(*ow, FLAGS)                                           # the 39 context lines, once
    P = operands(cx)
    nA = (-((cx["C0_b1"] + cx["w6"] + cx["X4"] + cx["w2"] & M) >> 16) & 127) * ONES   # -(A >> 16) mod 128
    Pq = ((rol(X15, 24) ^ cx["S15"]) & 127) << 14                     # q block base, q = L mod 128 (CJ 4)

    def lane(ms, E, i, om, C0a1, D0d1, W, cy):
        'Test (2) of one walked member, its Q path and passing lane; cy = [cached Y9 of the batch]; the reference.'
        nonlocal n_e, n_p, n_g, credit, first, bad, chk
        sh_ = LB * i
        omi = om >> sh_ & M
        m2 = T2(omi)                                                  # test (2)
        e1 = E >> sh_ & M
        y = (e1 - Y3) & M
        rom, ry9 = co_ref(*ow, y, FLAGS)                              # reference: the straight-line step CO
        rm2 = T2(rom)
        rx = T1(ry9) & rm2 if rm2 else 0
        x = y9i = 0
        if m2:                                                        # Q path
            o["e_lanes"] += 1
            o["units"] += U_E
            n_e += 1
            if n_e > E_BUDGET:
                raise Halt(1)
            if not cy:                                                # the batch's first E lane: fill the cache
                o["fills"] += 1
                o["units"] += U_FILL
                n_g += 1
                if n_g > G_BUDGET:
                    raise Halt(5)
                cy.append(y9_path(C0a1, D0d1, P))                     # the packed Y9 of all lanes, once per batch
            Y9p, ov2 = cy[0]
            bad += cy[0] != y9_path(C0a1, D0d1, P)                    # reference: the cache against a fresh Y9 path
            y9i = Y9p >> sh_ & M
            m1 = T1(y9i)
            x = m1 & m2
            bad += m1 != mask1_ref(y9i) or y9i != ry9 or bool(ov2 & BOUND)
            u = step_ct(rebuild(ow, y, e1), draws[o["e_lanes"] & 31])
            wr, _, ys = compress2(u["A"], u["t"], FLAGS)
            bad += (ys[4], ys[9], (ys[3] + ys[4] + wr[15] + wr[8]) & M) != (y, y9i, omi)
            chk += 3
        bad += omi != rom or m2 != rm2 or x != rx or rom & 511 not in W
        chk += 1
        if m2 or ms[i][2] % t2_every == 0:
            bad += m2 != mask2_ref(omi)
            chk += 1
        if not x:
            return
        o["passes"] += 1                                              # passing lane
        o["units"] += U_PASS
        n_p += 1
        if n_p > PASS_BUDGET:
            raise Halt(2)
        if first is None:
            first = ms[i][2]
        v = rebuild(ow, y, e1)
        bad += (v["Y9"], v["omega"]) != (y9i, omi)
        ok, gc = chart_check(v, draws[2 + o["passes"] % 30])
        bad, chk = bad + (not ok), chk + 2 + gc
        T = x & VMASK[nu_of(v["Y9"], e1, v["C2_c1"], v["C2_b1"])]   # pre-check
        if not T:
            return
        if CM[T] > credit:                                            # preflight: the whole metered cap CM(T)
            raise Halt(3)
        o["solver_calls"] += 1
        b, d = steps23(ow, y, e1, T, o)
        credit -= d                                                   # the executed, metered debit
        bad += b
        chk += 2

    try:
        e1, y = member(0)
        v = rebuild(ow, y, e1)
        for c1 in draws[:2]:
            ok, gc = chart_check(v, c1)
            bad, chk = bad + (not ok), chk + 1 + gc
        cw = (v["C0_b1"], v["C0_c1"], v["C0_d1"], v["C0_b1"] + v["w6"] + v["X4"] + v["w2"] & M,
              rol(X15, 24) ^ v["S15"], v["S0"] + v["S5"])            # reference: b, c, d, A, L, S0 + S5 of CI 1.1
        TAB, CH, tops, _ = build_table(v, cw[3])                      # XF1: the per-context survivor table
        o["units"] += tops
        o["table_ops"] = tops
        ApP, Ahi = (-cw[3] & M) * ONES, cw[3] >> 8 & 255
        for rb in list(range(nr - 1)) + [REP_BATCHES - 1]:            # representative batches, the last of 4 lanes
            reps = [cmember(g, 0) for g in range(7 * rb, min(7 * rb + 7, 1 << 14))]
            U, E = pack(reps)
            C0a1, D0d1, om, ov, Y0 = omega_side(U, E, P)
            key = ((Y0 >> 16 & R7) + nA & R7) | (E + P[15] & R7) << 7  # a | c << 7 in every lane (CJ 4)
            xs = omega_x(U, E, P)                                     # XF1: the same lines, for the carry index
            bad += (xs[3], xs[5], xs[8], xs[2]) != (C0a1, D0d1, om, Y0)
            IX = ix_word(xs[0], xs[1], xs[2], xs[4], xs[6], xs[7], xs[8], E, P, ApP)
            o["units"] += (U_REP if len(reps) == 7 else U_REP_TAIL) + X_IX
            o["members"] += len(reps)
            rc = []                                                   # the batch's cache, kept across its partners
            for i in range(len(reps)):
                g = 7 * rb + i
                W = prefixes(cw, *reps[i][1::-1])
                if not gate(Pq | key >> LB * i & 0x3FFF):             # closed: no T2 load, the next gate test
                    o["closed"] += 1
                    for j in range(32):                               # reference: all 32 members fail (2)
                        rom = co_ref(*ow, cmember(g, j)[1], FLAGS)[0]
                        m = mask2_ref(rom) > 0
                        o["skipped_pass"] += m
                        bad += m or rom & 511 not in W or (j == 0 and (rom != om >> LB * i & M or any(
                            S7 >> (w & 127) & 1 for w in W)))                 # both exact prefixes dead
                        chk += 1
                    continue
                o["opened"] += 1                                      # opened: count, budget, then partner work
                n_a += 1
                if n_a > A_BUDGET:
                    raise Halt(4)
                lane(reps, E, i, om, C0a1, D0d1, W, rc)               # the representative's T2 and paths
                s_ = LB * i
                if (Y0 >> s_ + 8 & 255) == Ahi:                       # XF1 guard fired: today's 31-partner walk
                    o["fallback"] += 1
                    o["units"] += U_FALLBACK
                    for j0 in range(1, 32, 7):                        # five partner batches, j = 1..31
                        ms = [cmember(g, j) for j in range(j0, min(j0 + 7, 32))]
                        pE = pack(ms)
                        pa, pd, pom, pov, _ = omega_side(*pE, P)
                        o["members"] += len(ms)
                        pc = []                                       # the partner batch's cache: not ready
                        for t in range(len(ms)):
                            lane(ms, pE[1], t, pom, pa, pd, W, pc)
                        bad += bool(pov & BOUND)
                        chk += 1
                    continue
                omr = om >> s_ & M
                idx = BIN10[g & 63] | (IX >> s_ & 15) << 1 | PX[omr & 511]
                mk = TAB[idx]
                o["units"] += U_REP_T2 + U_NEST + X_IDX + X_GUARD + (X_BCAST if CH[idx] else 0)
                ub, eb = rol(reps[i][1], 7), reps[i][0]
                for js, JU, JE in CH[idx]:                            # the masked partner batches (at most two)
                    n = len(js)
                    pE = (ub * ONES_N[n] + JU, eb * ONES_N[n] + JE)   # broadcast + per-context lane offsets
                    ms = [cmember(g, j) for j in js]
                    bad += pE != pack(ms)                             # reference: equals the member pack
                    chk += 1
                    o["units"] += (U_PART if n > 3 else U_PART_TAIL) + X_CHUNK
                    pa, pd, pom, pov, _ = omega_side(*pE, P)
                    o["members"] += n
                    o["masked_members"] += n
                    pc = []
                    for t in range(n):
                        lane(ms, pE[1], t, pom, pa, pd, W, pc)
                    bad += bool(pov & BOUND)
                    chk += 1
                for j in range(1, 32):                                # reference: every skipped member fails (2)
                    if mk >> j & 1:
                        continue
                    rom = co_ref(*ow, cmember(g, j)[1], FLAGS)[0]
                    m = mask2_ref(rom) > 0
                    o["lost"] += m
                    bad += m or rom & 511 not in W
                    chk += 1
            bad += bool(ov & BOUND)                                   # Lemma MB (d): no lane reaches 2^36
            chk += 1
    except Halt as e:
        o["halted"] = e.args[0]
    except Found:
        pass
    o["mismatches"] += bad
    o["checks"] += chk
    return ow, first, o


def trial(lo, hi, out, nr=TRIAL_REPS):
    keys = ("e_lanes", "passes", "solver_calls", "leaves", "roots", "certified", "opened", "closed", "skipped_pass",
            "halted", "solver_units")
    t0, rows = time.time(), []
    for i in range(lo, hi):
        seed = b"xf1-%04d" % i
        ow0, f0, o0 = F.walk(seed, nr=nr)
        ow1, f1, o1 = walk_x(seed, nr=nr)
        same = ow0 == ow1 and f0 == f1 and all(o0[k] == o1[k] for k in keys)
        rows.append(dict(i=i, same=same, first=[f0, f1], ref=o0, x=o1))
        json.dump(dict(range=[lo, i + 1], seconds=round(time.time() - t0, 1), rows=rows), open(out, "w"), indent=0)
        print("trial %d same %s e %d/%d pass %d/%d fills %d->%d members %d->%d units %d->%d mism %d/%d lost %d fb %d"
              " %.0fs" % (i, same, o0["e_lanes"], o1["e_lanes"], o0["passes"], o1["passes"], o0["fills"], o1["fills"],
                          o0["members"], o1["members"], o0["units"], o1["units"], o0["mismatches"], o1["mismatches"],
                          o1["lost"], o1["fallback"], time.time() - t0), flush=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "facts":
        facts(sys.argv[2])
    elif mode == "sweep":
        sweep(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif mode == "trial":
        trial(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5]) if len(sys.argv) > 5 else TRIAL_REPS)
