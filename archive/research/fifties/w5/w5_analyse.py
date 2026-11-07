#!/usr/bin/env python3
"""w5_analyse.py - lever 14: E1L / E1a rate split by the context word w5 (prereg8 member-loop data).

  python3 -B w5_analyse.py main      discovery: prereg8 main/ ctx-arm records (2^18 contexts, 2^46 trials);
                                     verifies every ctx-arm E1L hit by a Python re-computation (validates the w5 port),
                                     writes main_stats.json and selection.json (the classes the fresh run will test)
  python3 -B w5_analyse.py fresh     confirmation on fresh/ (new label keys); writes fresh_stats.json, confirm.json
  python3 -B w5_analyse.py x9        checks that X9 alone sets w5 (other six outer words fixed); writes x9_check.json
Standard library only. Reads prereg8 files read-only; writes only next to this script.
"""
import glob
import hashlib
import json
import math
import os
import random
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P8 = os.path.join(HERE, "..", "..", "impl", "memberloop", "prereg8")
M = 0xFFFFFFFF
EPS = 0x6E21BE55
BETA_STAR = 0x18B0E098
TAU_S = (0x175020A0, 0x185020A0, 0x275020A0, 0x285020A0, 0x385020A0, 0x685020A0)
TRIALS_PER_CTX = (1 << 19) * 512


def ror(x, r):
    x &= M
    return ((x >> r) | (x << (32 - r))) & M


def rol(x, r):
    return ror(x, 32 - r)


# ---- generators (copied from prereg8/ref8.py) ---------------------------------------------------------------------
def philox(c, k):
    c0, c1, c2, c3 = c
    k0, k1 = k
    for _ in range(10):
        p0, p1 = 0xD2511F53 * c0, 0xCD9E8D57 * c2
        c0, c1, c2, c3 = (p1 >> 32) ^ c1 ^ k0, p1 & M, (p0 >> 32) ^ c3 ^ k1, p0 & M
        k0, k1 = (k0 + 0x9E3779B9) & M, (k1 + 0xBB67AE85) & M
    return [c0, c1, c2, c3]


def gen_words(gen, keyhex, arm, block, member, purpose):
    if gen == 1:
        kb = bytes.fromhex(keyhex)
        k = struct.unpack(">2I", kb[:8])
        return philox((member, block, arm, 2 * purpose), k) + philox((member, block, arm, 2 * purpose + 1), k)
    d = hashlib.sha256(bytes.fromhex(keyhex) + struct.pack(">IIII", arm, block, member, purpose)).digest()
    return list(struct.unpack(">8I", d))


# ---- automatic transcription of prereg8/lines8.cuh (ctx_pre8, mem_eval8) -------------------------------------------
SRC = open(os.path.join(P8, "lines8.cuh")).read()
CONST = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"#define (C8_\w+) (0x[0-9a-fA-F]+)u", SRC)}
FREE = [int(x) for x in re.search(r"C8_FREE\[19\] = \{([^}]*)\}", SRC).group(1).split(",")]


def _body(fname):
    i = SRC.index(fname + "(")
    j = SRC.index("{", i)
    k = SRC.index("\n}", j)
    return SRC[j + 1:k]


def _tr(expr):
    e = re.sub(r"(0x[0-9a-fA-F]+)u", r"\1", expr).replace("d8_ror", "ror")
    e = e.replace("C->", "C_")
    return e


def _build(fname, arg):
    out = ["def %s(%s, C=None):" % (fname, arg)]
    for line in _body(fname).splitlines():
        m = re.match(r"\s*u32 (v_\w+) = (.+);\s*$", line)
        if m:
            name, ex = m.group(1), _tr(m.group(2))
            if fname == "mem_eval8" and ex.startswith("C_"):
                out.append("  %s = C[%r]" % (name, ex[2:]))
            else:
                out.append("  %s = (%s) & 0xFFFFFFFF" % (name, ex))
    out.append("  return {q: v for q, v in locals().items() if q.startswith('v_')}")
    return "\n".join(out)


exec(_build("ctx_pre8", "ow"))
exec(_build("mem_eval8", "v_Y4"))


def member_y8(mnum):
    w = 0
    for n in range(19):
        w |= ((mnum >> n) & 1) << FREE[n]
    return ((CONST["C8_CLASS_VALUE"] | (w & CONST["C8_FREE_MASK"])) - CONST["C8_Y3A"]) & M


