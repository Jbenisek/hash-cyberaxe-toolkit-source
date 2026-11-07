"""Permissive peeling core (ksplit NOTES 3): repeatedly remove either a word lying in exactly one remaining
equation, or ANY set Q of words of one G call that is touched by exactly |Q| remaining equations (a square
block that a table rule could solve jointly).  The words left must lie in J = A u B for any rule set whose
joint solving acts inside single G calls (plain propagation, gd_sat tables, 2^64 per-call tables).
Usage: python tcore.py <sysfile>"""
import itertools, sys
from regsat import load

N, E, F, names, eqs = load(sys.argv[1])
alive = set(range(N)); alive_e = set(range(E))
call = lambda w: names[w].split(".")[0] if "." in names[w] else None
ch = True
while ch:
    ch = False
    touch = {w: [j for j in alive_e if w in eqs[j][1]] for w in alive}
    for w in sorted(alive):
        if len(touch[w]) <= 1:
            alive.discard(w); alive_e.difference_update(touch[w]); ch = True
            break
    if ch:
        continue
    groups = {}
    for w in alive:
        if call(w):
            groups.setdefault(call(w), []).append(w)
    for cname, ws in sorted(groups.items()):
        for r in range(2, len(ws) + 1):
            for Q in itertools.combinations(ws, r):
                tq = {j for w in Q for j in touch[w]}
                if len(tq) == len(Q):
                    alive.difference_update(Q); alive_e.difference_update(tq); ch = True
                    print("removed square block", cname, [names[w] for w in Q])
                    break
            if ch:
                break
        if ch:
            break
print(sys.argv[1], "permissive core words", len(alive), "eqs", len(alive_e), "delta", len(alive) - len(alive_e))
print("removed:", " ".join(sorted(names[w] for w in set(range(N)) - alive)))
