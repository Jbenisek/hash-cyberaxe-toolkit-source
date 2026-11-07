#!/usr/bin/env python3
"""Rule A of the two-stage batch against the solutions of the seven-word system, outcome by outcome, with a SAT solver.
Research helper of the fifth package, not submitted. CPU only.

    python3 -B tools/rule_a_sat.py [threads, default 5]
    python3 -B tools/rule_a_sat.py example      (after the first form; one solver call, one thread)

The outcomes are those of the count of the package: every line OUTX of evidence/pairs_recount_<eta>.txt, that is
every outcome (tau, eps) of every beta of the list whose product P1 * N3 is not zero. For each of them the E3
system is written as CNF from its definition (encoder research/r2_sat.py): unknowns Y4, h1, Y9, w8; E3 evaluated
for message A and for message B (e1' = e1 + DY3, h1' = h1 XOR ROR(e1 XOR e1', 16)); the XOR differences of e1, g1,
e2 and g2 are forced to ROL(eta,16), ROL(tau XOR ROR(tau,1), 12), eps and tau. h1 is the first-half d value of E3
on message A, the word that stage A of the batch tests. Two questions per outcome, answered by kissat:

  all        is the system satisfiable?                 expected: yes. The model is evaluated again in plain
                                                        arithmetic (it must give the four differences).
  violate    system AND "h1 does not satisfy rule A"    UNSATISFIABLE: no solution of this outcome violates
                                                        rule A, so stage A drops none of its solutions.
                                                        SATISFIABLE: the model is a solution that stage A drops;
                                                        it is evaluated again in plain arithmetic.

Result: evidence/rule_a_sat_<eta>.txt, one line per outcome and question, and summary lines. The exit status is 0
when no answer is missing and every model passes its plain-arithmetic check. An UNSATISFIABLE answer is the
solver's; no proof certificate is kept or checked.

The second form completes one of the violating models to a solution of the whole seven-word system. It takes the
outcome with the largest product E1 * N3 among those with a violating model, writes the E1 system of that outcome
as CNF (unknowns d1, b1, a2 and the sum s = a1 + w5; E1 for message A and for message B with Y11' and delta; the
XOR differences of c1, a2 and c2 forced to ROL(beta,12), tau and eps), asks kissat for a model, evaluates E1 and
E3 again in plain arithmetic and appends one line EXAMPLE to the result file.
"""
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS.parent.parent))
import pkg5_data as data  # noqa: E402
import r2_sat  # noqa: E402
from r2_sat import CNF, const32, ror  # noqa: E402

MASK = 0xFFFFFFFF
ETA = data.ETA
RULE = data.RULE_A[ETA]
D = data.derive()
Y3, D3 = D["Y3"], D["DY3"]
TMP = Path(os.path.expanduser("~/hashsmash/pkg5-sat"))
OUT = data.EVID / f"rule_a_sat_{ETA:08x}.txt"
SOURCE = data.EVID / f"pairs_recount_{ETA:08x}.txt"
TIME = 900


def rol(x, n):
    return ((x << n) | (x >> (32 - n))) & MASK


def rorv(x, n):
    return ((x >> n) | (x << (32 - n))) & MASK


def passes(h):
    return all(bin(h & m).count("1") & 1 == v for m, v in RULE)


