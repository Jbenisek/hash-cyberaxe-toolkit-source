#!/usr/bin/env python3
# lens EVERY FIGURE: the 287 "violates rule A" questions asked again with an encoder written here and a second
# solver (cadical). Nothing of tools/rule_a_sat.py or research/r2_sat.py is used. CPU only, 4 workers.
# usage: fig_sat2.py <tmpdir> [solver, default cadical]

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

import os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

B = _hca_public_path_text('__HCA_WORKSPACE__/research')
EV = B + "/pkg5/evidence"
TMP = sys.argv[1]
SOLVER = sys.argv[2] if len(sys.argv) > 2 else "cadical"
os.makedirs(TMP, exist_ok=True)
M = 0xFFFFFFFF
ror = lambda v, n: ((v >> n) | (v << (32 - n))) & M
rol = lambda v, n: ror(v, 32 - n)
wt = lambda x: bin(x).count("1")
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)


def G(A, Bq, C, D, x, y):
    a1 = (A + Bq + x) & M; d1 = ror(D ^ a1, 16); c1 = (C + d1) & M; b1 = ror(Bq ^ c1, 12)
    a2 = (a1 + b1 + y) & M; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M; b2 = ror(b1 ^ c2, 7)
    return dict(a1=a1, d1=d1, c1=c1, b1=b1, a2=a2, d2=d2, c2=c2, b2=b2)


X3, X7, X11, X15, W4, W13 = 0xD5D881CA, 0xAA277E35, 0x1F208000, 0x123F2142, 0x7FFFFFFF, 0xFFFD6E01
K = (IV[2] + IV[6]) & M
W4B = ((((K + W4) & M) ^ 2) - K) & M
Y3 = G(X3, X7, X11, X15, W4, W13)["a2"]; Y3B = G(X3, X7, X11, X15, W4B, W13)["a2"]
ETA = 0xE7C1815F
RULE = ((0x00010000, 1), (0x00000003, 0), (0x00000006, 0), (0x0000000C, 0), (0x00000018, 1), (0x01800000, 1))
ruleA = lambda h: all(wt(h & m) & 1 == v for m, v in RULE)


class Cnf:
    def __init__(self):
        self.n = 1; self.cl = [[1]]                 # variable 1 is TRUE
    def new(self):
        self.n += 1; return self.n
    def word(self):
        return [self.new() for _ in range(32)]      # bit 0 first
    def const(self, v):
        return [1 if v >> i & 1 else -1 for i in range(32)]
    def xor(self, a, b):
        if abs(a) == 1: a, b = b, a
        if abs(b) == 1: return a if b == -1 else -a
        c = self.new()
        self.cl += [[-a, -b, -c], [a, b, -c], [a, -b, c], [-a, b, c]]
        return c
    def maj(self, a, b, c):
        m = self.new()
        self.cl += [[-a, -b, m], [-a, -c, m], [-b, -c, m], [a, b, -m], [a, c, -m], [b, c, -m]]
        return m
    def xorw(self, x, y):
        return [self.xor(a, b) for a, b in zip(x, y)]
    def add(self, x, y):
        out, carry = [], -1
        for i in range(32):
            out.append(self.xor(self.xor(x[i], y[i]), carry))
            if i < 31:
                carry = self.maj(x[i], y[i], carry)
        return out
    def force(self, word, value):
        for i, lit in enumerate(word):
            self.cl.append([lit if value >> i & 1 else -lit])
    def write(self, path):
        with open(path, "w") as f:
            f.write("p cnf %d %d\n" % (self.n, len(self.cl)))
            f.write("".join(" ".join(map(str, c)) + " 0\n" for c in self.cl))


rorw = lambda w, n: w[n:] + w[:n]                    # bit i of ROR(w, n) is bit (i + n) mod 32 of w


def build(tau, eps, violate):
    c = Cnf()
    y4, h1, y9, w8 = c.word(), c.word(), c.word(), c.word()
    e1a, e1b = c.add(c.const(Y3), y4), c.add(c.const(Y3B), y4)
    c.force(c.xorw(e1a, e1b), rol(ETA, 16))          # Y4 in the class: h1 XOR h1' = eta
    h1b = c.xorw(h1, c.const(ETA))
    sides = []
    for e1, h in ((e1a, h1), (e1b, h1b)):
        g1 = c.add(y9, h)
        f1 = rorw(c.xorw(y4, g1), 12)
        e2 = c.add(c.add(e1, f1), w8)
        h2 = rorw(c.xorw(h, e2), 8)
        g2 = c.add(g1, h2)
        sides.append((f1, e2, g2))
    c.force(c.xorw(sides[0][0], sides[1][0]), tau ^ ror(tau, 1))     # psi: first-half b difference
    c.force(c.xorw(sides[0][1], sides[1][1]), eps)                   # a output difference
    c.force(c.xorw(sides[0][2], sides[1][2]), tau)                   # c output difference
    if violate:
        lits = []
        for mask, value in RULE:
            x = -1
            for i in range(32):
                if mask >> i & 1:
                    x = c.xor(x, h1[i])
            lits.append(x if value == 0 else -x)     # the literal is true when the condition FAILS
        c.cl.append(lits)
    return c, (y4, h1, y9, w8)


