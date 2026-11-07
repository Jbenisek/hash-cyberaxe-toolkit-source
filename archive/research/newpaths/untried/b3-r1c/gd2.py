"""b3-r1c scout: complete word-level GD peak search (all unknown words are guess candidates).

Same relation system as gd.py.  Incremental closure; iterative deepening on the peak;
memo on the closed known-set.  Usage: python gd2.py <case> <peak> [budget_s]
cases: lift (9 E words held, dof 0), e3 (E3 held, dof 5), e1 (E1 held, dof 4).
"""
import sys, time
from gd import VARS, REL, NV, NR, OCC, CONST, E1IN, E3IN, mask

FULL = (1 << NV) - 1
RELM = [sum(1 << v for v in r) for r in REL]


def close(known, used, new):
    checks = 0
    stack = list(new)
    while stack:
        v = stack.pop()
        for ri in OCC[v]:
            if used >> ri & 1:
                continue
            unk = RELM[ri] & ~known
            if unk == 0:
                used |= 1 << ri
                checks += 1
            elif unk & (unk - 1) == 0:
                known |= unk
                used |= 1 << ri
                stack.append(unk.bit_length() - 1)
    return known, used, checks


def solve(known0, peak, budget):
    # initial closure
    allv = [v for v in range(NV) if known0 >> v & 1]
    k, u, c = close(known0, 0, allv)
    seen = {}
    t0 = time.time()
    nodes = [0]
    sol = [None]

    def rec(known, used, dim, order):
        nodes[0] += 1
        if known == FULL:
            sol[0] = list(order)
            return True
        if seen.get(known, 99) <= dim:
            return False
        seen[known] = dim
        if dim + 1 > peak:
            return False
        if time.time() - t0 > budget:
            raise TimeoutError
        unknown = [v for v in range(NV) if not known >> v & 1]
        # try guesses that give checks / derivations first
        scored = []
        for v in unknown:
            k2, u2, ch = close(known | (1 << v), used, [v])
            scored.append((-(ch), -bin(k2).count("1"), v, k2, u2, ch))
        scored.sort()
        for _, _, v, k2, u2, ch in scored:
            order.append((VARS[v], dim + 1, dim + 1 - ch))
            if rec(k2, u2, dim + 1 - ch, order):
                return True
            order.pop()
        return False

    try:
        found = rec(k, u, -c, [])
    except TimeoutError:
        return "timeout", nodes[0], len(seen)
    return (sol[0] if found else None), nodes[0], len(seen)


if __name__ == "__main__":
    case, peak = sys.argv[1], int(sys.argv[2])
    budget = float(sys.argv[3]) if len(sys.argv) > 3 else 500
    held = {"lift": E1IN + E3IN, "e3": E3IN, "e1": E1IN, "free": []}[case]
    t0 = time.time()
    res, nodes, states = solve(mask(CONST + held), peak, budget)
    print("case=%s peak<=%d: %s  nodes=%d states=%d  %.1fs" % (
        case, peak, "TIMEOUT" if res == "timeout" else ("NONE (exhaustive)" if res is None else "FOUND"),
        nodes, states, time.time() - t0))
    if res not in (None, "timeout"):
        print("   " + " -> ".join("%s[%d/%d]" % o for o in res))
