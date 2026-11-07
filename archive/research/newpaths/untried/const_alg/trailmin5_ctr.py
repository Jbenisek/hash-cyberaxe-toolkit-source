#!/usr/bin/env python3
"""COUNTER-OBJECTIVE VARIANT (const_alg, 2026-10-09) of research/night/main/trailmin5.py. Changes, nothing else:
  1. the cost bound --bound covers A4, A5, A3, A6, A7 only. A1 = weight of x5 = c1 xor c1' below bit 31 is the
     beta's weight k (beta = ROR(x5, 12)); on the counter path the counter solve prescribes the beta, so its 2^-k
     is not paid by trials and the objective is part(beta) x 2^k, whose proxy is cost - A1;
  2. A1 is bounded on its own by --max-k / --min-k;
  3. output names the model "pinctr-lxN" and prints k and the counter cost next to the full cost;
  4. r2_sat, r2_trail are imported read-only from research/; kissat-sat runs with --time=TIMEOUT as before.
Original docstring follows.

Designed constants: a pinned call C3 together with a cheap solution of the (E1, E3) pair. Research scratch.

One SAT instance holds, with real word values:
  - the pinned call C3 = G(X3, X7, X11, X15; w4, w13) for both messages (w4' = ((K + w4) xor 2) - K), with
    equal b and d outputs: its a and c outputs are Y3, Y3' and Y11, Y11';
  - E1 = G(., Y6, Y11, Y12; ., w5) and E3 = G(Y3, Y4, Y9, Y14; 0, w8) for both messages (E1's first sum
    a1 = Y1 + Y6 + w12 is one free word; message B has w5 + (w4 - w4'));
  - a zero residual (the four digest words fed by E1 and E3 agree).
So every model is a genuine pin plus a genuine solution of the seven-word system for that pin. The search is
steered by the cost of the solution's path: the number of bit positions (bit 31 excepted) where a difference
is active at the six additions that are not free in the class search,
    A1 c1: x5   A4 a2: beta|tau   A5 c2: nu|eps   A3 g1: eta|x2   A6 e2: psi|eps   A7 g2: mu|tau.
The weight of x1 = e1 xor e1' (the class has 2^(32 - weight) members) is bounded separately.

  trailmin5.py --bound N [--max-x1 24] [--min-x1 0] [--pin X3,X7,X11,X15,W4,W13] [--exclude FILE]
               [--seed S] [--timeout T] [--solver kissat]
Output: "RES ... status=SATISFIABLE cost=.. x1w=.. PIN=X3,X7,X11,X15,W4,W13 D3=.. D11=.. delta=.. Y3=.. Y11=..
         eta=.. beta=.. tau=.. eps=.. parts=.. sol=d1,b1,a2,Y4,h1,Y9,w8"
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

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research'))   # r2_sat, r2_trail (read-only)
from r2_sat import CNF, F, T, const32, ror, value  # noqa: E402
from r2_trail import K, at_most, g_rec, solve  # noqa: E402

M = 0xFFFFFFFF


def new32(cnf):
    return [cnf.new() for _ in range(32)]


def build(a):
    cnf = CNF()
    add, xor = cnf.add32, cnf.xor32
    pin = [int(v, 16) for v in a.pin.split(",")] if a.pin else None
    inputs = [const32(v) for v in pin[:4]] if pin else [new32(cnf) for _ in range(4)]
    w4 = const32(pin[4]) if pin else new32(cnf)
    w13 = const32(pin[5]) if pin else new32(cnf)
    if a.w13_top0 and not pin:
        # other length pairs force the top bytes of w13 (or all of it) to zero
        w13 = list(w13[:32 - a.w13_top0]) + [F] * a.w13_top0
    w4b = new32(cnf)
    for p, q in zip(add(const32(K), w4b), xor(add(const32(K), w4), const32(a.lenxor))):
        cnf.equal(p, q)
    va, vb = list(inputs), list(inputs)
    g_rec(cnf, va, 0, 1, 2, 3, w4, w13)
    g_rec(cnf, vb, 0, 1, 2, 3, w4b, w13)
    for index in (1, 3):
        for p, q in zip(va[index], vb[index]):
            cnf.equal(p, q)
    y3, y3b, y11, y11b = va[0], vb[0], va[2], vb[2]
    dw = new32(cnf)                      # w4 - w4'
    for p, q in zip(add(dw, w4b), w4):
        cnf.equal(p, q)
    # E1: a1 stands for Y1 + Y6 + w12
    a1, y12, y6, w5 = new32(cnf), new32(cnf), new32(cnf), new32(cnf)
    d1 = ror(xor(y12, a1), 16)
    e1out = []
    for c_in, m2 in ((y11, w5), (y11b, add(w5, dw))):
        c1 = add(c_in, d1)
        b1 = ror(xor(y6, c1), 12)
        a2 = add(add(a1, b1), m2)
        d2 = ror(xor(d1, a2), 8)
        c2 = add(c1, d2)
        b2 = ror(xor(b1, c2), 7)
        e1out.append(dict(c1=c1, b1=b1, a2=a2, d2=d2, c2=c2, b2=b2))
    # E3: first word is zero
    y4, y9, y14, w8 = new32(cnf), new32(cnf), new32(cnf), new32(cnf)
    e3out = []
    for a_in in (y3, y3b):
        e1 = add(a_in, y4)
        h1 = ror(xor(y14, e1), 16)
        g1 = add(y9, h1)
        f1 = ror(xor(y4, g1), 12)
        e2 = add(add(e1, f1), w8)
        h2 = ror(xor(h1, e2), 8)
        g2 = add(g1, h2)
        f2 = ror(xor(f1, g2), 7)
        e3out.append(dict(e1=e1, h1=h1, g1=g1, f1=f1, e2=e2, h2=h2, g2=g2, f2=f2))
    dE1 = {k: xor(e1out[0][k], e1out[1][k]) for k in e1out[0]}
    dE3 = {k: xor(e3out[0][k], e3out[1][k]) for k in e3out[0]}
    for p, q in ((dE1["a2"], dE3["g2"]), (dE3["e2"], dE1["c2"]), (dE3["f2"], dE1["d2"]), (dE1["b2"], dE3["h2"])):
        for u, v in zip(p, q):
            cnf.equal(u, v)
    x5, beta, tau, nu, eps = dE1["c1"], dE1["b1"], dE1["a2"], dE1["d2"], dE1["c2"]
    x1, eta, x2, psi, mu = dE3["e1"], dE3["h1"], dE3["g1"], dE3["f1"], dE3["h2"]
    if not a.no_redundant:
        # Implied by the zero residual (Lemma E and its twin); stated explicitly to help the solver.
        for i in range(32):
            j = (i + 1) % 32
            cnf.equal(psi[i], cnf.xor2(tau[i], tau[j]))
            cnf.equal(cnf.xor2(beta[i], eps[i]), cnf.xor2(eta[j], eps[j]))

    def orw(*ws):
        out = []
        for i in range(32):
            acc = ws[0][i]
            for w in ws[1:]:
                acc = cnf.or2(acc, w[i])
            out.append(acc)
        return out

    parts = [("A1", x5), ("A4", orw(beta, tau)), ("A5", orw(nu, eps)), ("A3", orw(eta, x2)), ("A6", orw(psi, eps)),
             ("A7", orw(mu, tau))]
    # counter objective: A1 (the beta's weight k) is not in the bound; it is bounded on its own
    at_most(cnf, [bit for n, w in parts if n != "A1" for bit in w[:31]], a.bound)
    if a.max_k >= 0:
        at_most(cnf, list(x5[:31]), a.max_k)
    if a.min_k > 0:
        at_most(cnf, [cnf.neg(b) for b in x5[:31]], 31 - a.min_k)
    if a.max_x1 >= 0:
        at_most(cnf, list(x1[:31]), a.max_x1)
    if a.min_x1 > 0:
        at_most(cnf, [cnf.neg(b) for b in x1[:31]], 31 - a.min_x1)
    d3 = new32(cnf)
    for p, q in zip(add(d3, y3), y3b):
        cnf.equal(p, q)
    d11 = new32(cnf)
    for p, q in zip(add(d11, y11), y11b):
        cnf.equal(p, q)
    for wd, text in ((d3, a.d3), (d11, a.d11), (dw, a.delta), (y3, a.y3_not), (y11, a.y11_not)):
        if not text:
            continue
        if wd is y3 or wd is y11:
            # exclude listed values (comma separated) of Y3 or Y11: enumerate other pins of the same family
            for v in text.split(","):
                val = int(v, 16)
                clause = [(-bit if (val >> i) & 1 else bit) for i, bit in enumerate(wd) if bit is not T and bit is not F]
                if clause:
                    cnf.add(*clause)
            continue
        for bit, c in zip(wd, const32(int(text, 16))):
            cnf.equal(bit, c)
    if a.near:
        # stay within a Hamming distance of given differences: --near D3HEX,D11HEX,DIST
        n3, n11, nd = a.near.split(",")
        diff = []
        for wd, val in ((d3, int(n3, 16)), (d11, int(n11, 16))):
            for i, bit in enumerate(wd):
                diff.append(bit if not (val >> i) & 1 else cnf.neg(bit))
        at_most(cnf, diff, int(nd))
    if a.exclude and Path(a.exclude).exists():
        for line in Path(a.exclude).read_text().split("\n"):
            t = line.split()
            if len(t) >= 2:
                clause = []
                for wd, v in ((d3, int(t[0], 16)), (d11, int(t[1], 16))):
                    for i, bit in enumerate(wd):
                        if bit is not T and bit is not F:
                            clause.append(-bit if (v >> i) & 1 else bit)
                if clause:
                    cnf.add(*clause)
    if a.exclude_pairs and Path(a.exclude_pairs).exists():
        for line in Path(a.exclude_pairs).read_text().split("\n"):
            t = line.split()
            if len(t) >= 2:
                clause = []
                for wd, v in ((eta, int(t[0], 16)), (beta, int(t[1], 16))):
                    for i, bit in enumerate(wd):
                        if bit is T or bit is F:
                            if (bit is T) != bool((v >> i) & 1):
                                clause = None
                                break
                            continue
                        clause.append(-bit if (v >> i) & 1 else bit)
                    if clause is None:
                        break
                if clause:
                    cnf.add(*clause)
    words = dict(X3=inputs[0], X7=inputs[1], X11=inputs[2], X15=inputs[3], W4=w4, W13=w13, dw=dw, D3=d3, D11=d11,
                 Y3=y3, Y11=y11, eta=eta, beta=beta, tau=tau, eps=eps, x1=x1,
                 d1=d1, b1=e1out[0]["b1"], a2=e1out[0]["a2"], Y4=y4, h1=e3out[0]["h1"], Y9=y9, w8=w8)
    return cnf, words, parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bound", type=int, required=True)
    ap.add_argument("--pin", default="")
    ap.add_argument("--max-x1", type=int, default=24)
    ap.add_argument("--min-x1", type=int, default=0)
    ap.add_argument("--max-k", type=int, default=24, help="bound on A1 = k, the beta's weight (counter variant)")
    ap.add_argument("--min-k", type=int, default=0)
    ap.add_argument("--exclude", default="")
    ap.add_argument("--no-redundant", action="store_true")
    ap.add_argument("--near", default="", help="D3HEX,D11HEX,DIST: differences within that Hamming distance of the given ones")
    ap.add_argument("--d3", default="", help="prescribe DY3 = Y3' - Y3")
    ap.add_argument("--d11", default="", help="prescribe D11 = Y11' - Y11")
    ap.add_argument("--delta", default="", help="prescribe W4 - W4' (00000002 or fffffffe)")
    ap.add_argument("--y3-not", default="", help="comma list of Y3 values to exclude")
    ap.add_argument("--y11-not", default="", help="comma list of Y11 values to exclude")
    ap.add_argument("--exclude-pairs", default="", help="file of 'eta beta' lines (hex) that must not be returned again")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--solver", default="kissat")
    ap.add_argument("--lenxor", type=int, default=2,
                    help="XOR of the two block lengths: 2 for 60/62 (filed), 1 for 60/61 or 62/63, 3 for 60/63 or 61/62")
    ap.add_argument("--w13-top0", type=int, default=0, help="number of top bits of W13 forced to zero (8 for lengths 55/63, 32 for 47/63)")
    a = ap.parse_args()
    cnf, words, parts = build(a)
    if a.solver == "kissat-sat":
        # kissat tuned for satisfiable instances; same file handling as r2_trail.solve
        import os, subprocess, tempfile, time
        directory = tempfile.mkdtemp(prefix="r2trail-")
        path = os.path.join(directory, "problem.cnf")
        cnf.write(path)
        started = time.monotonic()
        done = subprocess.run(["kissat", "-q", "--sat", f"--seed={a.seed}", f"--time={a.timeout}", path], capture_output=True, text=True)
        elapsed = time.monotonic() - started
        os.remove(path); os.rmdir(directory)
        status, model = "UNKNOWN", {}
        for line in done.stdout.splitlines():
            if line.startswith("s "):
                status = line[2:].strip()
            elif line.startswith("v "):
                for token in line[2:].split():
                    lit = int(token)
                    if lit:
                        model[abs(lit)] = lit > 0
    else:
        status, model, elapsed = solve(cnf, a.solver, a.seed, a.timeout)
    head = (f"RES model=pinctr-lx{a.lenxor} ctrbound={a.bound} maxk={a.max_k} delta={a.delta or 'free'} top0={a.w13_top0} "
            f"fixed={'yes' if a.pin else 'no'} seed={a.seed} t={elapsed:.0f}s status={status}")
    if status != "SATISFIABLE":
        print(head, flush=True)
        return 0
    v = {n: value(model, w) for n, w in words.items()}
    wt = lambda w: bin(value(model, w) & 0x7FFFFFFF).count("1")
    cost = sum(wt(w) for _, w in parts)
    kk = wt(parts[0][1])
    print(head + f" cost={cost} k={kk} ctrcost={cost - kk} x1w={bin(v['x1'] & 0x7FFFFFFF).count('1')} "
          f"PIN={v['X3']:08x},{v['X7']:08x},{v['X11']:08x},{v['X15']:08x},{v['W4']:08x},{v['W13']:08x} "
          f"D3={v['D3']:08x} D11={v['D11']:08x} delta={v['dw']:08x} Y3={v['Y3']:08x} Y11={v['Y11']:08x} "
          f"eta={v['eta']:08x} beta={v['beta']:08x} tau={v['tau']:08x} eps={v['eps']:08x} parts="
          + ",".join(f"{n}:{wt(w)}" for n, w in parts)
          + f" sol={v['d1']:08x},{v['b1']:08x},{v['a2']:08x},{v['Y4']:08x},{v['h1']:08x},{v['Y9']:08x},{v['w8']:08x}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