def build(tau, eps):
    cnf = CNF()
    new = lambda: [cnf.new() for _ in range(32)]  # noqa: E731
    y4, h1, y9, w8 = new(), new(), new(), new()
    e1a = cnf.add32(const32(Y3), y4)
    e1b = cnf.add32(const32((Y3 + D3) & MASK), y4)
    h1b = cnf.xor32(h1, ror(cnf.xor32(e1a, e1b), 16))
    sides = []
    for e1, h in ((e1a, h1), (e1b, h1b)):
        g1 = cnf.add32(y9, h)
        f1 = ror(cnf.xor32(y4, g1), 12)
        e2 = cnf.add32(cnf.add32(e1, f1), w8)
        h2 = ror(cnf.xor32(h, e2), 8)
        g2 = cnf.add32(g1, h2)
        sides.append((g1, e2, g2))
    x2 = rol(tau ^ rorv(tau, 1), 12)
    for word, want in ((cnf.xor32(e1a, e1b), rol(ETA, 16)), (cnf.xor32(sides[0][0], sides[1][0]), x2),
                       (cnf.xor32(sides[0][1], sides[1][1]), eps), (cnf.xor32(sides[0][2], sides[1][2]), tau)):
        for bit, c in zip(word, const32(want)):
            cnf.equal(bit, c)
    return cnf, y4, h1, y9, w8


def violate(cnf, h1):
    """One clause: at least one condition of the rule fails."""
    lits = []
    for mask, value in RULE:
        x = r2_sat.F
        for i in range(32):
            if mask >> i & 1:
                x = cnf.xor2(x, h1[i])
        lits.append(x if value == 0 else cnf.neg(x))
    cnf.add(*lits)


def plain(tau, eps, beta, y4, h1, y9, w8):
    """The model in 32-bit arithmetic, with G's assignments written out: is it a solution of this outcome?

    E3 on A and B must show eta, tau (c output), eps (a output), and the b and d output differences that a zero
    residual needs for this outcome: ROR(tau, 8) and ROR(beta XOR eps, 7), the d and b output differences of E1."""
    out = []
    e1s = (Y3 + y4) & MASK, (Y3 + D3 + y4) & MASK
    eta = rorv(e1s[0] ^ e1s[1], 16)
    for e1, h in zip(e1s, (h1, h1 ^ eta)):
        g1 = (y9 + h) & MASK
        f1 = rorv(y4 ^ g1, 12)
        e2 = (e1 + f1 + w8) & MASK
        h2 = rorv(h ^ e2, 8)
        g2 = (g1 + h2) & MASK
        f2 = rorv(f1 ^ g2, 7)
        out.append((e2, f2, g2, h2))
    (ea, fa, ga, ha), (eb, fb, gb, hb) = out
    return (eta == ETA and (ga ^ gb) == tau and (ea ^ eb) == eps and (fa ^ fb) == rorv(tau, 8)
            and (ha ^ hb) == rorv(beta ^ eps, 7) and ((e1s[0] & D["qmask"]) == D["qvalue"]))


def kissat(path):
    r = subprocess.run(["kissat", "-q", f"--time={TIME}", str(path)], capture_output=True, text=True)
    sat, model = "?", {}
    for line in r.stdout.splitlines():
        if line.startswith("s "):
            sat = {"SATISFIABLE": "SAT", "UNSATISFIABLE": "UNSAT"}.get(line[2:].strip(), "?")
        elif line.startswith("v "):
            for tok in line[2:].split():
                v = int(tok)
                if v:
                    model[abs(v)] = v > 0
    return sat, model


def val(model, bits):
    return sum(1 << i for i, b in enumerate(bits) if model.get(b, False))


def job(args):
    mode, (tau, eps, beta) = args
    cnf, y4, h1, y9, w8 = build(tau, eps)
    if mode == "violate":
        violate(cnf, h1)
    path = TMP / f"{mode}_{tau:08x}_{eps:08x}.cnf"
    cnf.write(str(path))
    sat, model = kissat(path)
    res = {"mode": mode, "key": (tau, eps, beta), "sat": sat}
    if sat == "SAT" and model:
        h = val(model, h1)
        res["h1"] = h
        res["ok"] = plain(tau, eps, beta, val(model, y4), h, val(model, y9), val(model, w8))
        res["model"] = (val(model, y4), h, val(model, y9), val(model, w8))
    try:
        path.unlink()
    except OSError:
        pass
    return res


