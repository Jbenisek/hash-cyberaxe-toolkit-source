"""Exact shape facts (32-bit, no sampling).  Owner: shape_odd agent.
 1. call-message graph: each message word links its round-0 call and its round-1 call -> cycle decomposition.
 2. lattice symmetries: the 4x4 state is a torus Z4 x Z4 with rows = roles (a,b,c,d), columns and diagonals =
    G lines.  Find every map (r,c) -> (r, e*c + s*r + t) that sends columns to columns and diagonals to
    diagonals, its induced message-word map, whether it commutes with the message permutation, and whether
    it fixes the initial state.
 3. Moebius / slide: the unique message M* whose round 0 returns the initial state (one round is a bijection,
    inverse formulas of ../../sol_answer_W_newpaths.md 3.3); then 2-round(M*) == 1-round(P M*).
 4. Circle: per-word rotation-invariant sets and the birthday on rotation classes.
"""
import math
import sys

sys.dont_write_bytecode = True
import toy  # noqa: E402

PERM, COLS, DIAG = toy.PERM, toy.COLS, toy.DIAG
MASK = 0xFFFFFFFF


def call_message_graph():
    calls = {}
    for j in range(4):
        for k, i in enumerate((2 * j, 2 * j + 1)):
            calls.setdefault(i, []).append(f"K{j}")
        for k, i in enumerate((8 + 2 * j, 9 + 2 * j)):
            calls.setdefault(i, []).append(f"D{j}")
    s1 = [PERM[i] for i in range(16)]
    for j in range(4):
        for i in (s1[2 * j], s1[2 * j + 1]):
            calls[i].append(f"C{j}")
        for i in (s1[8 + 2 * j], s1[9 + 2 * j]):
            calls[i].append(f"E{j}")
    adj = {}
    for i, (u, v) in calls.items():
        adj.setdefault(u, []).append((v, i))
        adj.setdefault(v, []).append((u, i))
    seen_e, cycles = set(), []
    for start in sorted(adj):
        for (v, i) in adj[start]:
            if i in seen_e:
                continue
            cyc, cur, e = [start], v, i
            seen_e.add(e)
            while cur != start:
                cyc.append(f"-m{e}-{cur}")
                nxt = [(w, k) for (w, k) in adj[cur] if k not in seen_e]
                if not nxt:
                    break
                w, k = nxt[0]
                seen_e.add(k)
                cur, e = w, k
            cyc.append(f"-m{e}-{start}")
            cycles.append("".join(cyc))
    print("1. call-message graph (COMPUTED): every call has degree 2 -> disjoint cycles")
    for c in cycles:
        print("   ", c, f"(length {c.count('-m')})")


def lattice_symmetries():
    print("2. torus-lattice maps (r,c) -> (r, e*c + s*r + t) sending columns->columns and diagonals->diagonals")
    pos = lambda r, c: 4 * r + (c % 4)  # noqa: E731
    colsets = [frozenset(x) for x in COLS]
    diagsets = [frozenset(x) for x in DIAG]
    init = toy.init_state(32)
    for e in (1, 3):
        for s in range(4):
            for t in range(4):
                f = {pos(r, c): pos(r, e * c + s * r + t) for r in range(4) for c in range(4)}
                mc = {i: colsets.index(frozenset(f[p] for p in col)) for i, col in enumerate(colsets)
                      if frozenset(f[p] for p in col) in colsets}
                md = {i: diagsets.index(frozenset(f[p] for p in dg)) for i, dg in enumerate(diagsets)
                      if frozenset(f[p] for p in dg) in diagsets}
                if len(mc) < 4 or len(md) < 4:
                    continue
                # G role order must be kept: f maps (a,b,c,d) of a call to (a,b,c,d) of its image (rows kept)
                msg = {}
                for j in range(4):
                    msg[2 * j], msg[2 * j + 1] = 2 * mc[j], 2 * mc[j] + 1
                    msg[8 + 2 * j], msg[9 + 2 * j] = 8 + 2 * md[j], 9 + 2 * md[j]
                commute = all(msg[PERM[i]] == PERM[msg[i]] for i in range(16))
                fixes_init = all(init[f[p]] == init[p] for p in range(16))
                bad = [p for p in range(16) if init[f[p]] != init[p]]
                print(f"   e={e} s={s} t={t}: columns {mc} diagonals {md}; message map commutes with PERM: {commute};"
                      f" initial state fixed: {fixes_init} (moves {len(bad)} of 16 words)")


