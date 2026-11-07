"""Lever s256r39: count a ROLLED 256-lane bit-sliced 39-step SHA-256 program (36 B per instruction) with the Gen of bsha.py
(the r39 build/c bit-sliced generator: pivot full adder, constant folding, polarity tracking), then price it with the bsha.py (v1) ledger.

Design II (counted here):
  phase A (straight): W'_i = W_i + K_i for i = 7..12 (constant K folded), stored; U-ring init; W-ring init constants.
  phase B (loop, 8-word body, 3 iterations): schedule words W_i = U_i + W_{i-7} + s1(W_{i-2}); U_{i+8} = W_{i-8} + s0(W_{i-7});
          W'_i = W_i + K_i (K planes loaded; their stored polarity chosen at setup so every W' plane is stored upright); W' stored.
  phase C (straight): steps 0..6 of the compression from the IV (folded), state at step 7.
  phase D (loop, 4-step body, 8 iterations, steps 7..38): T1 = h + ch + S1 + W' (W' loaded), no moves (a-ring and e-ring of 4).
  phase E (straight): feed-forward with the IV (constant adds), stage-1 test, loop control.
Every loaded plane is one load, every stored plane one store, every constant plane set into a ring register one operation,
every polarity correction one operation; loop control LOOP_ITER ops per iteration.
"""
import sys, os, importlib.util, json
from math import log2
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bsha", os.path.join(HERE, "bsha.py"))
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
Gen, ZERO, ONE, cw, sig = b.Gen, b.ZERO, b.ONE, b._constw, b._sigma
IV = b.IV
K = (0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
     0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
     0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
     0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
     0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
     0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2)        # FIPS 180-4 round constants (the first 39 equal bsha.K)
assert K[:39] == tuple(b.K)
ROUNDS = 39


def set_rounds(R):
    """Point this module and bsha at R rounds (bsha's scalar digest, unrolled trace and packed recovery kernel read ROUNDS and K)."""
    global ROUNDS
    ROUNDS = R
    b.ROUNDS, b.K, b.UNIT = R, K[:R], 84 * R - 464


LOOP_ITER = 4         # per loop iteration: pointer add, second pointer add, compare, branch
RESET = 3              # per batch: reset the two pointers and the iteration limit


def live_gates(g, outs):
    seen = set(o[0] for o in outs if o[0] != 0)
    for k in range(len(g.nodes) - 1, 0, -1):
        if k in seen and g.nodes[k][0] in "xao":
            seen.add(g.nodes[k][1])
            seen.add(g.nodes[k][2])
    return [k for k in range(1, len(g.nodes)) if k in seen and g.nodes[k][0] in "xao"]


def peak_live(g, gates, outs, carried, loaded):
    """Peak registers of the straight line in creation order: carried inputs live from the start, loaded inputs from first use,
    a gate result may take the register of an operand that dies at that gate, outputs live to the end."""
    last = {}
    for idx, k in enumerate(gates):
        _, x, y = g.nodes[k]
        last[x] = idx
        last[y] = idx
    END = len(gates)
    for o in outs:
        if o[0]:
            last[o[0]] = END
    live = set(v for v in carried if v in last)
    pk = len(live)
    for idx, k in enumerate(gates):
        _, x, y = g.nodes[k]
        for v in (x, y):
            if v in loaded and v not in live:
                live.add(v)
        pk = max(pk, len(live))
        for v in (x, y):
            if last.get(v, -1) == idx:
                live.discard(v)
        live.add(k)
        pk = max(pk, len(live))
        if last.get(k, -1) <= idx:
            live.discard(k)                  # no later use: stored at once (W'), register free again
    return pk


def add_knob(g, Kp, X):
    """X + K with K a loaded word whose 32 stored planes may be complemented at setup: K_j's polarity is chosen so that sum plane j
    is stored upright (sum polarity = xor of the three input polarities)."""
    s, c = [], ZERO
    KN = []
    for i in range(32):
        kk = (Kp[i][0], 0)
        if i == 31:
            want = X[i][1] ^ c[1]
            kk = (Kp[i][0], want)
            KN.append(want)
            s.append(g.XOR(g.XOR(X[i], kk), c))
        else:
            want = X[i][1] ^ (c[1] if c[0] else 0)
            kk = (Kp[i][0], want)
            KN.append(want)
            si, c = g.fa(X[i], kk, c)
            s.append(si)
    assert all(t[1] == 0 for t in s), "knob failed"
    KNOBS.append(KN)
    return s


KNOBS = []


