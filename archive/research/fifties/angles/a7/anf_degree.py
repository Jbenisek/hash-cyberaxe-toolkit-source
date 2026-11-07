'''A7 (ANGLES.md section 7): algebraic degree (ANF, Moebius transform) of the stage-A and residual bits.

Part C (the c1 cube of pkg16f, 21 free bits, per frame = the six words ctr_batch reads, from halfsearch.ctr_outer):
  h1 = ROR(Y14 ^ e1, 16) (all 32 bits; rule A reads its parities), the 8 rule-A parities, the rule-A pass flag,
  and the E1 word (zero = hit; the residual), as Boolean functions of the 21 free bits of c1 (ctr_c1 order).
Part Y (the member y of pkg21 outer.py / memberloop.py, 19 free bits, per context = seven outer words):
  omega = Y3 + y + w8 (input of test (2)) and Y9 (input of test (1)), as functions of the 19 member bits.
For every output bit: degree of its ANF and the number of variables its ANF involves. 16 random frames each.
Run: python -B anf_degree.py   (numpy; writes nothing but stdout)
'''
import hashlib, os, struct, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(RES, "pkg16f", "pkg", "blake3-r2", "experiments"))
sys.path.insert(0, os.path.join(RES, "impl", "memberloop"))
sys.path.insert(0, os.path.join(RES, "impl"))
import halfsearch as H          # noqa: E402
import outer as O               # noqa: E402
import memberloop as ML         # noqa: E402

M = 0xFFFFFFFF
U = np.uint64


def rorv(x, n):
    return ((x >> U(n)) | (x << U(32 - n))) & U(M)


def rolv(x, n):
    return rorv(x, (32 - n) % 32)


def words(tag, i, k):
    return list(struct.unpack("<%dI" % k, hashlib.shake_256(("a7 %s %d" % (tag, i)).encode()).digest(4 * k)))


def moebius(t, n):
    'In-place ANF of 32 packed Boolean functions (uint32 truth table of length 2^n, index bit i = variable i).'
    t = t.copy()
    for i in range(n):
        v = t.reshape(-1, 2, 1 << i)
        v[:, 1, :] ^= v[:, 0, :]
    return t


def profile(anf, n, nbits=32):
    'Per output bit: (degree, number of variables in the ANF, number of monomials).'
    idx = np.arange(1 << n, dtype=np.uint32)
    pc = np.bitwise_count(idx)
    out = []
    for b in range(nbits):
        nz = ((anf >> np.uint32(b)) & np.uint32(1)).astype(bool)
        if not nz.any():
            out.append((-1, 0, 0, 0))
            continue
        deg = int(pc[nz].max())
        vars_ = int(np.bitwise_or.reduce(idx[nz]))
        out.append((deg, bin(vars_).count("1"), int(nz.sum()), vars_))
    return out


# ---------------- Part C: the c1 cube ----------------
NC = len(H.CTR_FREE)
assert NC == 21 and H.CTR_MEMBERS == 1 << 21
j = np.arange(1 << NC, dtype=np.uint64)
C1 = np.full(1 << NC, H.CTR_VALUE, dtype=np.uint64)
for n, i in enumerate(H.CTR_FREE):
    C1 |= ((j >> U(n)) & U(1)) << U(i)


def lanes_c(key):
    y12, q, w5, cb, cc, e1 = (U(x) for x in key)
    c1 = C1
    d1 = (c1 + U((1 << 32) - H.Y11)) & U(M)
    a1 = rolv(d1, 16) ^ y12
    y6 = (a1 + q) & U(M)
    y14 = ((rolv(y6, 7) ^ cb) + (U(1 << 32) - cc)) & U(M)
    h1 = rorv(y14 ^ e1, 16)
    b1 = rorv(c1 ^ y6, 12)
    c2 = (c1 + rorv(((w5 + a1 + b1) & U(M)) ^ d1, 8)) & U(M)
    c1b = (d1 + U(H.Y11B)) & U(M)
    b1b = rorv(c1b ^ y6, 12)
    c2b = (c1b + rorv(((w5 + U(H.DELTA5) + a1 + b1b) & U(M)) ^ d1, 8)) & U(M)
    eps = c2 ^ c2b
    word = U(H.ETA) ^ eps ^ rolv(U(H.CTR_BETA) ^ eps, 1)
    cond = np.zeros(1 << NC, dtype=np.uint64)
    ok = np.ones(1 << NC, dtype=bool)
    for k, (mask, value) in enumerate(H.RULE_A):
        par = (np.bitwise_count(h1 & U(mask)) & 1).astype(np.uint64) ^ U(value ^ 1)   # 1 = condition holds
        cond |= par << U(k)
        ok &= par.astype(bool)
    cond |= ok.astype(np.uint64) << U(8)
    return h1.astype(np.uint32), cond.astype(np.uint32), word.astype(np.uint32)


def key_of(o):
    return (o["Y12"], (-o["Y1"] - o["w12"]) & M, o["w5"], o["C2.b1"], o["C2.c1"], (H.Y3 + o["Y4"]) & M)