def outcomes():
    keys = []
    for line in SOURCE.read_text(encoding="ascii").split("\n"):
        f = line.split()
        if f and f[0] == "OUTX" and int(f[1], 16) == ETA:
            keys.append((int(f[3], 16), int(f[4], 16), int(f[2], 16)))
    return keys


def example():
    """One complete solution of the seven-word system that violates rule A (appended to the result file)."""
    products, models = {}, {}
    for line in SOURCE.read_text(encoding="ascii").splitlines():
        f = line.split()
        if f and f[0] == "OUTX" and int(f[1], 16) == ETA:
            products[(int(f[2], 16), int(f[3], 16), int(f[4], 16))] = int(f[6]) * int(f[8])
    old = [l for l in OUT.read_text(encoding="ascii").splitlines() if l and not l.startswith("EXAMPLE")]
    for line in old:
        f = line.split()
        if f[0] == "VIOLATE" and f[4] == "SAT":
            models[(int(f[1], 16), int(f[2], 16), int(f[3], 16))] = tuple(int(f[i], 16) for i in (6, 8, 10, 12))
    beta, tau, eps = max(models, key=lambda k: (products[k], k))
    y4, h1, y9, w8 = models[(beta, tau, eps)]
    y11, y11b, delta = D["Y11"], D["Y11B"], D["delta"]
    cnf = CNF()
    new = lambda: [cnf.new() for _ in range(32)]  # noqa: E731
    d1, b1, a2, s = new(), new(), new(), new()
    c1, c1b = cnf.add32(const32(y11), d1), cnf.add32(const32(y11b), d1)
    b1b = cnf.xor32(b1, const32(beta))
    a2b = cnf.add32(cnf.add32(s, b1b), const32(delta))
    for x, y in zip(a2, cnf.add32(s, b1)):
        cnf.equal(x, y)
    c2 = cnf.add32(c1, ror(cnf.xor32(d1, a2), 8))
    c2b = cnf.add32(c1b, ror(cnf.xor32(d1, a2b), 8))
    for word, want in ((cnf.xor32(c1, c1b), rol(beta, 12)), (cnf.xor32(a2, a2b), tau), (cnf.xor32(c2, c2b), eps)):
        for bit, c in zip(word, const32(want)):
            cnf.equal(bit, c)
    TMP.mkdir(parents=True, exist_ok=True)
    path = TMP / "example_e1.cnf"
    cnf.write(str(path))
    sat, model = kissat(path)
    path.unlink()
    if sat != "SAT":
        raise SystemExit("the E1 system of the outcome has no model: " + sat)
    vd1, vb1, va2 = val(model, d1), val(model, b1), val(model, a2)
    # the inputs of E1 and E3 in the names of proof.md 6.2, with a1 = 0 and w12 = 0 (E1's first sum is free)
    Y12 = rol(vd1, 16)
    Y6 = rol(vb1, 12) ^ ((y11 + vd1) & MASK)
    Y1 = (0 - Y6) & MASK
    w5 = (va2 - vb1) & MASK
    Y14 = rol(h1, 16) ^ ((Y3 + y4) & MASK)
    ea, eb = data.g_steps(Y1, Y6, y11, Y12, 0, w5), data.g_steps(Y1, Y6, y11b, Y12, 0, (w5 + delta) & MASK)
    fa, fb = data.g_steps(Y3, y4, y9, Y14, 0, w8), data.g_steps(D["Y3B"], y4, y9, Y14, 0, w8)
    residual = (ea["a2"] ^ fa["c2"] ^ eb["a2"] ^ fb["c2"], fa["a2"] ^ ea["c2"] ^ fb["a2"] ^ eb["c2"],
                fa["b2"] ^ ea["d2"] ^ fb["b2"] ^ eb["d2"], ea["b2"] ^ fa["d2"] ^ eb["b2"] ^ fb["d2"])
    good = (not any(residual) and fa["d1"] == h1 and not passes(h1) and (ea["b1"] ^ eb["b1"]) == beta
            and (ea["a2"] ^ eb["a2"]) == tau and (ea["c2"] ^ eb["c2"]) == eps and ((Y3 + y4) & D["qmask"]) == D["qvalue"])
    line = (f"EXAMPLE {beta:08x} {tau:08x} {eps:08x} Y1 {Y1:08x} Y6 {Y6:08x} Y12 {Y12:08x} w12 00000000 w5 {w5:08x} "
            f"Y4 {y4:08x} Y9 {y9:08x} Y14 {Y14:08x} w8 {w8:08x} h1 {h1:08x} residual_zero {int(not any(residual))} "
            f"rule_A {int(passes(h1))} checked {int(good)}")
    with open(OUT, "w", encoding="ascii", newline=chr(10)) as handle:
        handle.write(chr(10).join(old + [line]) + chr(10))
    print(line)
    return 0 if good else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "example":
        return example()
    threads = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    TMP.mkdir(parents=True, exist_ok=True)
    keys = outcomes()
    for tau, eps, beta in keys:                 # the outcome of a beta: eta = eps XOR ROL(beta XOR eps, 1)
        if eps ^ rol(beta ^ eps, 1) != ETA:
            raise SystemExit(f"outcome {tau:08x} {eps:08x} of beta {beta:08x} does not belong to eta")
    jobs = [(mode, k) for mode in ("all", "violate") for k in keys]
    with ThreadPoolExecutor(threads) as pool:
        res = list(pool.map(job, jobs))
    allr = [r for r in res if r["mode"] == "all"]
    vio = [r for r in res if r["mode"] == "violate"]
    sat_all = [r for r in allr if r["sat"] == "SAT"]
    sat_vio = [r for r in vio if r["sat"] == "SAT"]
    lines = [f"# tools/rule_a_sat.py: eta {ETA:08x}, Y3 {Y3:08x}, DY3 {D3:08x}; {len(keys)} outcomes with a nonzero product from "
             f"{SOURCE.name} ({len({k[2] for k in keys})} betas); kissat on the E3 system written from its definition",
             "# rule A on h1 (mask:value, XOR of the masked bits): " + ",".join(f"{m:08x}:{v}" for m, v in RULE),
             f"SUMMARY all: {len(allr)} outcomes, satisfiable {len(sat_all)}, unsatisfiable {sum(r['sat'] == 'UNSAT' for r in allr)}, "
             f"undecided {sum(r['sat'] == '?' for r in allr)}; models that are solutions in plain arithmetic "
             f"{sum(bool(r.get('ok')) for r in sat_all)} of {len(sat_all)}; models that satisfy rule A {sum(passes(r['h1']) for r in sat_all)}",
             f"SUMMARY violate (system AND h1 does not satisfy rule A): unsatisfiable {sum(r['sat'] == 'UNSAT' for r in vio)} of {len(vio)}, "
             f"satisfiable {len(sat_vio)} (models that are solutions in plain arithmetic {sum(bool(r.get('ok')) for r in sat_vio)}, "
             f"that violate rule A {sum(not passes(r['h1']) for r in sat_vio)}), undecided {sum(r['sat'] == '?' for r in vio)}"]
    for r in res:
        tau, eps, beta = r["key"]
        tail = ""
        if "h1" in r:
            y4, h, y9, w8 = r["model"]
            tail = f" Y4 {y4:08x} h1 {h:08x} Y9 {y9:08x} w8 {w8:08x} solution {int(r['ok'])} rule_A {int(passes(h))}"
        lines.append(f"{r['mode'].upper()} {beta:08x} {tau:08x} {eps:08x} {r['sat']}{tail}")
    OUT.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    print(lines[2][:230])
    print(lines[3][:230])
    good = (len(sat_all) == len(allr) and all(r.get("ok") for r in sat_all) and all(r["sat"] != "?" for r in vio)
            and all(r.get("ok") and not passes(r["h1"]) for r in sat_vio))
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
