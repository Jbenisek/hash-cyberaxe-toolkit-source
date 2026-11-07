"""Variant systems that give a one-word-at-a-time solver more words to work with: every 3-term addition
o = p + q + r is split through an intermediate-sum word s (s = p + q, o = s + r); freedom is unchanged (+1 word,
+1 equation each).  Pairing choice per G half:  P0: (a+b)+x and (a1+b1)+y;  P1: (a+x)+b and (a1+y)+b1;
P2: (b+x)+a and (b1+y)+a1.  An intermediate whose two inputs are both family constants is a constant itself.
Writes sys_split_P<i>.txt (bf.c / flats.c format).  Also numerically checks the split equations on random messages.
"""
import os
import random

from sys_build import symbolic, compress, rotr, IV, M32

HERE = os.path.dirname(os.path.abspath(__file__))


def build(pairing):
    eqs, const, names, Y = symbolic()
    out = []
    for nm, op, o, ins in eqs:
        if op != "add3":
            out.append((nm, op, o, ins))
            continue
        p, q, r = ins                      # a1: (a, b, x)   a2: (a1, b1, y)
        pair = {0: (p, q, r), 1: (p, r, q), 2: (q, r, p)}[pairing]
        s = f"{nm}.s"
        if pair[0] in const and pair[1] in const:
            const = const | {s}
        out.append((nm + "s", "add2", s, (pair[0], pair[1])))
        out.append((nm, "add2", o, (s, pair[2])))
    return out, const, names


def numeric(eqs, names, pairing, trials=100):
    rng = random.Random(5)
    bad = 0
    for _ in range(trials):
        m = [rng.getrandbits(32) for _ in range(16)]
        tr = []
        compress(m, 2, trace=tr)
        val = {f"init{i}": w for i, w in enumerate(IV[:] + IV[:4] + [0, 0, 64, 11])}
        val.update({f"m{i}": m[i] for i in range(16)})
        for r, j, d in tr:
            if (r, j) in names:
                for t in ("a1", "d1", "c1", "b1", "a2", "d2", "c2", "b2"):
                    val[f"{names[(r, j)]}.{t}"] = d[t]
        for nm, op, o, ins in eqs:                  # evaluate in order: split sums are defined before use
            if op == "add2" and o not in val:
                val[o] = (val[ins[0]] + val[ins[1]]) & M32
        for nm, op, o, ins in eqs:
            iv = [val[i] for i in ins]
            if op == "add2":
                ok = val[o] == (iv[0] + iv[1]) & M32
            elif op == "add3":
                ok = val[o] == (iv[0] + iv[1] + iv[2]) & M32
            else:
                ok = val[o] == rotr(iv[0] ^ iv[1], int(op[2:]))
            bad += not ok
    return bad


def main():
    for P in (0, 1, 2):
        eqs, const, names = build(P)
        ncq = [frozenset(v for v in (o,) + ins if v not in const) for _, _, o, ins in eqs]
        ncq = [s for s in ncq if s]
        vars_ = sorted({v for s in ncq for v in s})
        bad = numeric(eqs, names, P)
        ix = {v: i for i, v in enumerate(vars_)}
        with open(os.path.join(HERE, f"sys_split_P{P}.txt"), "w", newline="\n") as fh:
            fh.write(f"{len(vars_)} {len(ncq)} 0\n" + " ".join(vars_) + "\n")
            for s in ncq:
                fh.write(" ".join(str(ix[v]) for v in sorted(s)) + "\n")
        one = sum(1 for s in ncq if len(s) == 1)
        print(f"P{P}: {len(vars_)} unknown words, {len(ncq)} equations, freedom {len(vars_) - len(ncq)}, "
              f"single-word equations {one}, numeric failures {bad}")


if __name__ == "__main__":
    main()