# ---------------------------------------------------------------- phase D: 4-step compression body
def comp_body(pol):
    """pol: 288 input polarities (a,b,c,d,e,f,g,h words then prev).  Returns dict(gates, outs, out_pol, peak, loads)."""
    nin = 288 + 128
    g = Gen(nin)
    I = g.inputs
    sigw = lambda k0: [(I[k0 + j][0], pol[k0 + j]) for j in range(32)]
    a, bb, c, d, e, f, h2, h = [sigw(32 * w) for w in range(8)]
    prev = [(I[256 + j][0], pol[256 + j]) for j in range(32)]
    Wp = [[I[288 + 32 * s + j] for j in range(32)] for s in range(4)]          # loaded, stored upright
    for s in range(4):
        S1 = sig(g, e, 6, 11, 25, False)
        ch = [g.XOR(h2[j], g.AND(e[j], g.XOR(f[j], h2[j]))) for j in range(32)]
        t1 = g.add(g.add(g.add(h, ch), S1), Wp[s])
        S0 = sig(g, a, 2, 13, 22, False)
        ab, mj = [], []
        for j in range(32):
            ab.append(g.XOR(a[j], bb[j]))
            mj.append(g.XOR(g.AND(ab[j], prev[j]), bb[j]))
        prev = ab
        t2 = g.add(S0, mj)
        ne = g.add(d, t1)                    # new e first: d's register is then free for new a
        na = g.add(t1, t2)
        a, bb, c, d, e, f, h2, h = na, a, bb, c, ne, e, f, h2
    outs = [t for w in (a, bb, c, d, e, f, h2, h) for t in w] + prev
    gates = live_gates(g, outs)
    carried = set(I[j][0] for j in range(288))
    loaded = set(I[j][0] for j in range(288, nin))
    return dict(gates=len(gates), out_pol=[o[1] for o in outs], peak=peak_live(g, gates, outs, carried, loaded), loads=128,
                g=g, outs=outs, pol=list(pol))


def fixed_point(body, n, iters=40):
    """Iterate input polarity <- output polarity; return (polarity, mismatches) with the fewest mismatches seen."""
    pol = [0] * n
    best = None
    seen = {}
    for it in range(iters):
        r = body(pol)
        mm = sum(1 for x, y in zip(pol, r["out_pol"]) if x != y)
        if best is None or mm < best[1]:
            best = (pol, mm, r)
        if mm == 0:
            break
        key = tuple(r["out_pol"])
        if key in seen:
            break
        seen[key] = it
        pol = r["out_pol"]
    return best


# ---------------------------------------------------------------- phase B: 8-word schedule body
def sched_body(pol, first):
    """Inputs: W-ring 8 words (W[i-8..i-1]), U-ring 8 words (U_i..U_{i+7}), K 8 words (loaded).  first = index i of the first word."""
    nin = 512 + 256
    g = Gen(nin)
    I = g.inputs
    Wr = {first - 8 + p: [(I[32 * p + j][0], pol[32 * p + j]) for j in range(32)] for p in range(8)}
    U = {first + p: [(I[256 + 32 * p + j][0], pol[256 + 32 * p + j]) for j in range(32)] for p in range(8)}
    Kp = [[I[512 + 32 * p + j] for j in range(32)] for p in range(8)]
    Wouts, knobs = [], []
    for p in range(8):
        i = first + p
        un = g.add(Wr[i - 8], sig(g, Wr[i - 7], 7, 18, 3, True))
        wi = g.add(g.add(U[i], Wr[i - 7]), sig(g, Wr[i - 2], 17, 19, 10, True))
        U[i + 8] = un
        Wr[i] = wi
        KNOBS.clear()
        Wouts.append(add_knob(g, Kp[p], wi))
        knobs.append(list(KNOBS[0]))
    outs_ring = [t for p in range(8) for t in Wr[first + p]] + [t for p in range(8) for t in U[first + 8 + p]]
    outs = outs_ring + [t for w in Wouts for t in w]
    gates = live_gates(g, outs)
    carried = set(I[j][0] for j in range(512))
    loaded = set(I[j][0] for j in range(512, nin))
    return dict(gates=len(gates), out_pol=[o[1] for o in outs_ring], peak=peak_live(g, gates, outs_ring, carried, loaded), loads=256, stores=256,
                g=g, outs_ring=outs_ring, Wouts=Wouts, knobs=knobs, pol=list(pol))