def ctx_of(gen, keyhex, block):
    return ctx_pre8(gen_words(gen, keyhex, 0, block, 0xFFFFFFFF, 0)[:7])


def e1_trial(C, mnum, c1):
    y = member_y8(mnum)
    V = mem_eval8(y, C)
    Y12, KY, w5 = V["v_Y12"], (V["v_Y1"] + C["v_w12"]) & M, C["v_w5"]
    w5b = (w5 + CONST["C8_DELTA5"]) & M
    d1 = (c1 - CONST["C8_Y11A"]) & M
    a1 = rol(d1, 16) ^ Y12
    y6 = (a1 - KY) & M
    b1 = ror(y6 ^ c1, 12)
    a2 = (a1 + b1 + w5) & M
    c2 = (c1 + ror(d1 ^ a2, 8)) & M
    c1b = (CONST["C8_Y11B"] + d1) & M
    b1b = ror(y6 ^ c1b, 12)
    a2b = (a1 + b1b + w5b) & M
    c2b = (c1b + ror(d1 ^ a2b, 8)) & M
    return a2 ^ a2b, c2 ^ c2b, b1 ^ b1b


# ---- record and hit files -------------------------------------------------------------------------------------------
def read_rec(path):
    b = open(path, "rb").read()
    hdr = struct.unpack("<8I", b[:32])
    assert hdr[0] == 0x38475250
    nb, nrec = hdr[4], hdr[7]
    r = struct.unpack("<%dQ" % (nrec * nb), b[32:32 + 8 * nrec * nb])
    return hdr, [r[nrec * i:nrec * (i + 1)] for i in range(nb)]


def read_hits(path):
    b = open(path, "rb").read()
    n = struct.unpack("<I", b[:4])[0]
    return [struct.unpack("<16I", b[4 + 64 * i:4 + 64 * (i + 1)]) for i in range(n)]


def load(files):
    """files: list of (bin, hits, gen, keyhex). Returns contexts [(w5, nE1a, nE1L, trials)] and hit check counts."""
    ctxs, hit_ok, hit_bad = [], 0, 0
    for fb, fh, gen, key in files:
        hdr, recs = read_rec(fb)
        assert hdr[1] == 0 and hdr[2] == gen and hdr[5] == 1 << 19 and hdr[6] == 512
        b0 = hdr[3]
        for i, r in enumerate(recs):
            C = ctx_of(gen, key, b0 + i)
            assert r[15] == TRIALS_PER_CTX and r[12] == 0
            ctxs.append((C["v_w5"], r[2], r[3], r[15], gen))
        if fh and os.path.exists(fh):
            for h in read_hits(fh):
                if not (h[6] & 2):
                    continue
                assert h[0] == 0 and h[1] == gen
                C = ctx_of(gen, key, h[2])
                tau, eps, beta = e1_trial(C, h[3], h[5])
                if tau == h[7] and eps == h[8] == EPS and tau in TAU_S and beta == BETA_STAR:
                    hit_ok += 1
                else:
                    hit_bad += 1
    return ctxs, hit_ok, hit_bad


# ---- statistics ---------------------------------------------------------------------------------------------------
def classes(ctxs, key):
    d = {}
    for w5, na, nl, t, g in ctxs:
        c = key(w5)
        e = d.setdefault(c, [0, 0, 0, 0.0, 0.0])   # contexts, nE1a, nE1L, sum x, sum x^2 (x = E1a per ctx)
        e[0] += 1; e[1] += na; e[2] += nl; e[3] += na; e[4] += na * na
    return d