def rol(x, r):
    return ((x << r) | (x >> (32 - r))) & MASK


def inverse_round0(X):
    """Sol 3.3: the unique message m with round0(init, m) = X (32-bit)."""
    init = toy.init_state(32)
    S = [None] * 16
    saved = {}
    for j, (ia, ib, ic, id_) in enumerate(DIAG):
        A, B, C, D = X[ia], X[ib], X[ic], X[id_]
        s = rol(B, 7) ^ C
        r = (C - D) & MASK
        q = rol(D, 8) ^ A
        S[ib] = rol(s, 12) ^ r
        S[ic] = (r - q) & MASK
        saved[j] = (A, s, q)
    m = [None] * 16
    for j, (ia, ib, ic, id_) in enumerate(COLS):
        a, b, c, d = init[ia], init[ib], init[ic], init[id_]
        B, C = S[ib], S[ic]
        s = rol(B, 7) ^ C
        r = rol(s, 12) ^ b
        q = (r - c) & MASK
        D = (C - r) & MASK
        p = rol(q, 16) ^ d
        A = rol(D, 8) ^ q
        m[2 * j] = (p - a - b) & MASK
        m[2 * j + 1] = (A - p - s) & MASK
        S[ia], S[id_] = A, D
    for j, (ia, ib, ic, id_) in enumerate(DIAG):
        A, s, q = saved[j]
        p = rol(q, 16) ^ S[id_]
        m[8 + 2 * j] = (p - S[ia] - S[ib]) & MASK
        m[9 + 2 * j] = (A - p - s) & MASK
    return m


def moebius_fixed_point():
    init = toy.init_state(32)
    import random
    rng = random.Random(9)
    for _ in range(200):     # check the inverse on random targets
        X = [rng.getrandbits(32) for _ in range(16)]
        assert toy.round_(init, inverse_round0(X), 32) == X
    Ms = inverse_round0(init)
    assert toy.round_(init, Ms, 32) == init
    two = toy.compress(Ms, 32)
    v1 = toy.round_(init, [Ms[PERM[i]] for i in range(16)], 32)
    one_of_PM = [v1[i] ^ v1[i + 8] for i in range(8)]
    assert two == one_of_PM
    print("3. Moebius/slide (COMPUTED): inverse of round 0 checked on 200 random targets; the unique message with")
    print("   round0(init, M*) = init is M* =", " ".join(f"{x:08x}" for x in Ms))
    print("   2-round digest of M* == 1-round digest of P(M*):", " ".join(f"{x:08x}" for x in two))


def circle():
    print("4. circle (DERIVED): words fixed by ROT_r number 2^gcd(r,32); a rotational pair (M, ROT_r M) under an")
    print("   EXACT rotational symmetry collides only if all 8 output words are ROT_r-invariant:")
    for r in (1, 2, 4, 8, 16):
        g = math.gcd(r, 32)
        print(f"   r={r:2d}: invariant words 2^{g}, condition {8 * (32 - g)} bits -> pair success 2^-{8 * (32 - g)}")
    print("   Birthday on rotation classes (canonical form over the 32 rotations) would save at most sqrt(32) = 2^2.5,")
    print("   i.e. 2^125.5, and only if F(ROT M) = ROT F(M) held with probability >= 2^-2.5.")


if __name__ == "__main__":
    call_message_graph()
    lattice_symmetries()
    moebius_fixed_point()
    circle()