# ---------------------------------------------------------------- straight phases
NET = {}
def straight_phases(sched_first, sched_pol, comp_pol, sc=7):
    """Phases A, C, E plus the corrections into the loop polarities.  x planes: word W(5+i) = planes 32(7-i)..+31 (as bsha.trace).
    sc = first step of the compression loop (steps 0..sc-1 straight)."""
    g = Gen(256)
    W = [cw(w) for w in b.PREFIX_WORDS] + [[g.inputs[32 * (7 - i) + j] for j in range(32)] for i in range(8)] + [cw(w) for w in b.TAIL]
    # phase A: W'_sc..W'_12 (constant K) and the straight schedule words with their W', stored upright (a complemented plane costs one NOT)
    s0f = lambda x: sig(g, x, 7, 18, 3, True)
    s1f = lambda x: sig(g, x, 17, 19, 10, True)
    for i in range(16, min(sched_first, ROUNDS)):        # schedule words before the loop, straight (constants folded)
        W.append(g.add(g.add(g.add(W[i - 16], s0f(W[i - 15])), W[i - 7]), s1f(W[i - 2])))
    Wp_idx = list(range(sc, 13)) + list(range(16, min(sched_first, ROUNDS)))
    Wp = [g.add(cw(K[i]), W[i]) for i in Wp_idx]
    nots_A = sum(1 for w in Wp for t in w if t[1])
    stores_A = 32 * len(Wp)
    # ring init for the schedule loop starting at sched_first
    Uinit, Winit = [], []
    for p in range(8 if sched_first < ROUNDS else 0):
        i = sched_first + p
        if i >= 16:
            Uinit.append(g.add(W[i - 16], s0f(W[i - 15])))
        else:                                            # fake U_i with W_i = U_i + W_{i-7} + s1(W_{i-2}) (i = 15 only)
            t = g.add(W[i - 7], s1f(W[i - 2]))
            neg = g.add([(x[0], x[1] ^ 1) for x in t], cw(1))      # -t = ~t + 1
            Uinit.append(g.add(W[i], neg))
    for p in range(8 if sched_first < ROUNDS else 0):
        Winit.append(W[sched_first - 8 + p])
    ring = [t for w in Winit for t in w] + [t for w in Uinit for t in w]
    sets_B = sum(1 for t in ring if t[0] == 0)          # constant planes written into ring registers
    nots_B = sum(1 for t, q in zip(ring, sched_pol) if t[0] != 0 and t[1] != q)
    # phase C: steps 0..sc-1 from the IV
    a, bb, c, d, e, f, h2, h = [cw(w) for w in IV]
    prev = [g.XOR(bb[j], c[j]) for j in range(32)]
    for i in range(sc):
        S1 = sig(g, e, 6, 11, 25, False)
        ch = [g.XOR(h2[j], g.AND(e[j], g.XOR(f[j], h2[j]))) for j in range(32)]
        t1 = g.add(g.add(g.add(g.add(cw(K[i]), h), ch), S1), W[i])
        S0 = sig(g, a, 2, 13, 22, False)
        ab, mj = [], []
        for j in range(32):
            ab.append(g.XOR(a[j], bb[j]))
            mj.append(g.XOR(g.AND(ab[j], prev[j]), bb[j]))
        prev = ab
        t2 = g.add(S0, mj)
        a, bb, c, d, e, f, h2, h = g.add(t1, t2), a, bb, c, g.add(d, t1), e, f, h2
    st7 = [t for w in (a, bb, c, d, e, f, h2, h) for t in w] + prev
    sets_C = sum(1 for t in st7 if t[0] == 0)
    nots_C = sum(1 for t, q in zip(st7, comp_pol) if t[0] != 0 and t[1] != q)
    gates_AC = live_gates(g, [t for w in Wp for t in w] + ring + st7)
    peak_AC = peak_live(g, gates_AC, ring + st7, set(t[0] for t in g.inputs), set())
    # phase E: feed-forward from a state with polarity comp_pol (separate network)
    g2 = Gen(256)
    sw = [[(g2.inputs[32 * w + j][0], comp_pol[32 * w + j]) for j in range(32)] for w in range(8)]
    out = [g2.add(x, cw(v)) for x, v in zip(sw, IV)]
    outs = [sig_ for k in range(7, -1, -1) for sig_ in out[k]]
    gates_E = live_gates(g2, outs)
    pin = [o[1] for o in outs]
    filt = b.stage1_ops(pin, b.STAGE1_PLANES)
    NET.update(g=g, Wp=Wp, Wp_idx=Wp_idx, ring=ring, st7=st7, g2=g2, outs_E=outs, sc=sc)
    return dict(gates_AC=len(gates_AC), peak_AC=peak_AC, nots_A=nots_A, stores_A=stores_A, sets_B=sets_B, nots_B=nots_B, sets_C=sets_C, nots_C=nots_C,
                gates_E=len(gates_E), filt=filt)