def summarise(ctxs):
    T = sum(c[3] for c in ctxs)
    NA = sum(c[1] for c in ctxs)
    NL = sum(c[2] for c in ctxs)
    n = len(ctxs)
    mA = NA / n
    varA = sum((c[1] - mA) ** 2 for c in ctxs) / (n - 1)
    out = dict(contexts=n, trials=T, log2_trials=math.log2(T), E1a=NA, E1L=NL,
               E1a_rate_log2=math.log2(NA / T), E1L_rate_log2=math.log2(NL / T) if NL else None,
               E1a_ctx_var_over_mean=varA / mA)
    rateL, rateA = NL / T, NA / T

    def cls_row(e, ntot):
        k, na, nl, sx, sxx = e
        tl = k * TRIALS_PER_CTX
        rl = (nl / tl) / rateL
        sel = math.sqrt(nl) / tl / rateL if nl else float("nan")
        # E1a: between-context SE of the class mean, ratio to the overall mean
        ma = sx / k
        va = (sxx - k * ma * ma) / (k - 1) if k > 1 else float("nan")
        ra = ma / mA
        sea = math.sqrt(va / k) / mA if k > 1 else float("nan")
        return dict(ctx=k, E1L=nl, E1L_ratio=rl, E1L_se=sel, E1a_ratio=ra, E1a_se=sea)

    bits = []
    for i in range(32):
        d = classes(ctxs, lambda w, i=i: (w >> i) & 1)
        r0, r1 = cls_row(d[0], n), cls_row(d[1], n)
        # rate ratio bit=1 / bit=0
        RL = (d[1][2] / d[1][0]) / (d[0][2] / d[0][0])
        seRL = RL * math.sqrt(1 / d[1][2] + 1 / d[0][2])
        RA = r1["E1a_ratio"] / r0["E1a_ratio"]
        seRA = RA * math.sqrt((r1["E1a_se"] / r1["E1a_ratio"]) ** 2 + (r0["E1a_se"] / r0["E1a_ratio"]) ** 2)
        bits.append(dict(bit=i, v0=r0, v1=r1, E1L_R10=RL, E1L_R10_se=seRL, E1L_z=(RL - 1) / seRL,
                         E1a_R10=RA, E1a_R10_se=seRA, E1a_z=(RA - 1) / seRA))
    out["bits"] = bits
    d = classes(ctxs, lambda w: w & 0xFF)
    rows = {c: cls_row(d[c], n) for c in sorted(d)}
    # homogeneity: E1L Poisson chi^2 (df 255), E1a between-context chi^2 (df 255)
    chiL = sum((rows[c]["E1L"] - NL * rows[c]["ctx"] / n) ** 2 / (NL * rows[c]["ctx"] / n) for c in rows)
    chiA = sum(((rows[c]["E1a_ratio"] - 1) / (math.sqrt(varA / rows[c]["ctx"]) / mA)) ** 2 for c in rows)
    out["byte_classes"] = len(rows)
    out["byte_chi2_E1L"], out["byte_chi2_E1a"], out["byte_df"] = chiL, chiA, len(rows) - 1
    out["byte_rows"] = {str(c): rows[c] for c in rows}
    bestL = max(rows, key=lambda c: rows[c]["E1L_ratio"])
    bestA = max(rows, key=lambda c: rows[c]["E1a_ratio"])
    out["byte_best_E1L"] = dict(byte=bestL, **rows[bestL])
    out["byte_best_E1a"] = dict(byte=bestA, **rows[bestA])
    bb = []
    for b in bits:
        for v in (0, 1):
            r = b["v%d" % v]
            bb.append((r["E1L_ratio"], b["bit"], v, r))
    bb.sort(reverse=True)
    out["bit_best_E1L"] = dict(bit=bb[0][1], value=bb[0][2], **bb[0][3])
    ba = sorted(((b["v%d" % v]["E1a_ratio"], b["bit"], v, b["v%d" % v]) for b in bits for v in (0, 1)), reverse=True)
    out["bit_best_E1a"] = dict(bit=ba[0][1], value=ba[0][2], **ba[0][3])
    out["max_abs_bit_z_E1L"] = max(abs(b["E1L_z"]) for b in bits)
    out["max_abs_bit_z_E1a"] = max(abs(b["E1a_z"]) for b in bits)
    return out


def main_files():
    import importlib.util
    spec = importlib.util.spec_from_file_location("seeds", os.path.join(P8, "seeds.py"))
    S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
    key = {1: S.keyhex("main", 1), 2: S.keyhex("main", 2)}
    files = []
    for fb in sorted(glob.glob(os.path.join(P8, "main", "s*_a0_g*.bin"))):
        g = int(fb[-5])
        files.append((fb, fb[:-4] + ".hits", g, key[g]))
    return files