def plain(beta, tau, eps, y4, h1, y9, w8):
    e1 = (Y3 + y4) & M
    y14 = rol(h1, 16) ^ e1
    a, b = G(Y3, y4, y9, y14, 0, w8), G(Y3B, y4, y9, y14, 0, w8)
    return (a["d1"] == h1 and (a["d1"] ^ b["d1"]) == ETA and (a["c2"] ^ b["c2"]) == tau and (a["a2"] ^ b["a2"]) == eps
            and (a["b1"] ^ b["b1"]) == (tau ^ ror(tau, 1)) and (a["b2"] ^ b["b2"]) == ror(tau, 8) and (a["d2"] ^ b["d2"]) == ror(beta ^ eps, 7))


def job(arg):
    mode, (beta, tau, eps) = arg
    c, words = build(int(tau, 16), int(eps, 16), mode == "violate")
    path = os.path.join(TMP, "%s_%s_%s_%s.cnf" % (mode, beta, tau, eps))
    c.write(path)
    cmd = {"cadical": ["cadical", "-q", "-t", "900", path], "cryptominisat5": ["cryptominisat5", "--verb", "0", "--maxtime", "900", path],
           "kissat": ["kissat", "-q", "--time=900", path]}[SOLVER]
    r = subprocess.run(cmd, capture_output=True, text=True)
    os.unlink(path)
    ans, model = "?", {}
    for line in r.stdout.splitlines():
        if line.startswith("s "):
            ans = {"SATISFIABLE": "SAT", "UNSATISFIABLE": "UNSAT"}.get(line[2:].strip(), "?")
        elif line.startswith("v "):
            for tok in line[2:].split():
                v = int(tok)
                if v:
                    model[abs(v)] = v > 0
    res = {"mode": mode, "key": (beta, tau, eps), "ans": ans}
    if ans == "SAT":
        vals = [sum(1 << i for i, b in enumerate(w) if model.get(b, False)) for w in words]
        res["h1"] = vals[1]
        res["ok"] = plain(int(beta, 16), int(tau, 16), int(eps, 16), *vals)
    return res


keys = [(m.group(1), m.group(2), m.group(3)) for m in re.finditer(r"^OUTX e7c1815f ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) E1", open(EV + "/pairs_recount_e7c1815f.txt").read(), re.M)]
theirs = {}
for line in open(EV + "/rule_a_sat_e7c1815f.txt"):
    f = line.split()
    if f and f[0] in ("ALL", "VIOLATE"):
        theirs[(f[0], f[1], f[2], f[3])] = f[4]
jobs = [(mode, k) for mode in ("violate", "all") for k in keys]
with ThreadPoolExecutor(4) as pool:
    res = list(pool.map(job, jobs))
out = open(B + "/pkg5/review/fig_sat2_%s.out" % SOLVER, "w")
vio = [r for r in res if r["mode"] == "violate"]; al = [r for r in res if r["mode"] == "all"]
diff = [r for r in res if theirs.get((r["mode"].upper(),) + r["key"]) != r["ans"]]
print("solver %s, own encoder; outcomes %d" % (SOLVER, len(keys)), file=out)
print("violate: UNSAT %d SAT %d undecided %d ; SAT models that are solutions by own G %d, that violate rule A %d" % (
    sum(r["ans"] == "UNSAT" for r in vio), sum(r["ans"] == "SAT" for r in vio), sum(r["ans"] == "?" for r in vio),
    sum(bool(r.get("ok")) for r in vio), sum(1 for r in vio if r["ans"] == "SAT" and not ruleA(r["h1"]))), file=out)
print("all: SAT %d UNSAT %d undecided %d ; models that are solutions %d ; models that satisfy rule A %d" % (
    sum(r["ans"] == "SAT" for r in al), sum(r["ans"] == "UNSAT" for r in al), sum(r["ans"] == "?" for r in al),
    sum(bool(r.get("ok")) for r in al), sum(1 for r in al if r["ans"] == "SAT" and ruleA(r["h1"]))), file=out)
print("answers that differ from evidence/rule_a_sat_e7c1815f.txt: %d %s" % (len(diff), [(r["mode"],) + r["key"] + (r["ans"],) for r in diff[:5]]), file=out)
for r in res:
    print(r["mode"], *r["key"], r["ans"], ("h1 %08x ok %d ruleA %d" % (r["h1"], r["ok"], ruleA(r["h1"]))) if "h1" in r else "", file=out)
out.close()
print("differ from the package's file:", len(diff), "; violate UNSAT", sum(r["ans"] == "UNSAT" for r in vio), "SAT", sum(r["ans"] == "SAT" for r in vio), "undecided", sum(r["ans"] == "?" for r in res))