def design(sched_first=15):
    """Rolled program for ROUNDS rounds; the schedule loop covers sched_first..ROUNDS-1 (a multiple of 8 words, or none when
    sched_first >= ROUNDS); the compression loop covers sc..ROUNDS-1 in 4-step iterations, sc = 7 + (ROUNDS - 7) % 4."""
    R = ROUNDS
    if sched_first < R:
        assert (R - sched_first) % 8 == 0 and sched_first >= 15
    n_sched_iter = max(0, (R - sched_first) // 8)
    sc = 7 + (R - 7) % 4
    n_comp_iter = (R - sc) // 4
    # schedule loop polarity fixed point (rings only)
    sp, smm, sr = fixed_point(lambda pol: sched_body(pol, 24), 512)
    cp, cmm, cr = fixed_point(comp_body, 288)
    s = straight_phases(sched_first, sp, cp, sc)
    sched_iter_ops = sr["gates"] + smm + sr["loads"] + sr["stores"] + LOOP_ITER
    comp_iter_ops = cr["gates"] + cmm + cr["loads"] + LOOP_ITER
    straight_ops = (s["gates_AC"] + s["nots_A"] + s["stores_A"] + s["sets_B"] + s["nots_B"] + s["sets_C"] + s["nots_C"]
                    + s["gates_E"] + RESET)
    kernel = straight_ops + n_sched_iter * sched_iter_ops + n_comp_iter * comp_iter_ops   # per batch, before stage-1 and the batch loop
    instr = straight_ops + (sched_iter_ops if n_sched_iter else 0) + comp_iter_ops       # each instruction once in the program
    mem_arrays = (R - sc) * 1024 + n_sched_iter * 8 * 1024        # W' array W'_sc..W'_{R-1} + K array of the schedule loop, 1,024 B per word
    NET.update(sched=sr, comp=cr)
    return dict(rounds=R, sc=sc, comp_iters=n_comp_iter, sched_first=sched_first, sched_iters=n_sched_iter, sched_gates=sr["gates"], sched_nots=smm, sched_peak=sr["peak"],
                comp_gates=cr["gates"], comp_nots=cmm, comp_peak=cr["peak"], sched_iter_ops=sched_iter_ops, comp_iter_ops=comp_iter_ops,
                straight=s, straight_ops=straight_ops, kernel=kernel, filt=s["filt"], instr=instr, mem_arrays=mem_arrays)


def price(d, R, line_bytes=36):
    """Patch the bsha (v1) ledger with the rolled program: body = kernel + stage-1 + 3; code = (instr + filter + 3 + other code) * 36;
    the W' and K arrays and the R-register file are memory."""
    st = b.step256()
    oc = b.other_code(st)

    def mc(st_=None, R_=R):
        ph = d["kernel"]
        filt = d["filt"]
        body = ph + filt + b.LOOP_OPS
        code = (d["instr"] + filt + b.LOOP_OPS + oc) * line_bytes
        tmax = (b.MEM_LIMIT - code - R_ * 32 - b.COUNTERS - b.ADVICE - d["mem_arrays"]) // b.ENTRY
        return ph, filt, body, code, tmax
    b.machine_constants = mc
    b.REGISTERS, b.REGFILE = R, R * 32
    p = b.plan(256, None, None, R)
    if p is None:
        return None
    lg = b.ledger(p, st, R)
    ls = b.loss(p)
    ph, filt, body, code, tmax = mc()
    return dict(time_log2=log2(lg["total"] / b.UNIT), tmax=p["tmax"], Tp=p["Tp"], body=body, code=code, P_lower=ls["P_lower"],
                memory=code + R * 32 + b.COUNTERS + d["mem_arrays"] + b.ENTRY * p["tmax"], main_share=float(lg["parts"]["main"] / lg["total"]))


if __name__ == "__main__":
    import time
    t0 = time.time()
    out = {}
    for sf in (15, 16, 23, 31, 39):
        d = design(sf)
        out[sf] = d
        print(json.dumps({k: v for k, v in d.items()}, default=str))
    print("seconds", round(time.time() - t0, 1))
    json.dump(out, open(os.path.join(HERE, "design_counts.json"), "w"), indent=1, default=str)