def fresh_files():
    K = json.load(open(os.path.join(HERE, "fresh", "keys.json")))
    files = []
    for fb in sorted(glob.glob(os.path.join(HERE, "fresh", "s*_g*.bin"))):
        g = int(fb[-5])
        files.append((fb, fb[:-4] + ".hits", g, K["key_g%d" % g]))
    return files


def brief(s):
    q = {k: s[k] for k in ("contexts", "log2_trials", "E1a", "E1L", "E1a_rate_log2", "E1L_rate_log2",
                           "E1a_ctx_var_over_mean", "byte_chi2_E1L", "byte_chi2_E1a", "byte_df",
                           "max_abs_bit_z_E1L", "max_abs_bit_z_E1a")}
    q["bit_best_E1L"], q["bit_best_E1a"] = s["bit_best_E1L"], s["bit_best_E1a"]
    q["byte_best_E1L"], q["byte_best_E1a"] = s["byte_best_E1L"], s["byte_best_E1a"]
    return q


def class_rate(ctxs, pred, NLall, NAall, T):
    k = sum(1 for c in ctxs if pred(c[0]))
    nl = sum(c[2] for c in ctxs if pred(c[0]))
    xs = [c[1] for c in ctxs if pred(c[0])]
    n = len(ctxs)
    rl = (nl / (k * TRIALS_PER_CTX)) / (NLall / T)
    sel = math.sqrt(nl) / (k * TRIALS_PER_CTX) / (NLall / T) if nl else float("nan")
    mA = NAall / n
    m = sum(xs) / k
    v = sum((x - m) ** 2 for x in xs) / (k - 1)
    return dict(ctx=k, E1L=nl, E1L_ratio=rl, E1L_se=sel, E1L_gain_bits=math.log2(rl) if rl > 0 else None,
                E1a_ratio=m / mA, E1a_se=math.sqrt(v / k) / mA, E1a_gain_bits=math.log2(m / mA))


def table():
    """per-bit E1L and E1a ratios (bit=1 / bit=0) for main, fresh and pooled; pooled best bit class; table.md"""
    A = json.load(open(os.path.join(HERE, "main_stats.json")))
    B = json.load(open(os.path.join(HERE, "fresh_stats.json")))
    lines = ["| bit | E1L R10 main | E1L R10 fresh | E1L R10 pooled | z pooled | E1a R10 pooled (x1e5 - 1e5) | z |",
             "|---:|---:|---:|---:|---:|---:|---:|"]
    pooled, best = [], None
    for i in range(32):
        a, b = A["bits"][i], B["bits"][i]
        n1 = a["v1"]["E1L"] + b["v1"]["E1L"]; n0 = a["v0"]["E1L"] + b["v0"]["E1L"]
        c1 = a["v1"]["ctx"] + b["v1"]["ctx"]; c0 = a["v0"]["ctx"] + b["v0"]["ctx"]
        R = (n1 / c1) / (n0 / c0); se = R * math.sqrt(1 / n1 + 1 / n0)
        wa, wb = 1 / a["E1a_R10_se"] ** 2, 1 / b["E1a_R10_se"] ** 2
        RA = (a["E1a_R10"] * wa + b["E1a_R10"] * wb) / (wa + wb); seA = 1 / math.sqrt(wa + wb)
        pooled.append(dict(bit=i, E1L_R10=R, se=se, z=(R - 1) / se, E1a_R10=RA, E1a_se=seA, E1a_z=(RA - 1) / seA))
        lines.append("| %d | %.4f ± %.4f | %.4f ± %.4f | %.4f ± %.4f | %+.2f | %+.2f ± %.2f | %+.2f |" % (
            i, a["E1L_R10"], a["E1L_R10_se"], b["E1L_R10"], b["E1L_R10_se"], R, se, (R - 1) / se,
            (RA - 1) * 1e5, seA * 1e5, (RA - 1) / seA))
        # pooled class ratio to the overall rate for each value
        NL = A["E1L"] + B["E1L"]; NC = A["contexts"] + B["contexts"]
        for v, n, c in ((1, n1, c1), (0, n0, c0)):
            r = (n / c) / (NL / NC)
            if best is None or r > best["ratio"]:
                best = dict(bit=i, value=v, ratio=r, se=math.sqrt(n) / c / (NL / NC), gain_bits=math.log2(r),
                            gain_se=math.sqrt(n) / c / (NL / NC) / r / math.log(2))
    out = dict(pooled=pooled, pooled_best_bit_class_E1L=best,
               max_abs_z_E1L=max(abs(p["z"]) for p in pooled), max_abs_z_E1a=max(abs(p["E1a_z"]) for p in pooled),
               chi2_bits_E1L=sum(p["z"] ** 2 for p in pooled), chi2_bits_E1a=sum(p["E1a_z"] ** 2 for p in pooled))
    json.dump(out, open(os.path.join(HERE, "pooled.json"), "w"), indent=1)
    open(os.path.join(HERE, "bits_table.md"), "w").write("\n".join(lines) + "\n")
    print(json.dumps({k: out[k] for k in out if k != "pooled"}, indent=1))


