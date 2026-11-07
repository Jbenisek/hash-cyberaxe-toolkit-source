"""Decode a SAT model of sat_toy.py's encoder and replay it: the guessed words must determine every word by
plain propagation, and checks = guesses - F.   Usage: python decode.py real_out0_k16.kout out0
(1-round toys: python decode.py toy_r1_out0_k15.kout out0 r1)
"""
import sys

from build import system
from cores import incid


def main():
    kout, held = sys.argv[1], tuple(sys.argv[2].split(","))
    rounds = 1 if len(sys.argv) > 3 and sys.argv[3] == "r1" else 2
    eqs, const, _ = system(held=held, rounds=rounds)
    E, occ = incid(eqs, const)
    words = sorted(occ)                          # g variables are 1..len(words) in this order (encode())
    true = set()
    for line in open(kout):
        if line.startswith("v "):
            true.update(int(x) for x in line[2:].split() if int(x) > 0)
    guesses = [w for i, w in enumerate(words) if (i + 1) in true]
    known = set(guesses)
    used = set()
    ch = True
    while ch:
        ch = False
        for i, e in enumerate(E):
            u = [v for v in e if v not in known]
            if len(u) == 1:
                known.add(u[0])
                used.add(i)
                ch = True
    F = len(words) - len(eqs)
    print(f"{kout}: {len(guesses)} guesses {guesses}")
    print(f"  all {len(words)} words determined: {len(known) == len(words)}; F = {F}; checks = "
          f"{len(guesses) - F}; check equations: {[eqs[i][0] for i in range(len(eqs)) if i not in used]}")


if __name__ == "__main__":
    main()
