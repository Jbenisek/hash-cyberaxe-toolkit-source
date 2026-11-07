"""Execute the counted rolled program (the same Gen networks rolled.design() counts) on 256 lanes and compare every lane with the
scalar 39-step digest of bsha.f_scalar (the build/c scalar, itself checked against the organizer reference in r39 BUILD.md).
Usage: python verify.py SEED   (lanes: 254 random values, all-zero, all-ones)."""
import sys, os, random
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rolled
b = rolled.b
ALL = (1 << 256) - 1
M32 = 0xFFFFFFFF


def ev(g, inp):
    v = [0] * len(g.nodes)
    for k in range(1, len(g.nodes)):
        nd = g.nodes[k]
        o = nd[0]
        if o == "v":
            v[k] = inp[nd[1]]
        elif o == "x":
            v[k] = v[nd[1]] ^ v[nd[2]]
        elif o == "a":
            v[k] = v[nd[1]] & v[nd[2]]
        else:
            v[k] = v[nd[1]] | v[nd[2]]
    return v


def tv(v, s):
    return v[s[0]] ^ (ALL if s[1] else 0)


def bcast(word):
    return [ALL if (word >> j) & 1 else 0 for j in range(32)]


def run(sf, xs):
    d = rolled.design(sf)
    N = rolled.NET
    planes = [sum(((x >> j) & 1) << l for l, x in enumerate(xs)) for j in range(256)]
    v = ev(N["g"], planes)
    Wp = {}
    for idx, w in zip(N["Wp_idx"], N["Wp"]):
        Wp[idx] = [tv(v, s) for s in w]                       # stored upright (a complemented plane gets its counted NOT)
    for i in (13, 14, 15):
        Wp.setdefault(i, bcast((rolled.K[i] + b.TAIL[i - 13]) & M32))   # constants written at setup (the loop overwrites W'_15 when it starts at 15)
    if d["sched_iters"]:
        sr = N["sched"]
        ring = [tv(v, s) ^ (ALL if p else 0) for s, p in zip(N["ring"], sr["pol"])]       # stored = true xor loop polarity
        for t in range(d["sched_iters"]):
            first = sf + 8 * t
            kin = []
            for p in range(8):
                i = first + p
                kw = rolled.K[i]
                kin += [(ALL if (kw >> j) & 1 else 0) ^ (ALL if sr["knobs"][p][j] else 0) for j in range(32)]
            vv = ev(sr["g"], ring + kin)
            for p in range(8):
                Wp[first + p] = [tv(vv, s) for s in sr["Wouts"][p]]
            ring = [vv[s[0]] for s in sr["outs_ring"]]        # out polarity = in polarity (fixed point, 0 corrections)
    cr = N["comp"]
    state = [tv(v, s) ^ (ALL if p else 0) for s, p in zip(N["st7"], cr["pol"])]
    for t in range(d["comp_iters"]):
        wl = []
        for s4 in range(4):
            wl += Wp[d["sc"] + 4 * t + s4]
        vv = ev(cr["g"], state + wl)
        state = [vv[s[0]] for s in cr["outs"]]
    v2 = ev(N["g2"], state[:256])
    out = [tv(v2, s) for s in N["outs_E"]]
    bad = 0
    for l, x in enumerate(xs):
        got = sum(((out[j] >> l) & 1) << j for j in range(256))
        if got != b.f_scalar(x, 256):
            bad += 1
    return bad, d


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    R = int(sys.argv[2]) if len(sys.argv) > 2 else 39
    rolled.set_rounds(R)
    rnd = random.Random(seed)
    xs = [rnd.getrandbits(256) for _ in range(254)] + [0, (1 << 256) - 1]
    for sf in [R] + [s for s in range(15, R) if (R - s) % 8 == 0]:
        bad, d = run(sf, xs)
        print("seed", seed, "rounds", R, "sched_first", sf, "lanes", len(xs), "mismatches", bad, "kernel", d["kernel"], "instr", d["instr"])
