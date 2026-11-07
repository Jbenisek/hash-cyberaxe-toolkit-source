"""Literal "geometric" elimination orders of the words (the owner's shapes), written as order files for
'bd order'.  shape_any agent.
Words: m0..m15 and <call>.<role>.  Layer: K=0, D=1, C=2, E=3; index j = column/diagonal number; roles in G order.
Shapes:
  forward   sweep in computation order (K, D, C, E)          backward  the reverse
  onion     sphere peeled from both ends inward (alternate forward / backward)
  cylinder  column by column (j = 0..3), all layers of a column together
  torus     diagonal sweep on the 4x4 torus: key (j + layer) mod 4
  ring8     round-0 calls around the 8-ring K0 D3 K1 D0 K2 D1 K3 D2 (a polygon), then the C/E layer by column
  hexagon   six sectors: the ring8 cut into 6 arcs + C, E as two more sectors, swept in a hexagon-like rotation
  msgcyc    following the message permutation's two 8-cycles (0 2 3 10 12 9 11 5) and (1 6 4 7 13 14 15 8)
  star      hub = all message words first, then the calls (a star with the messages at the centre)
Usage: python geo.py <sys> <outdir>
"""
import os
import random
import sys

ROLES = ["a1", "d1", "c1", "b1", "a2", "d2", "c2", "b2"]
LAYER = {"K": 0, "D": 1, "C": 2, "E": 3}
MSG_R0 = {0: "K0", 1: "K0", 2: "K1", 3: "K1", 4: "K2", 5: "K2", 6: "K3", 7: "K3",
          8: "D0", 9: "D0", 10: "D1", 11: "D1", 12: "D2", 13: "D2", 14: "D3", 15: "D3"}
RING8 = ["K0", "D3", "K1", "D0", "K2", "D1", "K3", "D2"]
CYC = [0, 2, 3, 10, 12, 9, 11, 5, 1, 6, 4, 7, 13, 14, 15, 8]


def info(w):
    if w.startswith("m"):
        call = MSG_R0[int(w[1:])]
        return LAYER[call[0]], int(call[1]), -1, call
    call, role = w.split(".")
    return LAYER[call[0]], int(call[1]), ROLES.index(role), call


def main():
    fn, outdir = sys.argv[1], sys.argv[2]
    lines = open(fn).read().split("\n")
    N = int(lines[0].split()[0])
    words = lines[1:1 + N]
    os.makedirs(outdir, exist_ok=True)
    fwd = sorted(words, key=lambda w: (info(w)[0], info(w)[1], info(w)[2]))
    orders = {"forward": fwd, "backward": fwd[::-1]}
    on = []
    for a, b in zip(fwd, fwd[::-1]):
        for w in (a, b):
            if w not in on:
                on.append(w)
    orders["onion"] = on
    orders["cylinder"] = sorted(words, key=lambda w: (info(w)[1], info(w)[0], info(w)[2]))
    orders["torus"] = sorted(words, key=lambda w: ((info(w)[1] + info(w)[0]) % 4, info(w)[0], info(w)[2]))

    def ringkey(w):
        l, j, r, call = info(w)
        if call in RING8:
            return (RING8.index(call), r)
        return (8 + l * 4 + j, r)
    orders["ring8"] = sorted(words, key=ringkey)

    def hexkey(w):
        l, j, r, call = info(w)
        if call in RING8:
            sector = (RING8.index(call) * 6) // 8
        else:
            sector = 6 if l == 2 else 7
        return (sector, l, j, r)
    orders["hexagon"] = sorted(words, key=hexkey)

    def msgkey(w):
        if w.startswith("m"):
            return (CYC.index(int(w[1:])), -1, -1)
        l, j, r, call = info(w)
        # attach a call word to the earliest cycle position of the messages its call uses
        return (min(CYC.index(i) for i, c in MSG_R0.items() if c == call) if call in MSG_R0.values() else 16, l, r)
    orders["msgcyc"] = sorted(words, key=msgkey)
    orders["star"] = sorted(words, key=lambda w: (0 if w.startswith("m") else 1, info(w)[0], info(w)[1], info(w)[2]))
    rng = random.Random(9)
    for i in range(3):
        o = list(words)
        rng.shuffle(o)
        orders[f"random{i}"] = o
    for k, o in orders.items():
        with open(os.path.join(outdir, k + ".ord"), "w") as fh:
            fh.write("\n".join(o) + "\n")
    print(outdir, " ".join(orders))


if __name__ == "__main__":
    main()