def scalar_lane(key, c1):
    y12, q, w5, cb, cc, e1 = key
    d1 = (c1 - H.Y11) & M
    a1 = H.rol(d1, 16) ^ y12
    y6 = (a1 + q) & M
    y14 = ((H.rol(y6, 7) ^ cb) - cc) & M
    h1 = H.ror(y14 ^ e1, 16)
    b1 = H.ror(c1 ^ y6, 12)
    c2 = (c1 + H.ror(((w5 + a1 + b1) & M) ^ d1, 8)) & M
    c1b = (d1 + H.Y11B) & M
    b1b = H.ror(c1b ^ y6, 12)
    c2b = (c1b + H.ror(((w5 + H.DELTA5 + a1 + b1b) & M) ^ d1, 8)) & M
    eps = c2 ^ c2b
    return H.ETA ^ eps ^ H.rol(H.CTR_BETA ^ eps, 1), int(H.rule_a(h1)), h1


# ---------------- Part Y: the member y of outer.py ----------------
NY = len(O.CLASS_FREE)
assert NY == 19
jy = np.arange(1 << NY, dtype=np.uint64)
E1Y = np.full(1 << NY, O.CLASS_VALUE, dtype=np.uint64)
for n, i in enumerate(O.CLASS_FREE):
    E1Y |= ((jy >> U(n)) & U(1)) << U(i)
YY = (E1Y + U((1 << 32) - O.Y3)) & U(M)


def evv(e, v):
    if isinstance(e, int):
        return U(e)
    if isinstance(e, str):
        return v[e]
    k = e[0]
    if k == "sum":
        s = U(0)
        for t in e[1]:
            if isinstance(t, tuple) and t[0] == "neg":
                s = s + (U(1 << 32) - (evv(t[1], v) & U(M)))
            else:
                s = s + evv(t, v)
        return s & U(M)
    if k == "xor":
        return evv(e[1], v) ^ evv(e[2], v)
    if k == "ror":
        return rorv(evv(e[1], v), e[2])
    raise ValueError(k)


def lanes_y(seven):
    base = ML.context_precompute(dict(zip(O.OUTER_WORDS, seven)))
    v = {k: (U(x) if isinstance(x, int) else x) for k, x in base.items()}
    v["Y4"] = YY
    for name, e in ML.DEP_LINES:
        v[name] = evv(e, v)
    omega = (U(O.Y3) + YY + v["w8"]) & U(M)
    return omega.astype(np.uint32), v["Y9"].astype(np.uint32)


def main():
    frames = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    rep = {"C": [], "Y": []}
    # reference checks (MEASURED): numpy lanes against the scalar formula and against ctr_lane (full compressions)
    badc = totc = badfull = totfull = 0
    for f in range(frames):
        o = H.ctr_outer(words("frame", f, 8))
        key = key_of(o)
        h1, cond, word = lanes_c(key)
        for s in range(64):
            jj = (s * 32771 + f * 977) % (1 << NC)
            c1 = H.ctr_c1(jj)
            w, ra, hh = scalar_lane(key, c1)
            totc += 1
            badc += (int(word[jj]), int(cond[jj] >> 8 & 1), int(h1[jj])) != (w, ra, hh)
        for c1 in H.ctr_table_word((f * 299993) % H.CTR_WORDS)[2]:
            good, ra, w = H.ctr_lane(o, c1)
            if good:
                jj = sum(((c1 >> i) & 1) << n for n, i in enumerate(H.CTR_FREE))
                totfull += 1
                badfull += (int(word[jj]), int(cond[jj] >> 8 & 1)) != (w, ra)
        r = {"h1": profile(moebius(h1, NC), NC), "cond": profile(moebius(cond, NC), NC, 9),
             "word": profile(moebius(word, NC), NC), "passes": int((cond >> 8 & 1).sum()),
             "hits": int((word == 0).sum())}
        rep["C"].append(r)
        print("C frame %2d passA %7d hits %d | h1 deg %s | cond deg %s | word deg(low8) %s" % (
            f, r["passes"], r["hits"], [p[0] for p in r["h1"]], [p[0] for p in r["cond"]],
            [p[0] for p in r["word"][:8]]), flush=True)
    print("C reference: numpy vs scalar %d/%d mismatches, vs ctr_lane (full 2-round) %d/%d mismatches" % (
        badc, totc, badfull, totfull), flush=True)
    bady = toty = 0
    for f in range(frames):
        seven = words("ctx", f, 7)
        om, y9 = lanes_y(seven)
        for s in range(64):
            jj = (s * 8191 + f * 131) % (1 << NY)
            w = 0
            for n, i in enumerate(O.CLASS_FREE):
                w |= ((jj >> n) & 1) << i
            sv = O.scalar_outer(seven + [w])
            toty += 1
            bady += (sv["omega"], sv["Y9"]) != (int(om[jj]), int(y9[jj]))
        r = {"omega": profile(moebius(om, NY), NY), "Y9": profile(moebius(y9, NY), NY)}
        rep["Y"].append(r)
        print("Y frame %2d | omega deg %s | Y9 deg %s" % (
            f, [p[0] for p in r["omega"]], [p[0] for p in r["Y9"]]), flush=True)
    print("Y reference: numpy vs outer.scalar_outer %d/%d mismatches" % (bady, toty), flush=True)
    with open(os.path.join(HERE, "anf_result.json"), "w") as fh:
        json.dump(rep, fh)


if __name__ == "__main__":
    main()
