"""Validate the front-line residual samples (rand/, ctx/) written by gen.c.

Per sampled row (1,000 per set): rebuild the pair from its free inputs with pkgCG frontline.py (step CO + step CT),
compress both blocks with the ORGANIZER blake3.py _compress (rounds=2, counter t, flags 3), and compare every stored
column; K1/K3 also recomputed from E-inputs only with pkg13/mitm/check.py key1/key3. Whole-set identities by numpy.
No file outside perspectives/data is written (bytecode writing disabled).
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

import sys
sys.dont_write_bytecode = True
import hashlib, importlib.util, os, random, struct
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WS = _hca_public_path_text('__HCA_WORKSPACE__/')
SRC = {
    "b3": WS + r"\hash-smash\verifier\blake3.py",
    "fl": WS + r"\research\tools\build_pkg\scratch\pkgCG\pkg\blake3-r2\experiments\frontline.py",
    "ck": WS + r"\research\pkg13\mitm\check.py",
}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


b3, fl, ck = load("b3", SRC["b3"]), load("frontline", SRC["fl"]), load("check", SRC["ck"])
M = 0xFFFFFFFF
QMASK, QVALUE = 0x0E09818B, 0x02008000
COLS = {"inputs": 12, "einputs": 9, "dig": 8, "eout": 16, "emid": 16, "keys": 8, "res": 4}
IDX = (1, 3, 4, 6)
DG = ((0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
CL = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15))


def pdep(x, mask):
    r, n = 0, 0
    for i in range(32):
        if mask >> i & 1:
            r |= (x >> n & 1) << i
            n += 1
    return r


def org_trace(words, t, blen):
    'Organizer _g step by step (2 rounds): state after round-2 columns and final state; cross-checked to _compress.'
    v = list(b3.IV) + list(b3.IV[:4]) + [t & M, t >> 32, blen, 3]
    m = list(words)
    ys = None
    for r in range(2):
        for a, b, c, d in CL:
            j = CL.index((a, b, c, d))
            b3._g(v, a, b, c, d, m[2 * j], m[2 * j + 1])
        if r == 1:
            ys = list(v)
        for k, (a, b, c, d) in enumerate(DG):
            b3._g(v, a, b, c, d, m[8 + 2 * k], m[9 + 2 * k])
        m = [m[i] for i in b3.PERMUTATION]
    return ys, v


def load_set(name):
    d = os.path.join(HERE, name)
    out = {}
    for f, c in COLS.items():
        a = np.fromfile(os.path.join(d, f + ".u32"), dtype="<u4")
        out[f] = a.reshape(-1, c)
    n = {f: a.shape[0] for f, a in out.items()}
    assert len(set(n.values())) == 1, n
    return out


def whole_set(name, S):
    'Identities on every row (numpy).'
    inp, dig, eo, em, keys, res = S["inputs"], S["dig"], S["eout"], S["emid"], S["keys"], S["res"]
    e1a, e1b, e3a, e3b = eo[:, 0:4], eo[:, 4:8], eo[:, 8:12], eo[:, 12:16]
    rep = {}
    rep["rows"] = int(inp.shape[0])
    rep["res == digA^digB"] = int(np.sum(np.any(res != (dig[:, :4] ^ dig[:, 4:]), axis=1)))
    rep["res == K1^K3"] = int(np.sum(np.any(res != (keys[:, :4] ^ keys[:, 4:]), axis=1)))
    K1 = np.stack([e1a[:, 0] ^ e1b[:, 0], e1a[:, 2] ^ e1b[:, 2], e1a[:, 3] ^ e1b[:, 3], e1a[:, 1] ^ e1b[:, 1]], 1)
    K3 = np.stack([e3a[:, 2] ^ e3b[:, 2], e3a[:, 0] ^ e3b[:, 0], e3a[:, 1] ^ e3b[:, 1], e3a[:, 3] ^ e3b[:, 3]], 1)
    rep["K1 from eout"] = int(np.sum(np.any(K1 != keys[:, :4], axis=1)))
    rep["K3 from eout"] = int(np.sum(np.any(K3 != keys[:, 4:], axis=1)))
    for s, (ea, e3) in (("A", (e1a, e3a)), ("B", (e1b, e3b))):
        D = np.stack([ea[:, 0] ^ e3[:, 2], ea[:, 2] ^ e3[:, 0], ea[:, 3] ^ e3[:, 1], ea[:, 1] ^ e3[:, 3]], 1)
        off = 0 if s == "A" else 4
        rep["dig%s from eout" % s] = int(np.sum(np.any(D != dig[:, off:off + 4], axis=1)))
    rep["c1 in Q*"] = int(np.sum((inp[:, 10] & QMASK) != QVALUE))
    rep["e1 in class"] = int(np.sum(((inp[:, 9].astype(np.uint64) + 0x8127C181) & M & 0x03CF8303) != 0x030C0303))
    rep["t != 0"] = int(np.sum(inp[:, 11] == 0))
    rep["dh1 = eta"] = int(np.sum((em[:, 11] ^ em[:, 15]) != 0x830303CF))
    rep["emid E1.c1(A) = c1"] = int(np.sum(em[:, 2] != inp[:, 10]))
    return rep


def per_row(name, S, n, seed):
    rnd = random.Random(seed)
    rows = rnd.sample(range(S["inputs"].shape[0]), n)
    bad = {k: 0 for k in ("member/Y4", "c1 from j", "t", "einputs", "org _compress vs trace", "words 0,2,5,7 equal",
                          "dig stored", "res stored", "eout stored", "emid stored", "keys vs check.py key1/key3",
                          "res = K1^K3 (check.py)", "frontline chart cons", "frontline compress2")}
    for r in rows:
        inp = [int(x) for x in S["inputs"][r]]
        ow, k, j, Y4, c1, t = inp[:7], inp[7], inp[8], inp[9], inp[10], inp[11]
        e1, y = fl.member(k)
        bad["member/Y4"] += y != Y4
        bad["c1 from j"] += (QVALUE | pdep(j, ~QMASK & M)) != c1
        v = fl.rebuild(ow, y, e1)
        u = fl.step_ct(v, c1)
        bad["t"] += u["t"] != t
        ein = [u["Y1"], u["Y6"], u["Y12"], u["w12"], u["w5"], u["Y4"], u["Y9"], u["Y14"], u["w8"]]
        bad["einputs"] += ein != [int(x) for x in S["einputs"][r]]
        wa = struct.unpack("<16I", u["A"].ljust(64, b"\0"))
        wb = struct.unpack("<16I", u["B"].ljust(64, b"\0"))
        da = b3._compress(b3.IV, wa, t, len(u["A"]), 3, 2)[:8]
        db = b3._compress(b3.IV, wb, t, len(u["B"]), 3, 2)[:8]
        (ysa, va), (ysb, vb) = org_trace(wa, t, 55), org_trace(wb, t, 63)
        bad["org _compress vs trace"] += (tuple(va[i] ^ va[i + 8] for i in range(8)) != da or
                                          tuple(vb[i] ^ vb[i + 8] for i in range(8)) != db)
        bad["words 0,2,5,7 equal"] += any(da[i] != db[i] for i in (0, 2, 5, 7))
        bad["dig stored"] += [da[i] for i in IDX] + [db[i] for i in IDX] != [int(x) for x in S["dig"][r]]
        bad["res stored"] += [da[i] ^ db[i] for i in IDX] != [int(x) for x in S["res"][r]]
        eo = [va[1], va[6], va[11], va[12], vb[1], vb[6], vb[11], vb[12],
              va[3], va[4], va[9], va[14], vb[3], vb[4], vb[9], vb[14]]
        bad["eout stored"] += eo != [int(x) for x in S["eout"][r]]
        mids = []
        for ys, w in ((ysa, wa), (ysb, wb)):
            mp = [w[p] for p in b3.PERMUTATION]                      # round-2 message words
            q = [ys[1], ys[6], ys[11], ys[12]]
            q[0] = (q[0] + q[1] + mp[10]) & M; q[3] = b3._ror(q[3] ^ q[0], 16); q[2] = (q[2] + q[3]) & M; q[1] = b3._ror(q[1] ^ q[2], 12)
            mids.append(q)
        for ys, w in ((ysa, wa), (ysb, wb)):
            mp = [w[p] for p in b3.PERMUTATION]
            q = [ys[3], ys[4], ys[9], ys[14]]
            q[0] = (q[0] + q[1] + mp[14]) & M; q[3] = b3._ror(q[3] ^ q[0], 16); q[2] = (q[2] + q[3]) & M; q[1] = b3._ror(q[1] ^ q[2], 12)
            mids.append(q)
        bad["emid stored"] += sum(mids, []) != [int(x) for x in S["emid"][r]]
        k1 = ck.key1(u["Y12"], (u["Y1"] + u["w12"]) & M, u["w5"], c1)
        k3 = ck.key3(u["Y4"], u["Y9"], u["w8"], u["E3_h1"])
        bad["keys vs check.py key1/key3"] += [k1[i] for i in IDX] + [k3[i] for i in IDX] != [int(x) for x in S["keys"][r]]
        bad["res = K1^K3 (check.py)"] += any(k1[i] ^ k3[i] != da[i] ^ db[i] for i in IDX)
        ch = fl.chart(u)
        bad["frontline chart cons"] += not ch["cons"]
        bad["frontline compress2"] += tuple(ch["cva"]) != da or tuple(ch["cvb"]) != db
    return n, bad


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


if __name__ == "__main__":
    print("sources (sha256/16):", {k: sha(p) for k, p in SRC.items()})
    alt = WS + r"\research\frontline\program\frontline.py"
    if os.path.exists(alt):
        print("research/frontline/program/frontline.py same bytes as pkgCG copy:", sha(alt) == sha(SRC["fl"]))
    total_fail = 0
    for name, seed in (("rand", 101), ("ctx", 102)):
        S = load_set(name)
        rep = whole_set(name, S)
        print("[%s] whole-set identity failures:" % name, rep)
        total_fail += sum(v for k, v in rep.items() if k != "rows")
        n, bad = per_row(name, S, 1000, seed)
        print("[%s] %d rows vs organizer blake3.py + frontline.py + check.py, failures:" % (name, n), bad)
        total_fail += sum(bad.values())
    print("TOTAL FAILURES", total_fail)