def cmd(mode):
    if mode == "table":
        table()
        return
    if mode == "x9":
        rnd = random.Random(14)
        ok, changed = 0, set()
        for _ in range(2000):
            ow = [rnd.getrandbits(32) for _ in range(7)]
            target = rnd.getrandbits(32)
            C0 = ctx_pre8(ow)
            # invert the X9 -> w5 chain (lines8.cuh lines 64, 67, 74, 82, 90)
            D3_a1 = C0["v_D3_a1"]; D3_c1 = C0["v_D3_c1"]
            S2 = (target + 0xF33A2355 + 0xF0740523) & M
            S14 = rol(S2 ^ 0x2362F33A, 24)
            D3_d1 = rol(S14 ^ D3_a1, 16)
            X14 = rol(D3_d1 ^ 0x29D4FA98, 24)
            ow2 = list(ow); ow2[5] = (X14 + D3_c1) & M
            C1 = ctx_pre8(ow2)
            ok += C1["v_w5"] == target
            changed |= {q for q in C1 if C1[q] != C0[q]}
        out = dict(trials=2000, w5_hit=ok, outer_words_changed=["ow[5]=X9 only"],
                   derived_values_changed=sorted(changed))
        json.dump(out, open(os.path.join(HERE, "x9_check.json"), "w"), indent=1)
        print(json.dumps(out))
        return
    files = main_files() if mode == "main" else fresh_files()
    ctxs, ok, bad = load(files)
    s = summarise(ctxs)
    s["E1L_hits_verified_ok"], s["E1L_hits_verified_bad"] = ok, bad
    s["files"] = len(files)
    for g in (1, 2):
        cg = [c for c in ctxs if c[4] == g]
        if cg:
            sg = summarise(cg)
            s["gen%d" % g] = brief(sg)
    json.dump(s, open(os.path.join(HERE, "%s_stats.json" % mode), "w"), indent=1)
    b = brief(s)
    b["hits_ok"], b["hits_bad"] = ok, bad
    print(json.dumps(b, indent=1))
    if mode == "main":
        sel = dict(note="chosen from main (discovery) data only, before any fresh data was analysed",
                   bit_E1L=[s["bit_best_E1L"]["bit"], s["bit_best_E1L"]["value"]],
                   bit_E1a=[s["bit_best_E1a"]["bit"], s["bit_best_E1a"]["value"]],
                   byte_E1L=s["byte_best_E1L"]["byte"], byte_E1a=s["byte_best_E1a"]["byte"])
        json.dump(sel, open(os.path.join(HERE, "selection.json"), "w"), indent=1)
        print(json.dumps(sel))
    else:
        sel = json.load(open(os.path.join(HERE, "selection.json")))
        T = s["trials"]
        conf = {}
        for name, pred in (("bit_E1L", lambda w, b=sel["bit_E1L"]: ((w >> b[0]) & 1) == b[1]),
                           ("bit_E1a", lambda w, b=sel["bit_E1a"]: ((w >> b[0]) & 1) == b[1]),
                           ("byte_E1L", lambda w, b=sel["byte_E1L"]: (w & 0xFF) == b),
                           ("byte_E1a", lambda w, b=sel["byte_E1a"]: (w & 0xFF) == b)):
            conf[name] = dict(selected=sel[name], **class_rate(ctxs, pred, s["E1L"], s["E1a"], T))
        json.dump(conf, open(os.path.join(HERE, "confirm.json"), "w"), indent=1)
        print(json.dumps(conf, indent=1))


if __name__ == "__main__":
    cmd(sys.argv[1])
