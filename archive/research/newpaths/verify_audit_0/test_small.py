"""Small random systems: brute-force kmin (all guess subsets; closure by the literal one-at-a-time definition with a
random scan order) vs flats.c (look, look1, plain) and audit/bf3 (look, none).
  python test_small.py gen   -> writes unit/s<i>.txt and unit/expected.txt and unit/run.sh
  (run unit/run.sh in WSL)
  python test_small.py cmp   -> compares
"""
import itertools
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
U = os.path.join(HERE, "unit")
N = 80


def rand_system(rng):
    nv = rng.randint(6, 14)
    f = rng.randint(0, 4)
    ne = max(1, nv - f + rng.randint(-1, 1))
    eqs = []
    for _ in range(ne):
        k = rng.choice((2, 3, 3, 3, 4))
        eqs.append(frozenset(rng.sample(range(nv), min(k, nv))))
    used = set().union(*eqs)
    for v in range(nv):          # every word in some equation
        if v not in used:
            eqs.append(frozenset({v, rng.randrange(nv)} if nv > 1 else {v}))
    eqs = [e for e in eqs if len(e) >= 2]
    vars_ = sorted(set().union(*eqs))
    ix = {v: i for i, v in enumerate(vars_)}
    return len(vars_), [frozenset(ix[v] for v in e) for e in eqs]


def plain(eqs, K):
    K = set(K)
    ch = True
    while ch:
        ch = False
        for e in eqs:
            u = e - K
            if len(u) == 1:
                K |= u
                ch = True
    return K


def ncov(eqs, K):
    return sum(1 for e in eqs if e <= K)


def look(eqs, nv, K, rng, on=True):
    K = plain(eqs, K)
    if not on:
        return K
    while True:
        order = list(range(nv))
        rng.shuffle(order)
        for z in order:
            if z in K:
                continue
            K3 = plain(eqs, K | {z})
            if ncov(eqs, K3) - ncov(eqs, K) >= len(K3) - len(K):
                K = K3
                break
        else:
            return K


def kmin(eqs, nv, rng, on):
    for k in range(nv + 1):
        for G in itertools.combinations(range(nv), k):
            if len(look(eqs, nv, set(G), rng, on)) == nv:
                return k
    return None


def gen():
    os.makedirs(U, exist_ok=True)
    rng = random.Random(77)
    exp = []
    sh = ["#!/bin/bash", 'cd "$(dirname "$0")"', "rm -f res.txt"]
    for i in range(N):
        nv, eqs = rand_system(rng)
        kl = kmin(eqs, nv, rng, True)
        kp = kmin(eqs, nv, rng, False)
        exp.append(f"{i} {kl} {kp}")
        with open(os.path.join(U, f"s{i}.txt"), "w", newline="\n") as fh:
            fh.write(f"{nv} {len(eqs)} 0\n" + " ".join(f"v{j}" for j in range(nv)) + "\n")
            for e in eqs:
                fh.write(" ".join(map(str, sorted(e))) + "\n")
        for m in ("look", "look1", "plain"):
            sh.append(f'echo "S {i} flats {m} $(../flats s{i}.txt {nv} {m} | grep RESULT)" >> res.txt')
        for m in ("look", "none"):
            sh.append(f'../../audit/bf3 s{i}.txt {nv} 0 1 {m} > bf3_{i}_{m}.out')
    open(os.path.join(U, "expected.txt"), "w").write("\n".join(exp) + "\n")
    open(os.path.join(U, "run.sh"), "w", newline="\n").write("\n".join(sh) + "\n")
    print("generated", N)


def cmp():
    exp = {}
    for l in open(os.path.join(U, "expected.txt")):
        i, kl, kp = l.split()
        exp[int(i)] = (int(kl), int(kp))
    bad = 0
    lines = []
    for l in open(os.path.join(U, "res.txt")):
        p = l.split()
        i, tool, m = int(p[1]), p[2], p[3]
        want = exp[i][0] if m in ("look", "look1") else exp[i][1]
        if tool == "flats":
            got = int(l.split("kmin=")[1].split()[0]) if "kmin=" in l else None
        else:
            got = int(l.split("k=")[1].split()[0]) if "k=" in l else None
        ok = got == want
        bad += not ok
        if not ok:
            lines.append(f"MISMATCH sys {i} {tool} {m}: got {got} want {want}")
    for i in exp:
        for m in ("look", "none"):
            ks = [int(l.split("k=")[1].split()[0]) for l in open(os.path.join(U, f"bf3_{i}_{m}.out")) if l.startswith("FOUND")]
            got = min(ks) if ks else None
            want = exp[i][0] if m == "look" else exp[i][1]
            if got != want:
                bad += 1
                lines.append(f"MISMATCH sys {i} bf3 {m}: got {got} want {want}")
    hist = {}
    for kl, kp in exp.values():
        hist[(kl, kp)] = hist.get((kl, kp), 0) + 1
    lines.append(f"(kmin look, kmin plain) histogram over {len(exp)} systems: {dict(sorted(hist.items()))}")
    lines.append(f"systems where look < plain: {sum(1 for a, b in exp.values() if a < b)}")
    lines.append(f"mismatches: {bad} of {sum(1 for _ in open(os.path.join(U, 'res.txt')))} runs")
    print("\n".join(lines))
    open(os.path.join(HERE, "test_small.log"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    gen() if sys.argv[1] == "gen" else cmp()
