"""D189: exact real-Pallas r=1 odd-part learning run.

Builds the line construction from the pinned Orchard constants, constructs
F(W) through full rounds 2,3, partial round 4, and full rounds 60..63, then
Taylor-shifts at deterministic random centres.  For each centre the odd part
g(s^2) is checked for squarefreeness, total field roots, and nonzero-square
roots.  A small number of witnesses are mapped back to (nk,rho) and checked
with poseidon_ref.hash_reduced.
"""
from __future__ import annotations
import json, math, random, sys, time
from pathlib import Path
import flint

HERE = Path(__file__).resolve().parent
REF_DIR = HERE / "orchard" / "impl"
sys.path.insert(0, str(REF_DIR))
from poseidon_ref import hash_reduced  # type: ignore

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
CAPACITY = 1 << 65
R = flint.fmpz_mod_poly_ctx(P)
X = R.gen()
const_path = REF_DIR / ".." / ".." / "pareto_clone" / "pareto" / "orchard-pallas-constants.json"
if not const_path.exists():
    const_path = HERE.parent / ".." / "3rd_openai_workspace" / "kit" / "orchard-pallas-constants.json"
data = json.loads(const_path.read_text())
RC = [[int(x, 16) for x in row] for row in data["round_constants"]]
M = [[int(x, 16) for x in row] for row in data["mds"]]
INV5 = pow(5, -1, P - 1)


def solve2(a, b, c, d, e, f):
    det = (a * d - b * c) % P
    inv = pow(det, P - 2, P)
    return ((e * d - b * f) * inv % P, (a * f - e * c) * inv % P)


def line_setup(j=0):
    cap = pow((CAPACITY + RC[0][2]) % P, 5, P)
    base = [(M[i][2] * cap + RC[1][i]) % P for i in range(3)]
    i, k = [q for q in range(3) if q != j]
    U, V = solve2(M[i][0], M[i][1], M[k][0], M[k][1], -base[i] % P, -base[k] % P)
    Q = [(base[t] + M[t][0] * U + M[t][1] * V) % P for t in range(3)]
    a, b = M[j][1] % P, (-M[j][0]) % P
    D = [(M[t][0] * a + M[t][1] * b) % P for t in range(3)]
    assert Q[i] == 0 and Q[k] == 0 and D[j] == 0
    return a, b, U, V, Q, D


def inputs_for_tau(tau, line):
    a, b, U0, V0, _Q, _D = line
    U = (U0 + a * tau) % P
    V = (V0 + b * tau) % P
    return (pow(U, INV5, P) - RC[0][0]) % P, (pow(V, INV5, P) - RC[0][1]) % P


def mds_poly(vals):
    return [sum(M[i][j] * vals[j] for j in range(3)) for i in range(3)]


def build_F(line):
    _a, _b, _u, _v, Q, D = line
    # After round 1, the state is affine in W=tau^5.
    sb = [R([pow(Q[t], 5, P)]) if D[t] == 0 else R([0, pow(D[t], 5, P)]) for t in range(3)]
    state = []
    for row in M:
        state.append(sum((int(row[t]) * sb[t] for t in range(3)), R([0])))

    def full(state, rnd):
        z = [state[t] + RC[rnd][t] for t in range(3)]
        y = [v ** 5 for v in z]
        return [sum((int(M[i][t]) * y[t] for t in range(3)), R([0])) for i in range(3)]

    def partial(state, rnd):
        z = [state[t] + RC[rnd][t] for t in range(3)]
        z = [z[0] ** 5, z[1], z[2]]
        return [sum((int(M[i][t]) * z[t] for t in range(3)), R([0])) for i in range(3)]

    # r=1 reduced target: rounds 2,3,4(partial),60,61,62,63.
    for rnd in (2, 3):
        state = full(state, rnd)
    state = partial(state, 4)
    for rnd in range(60, 64):
        state = full(state, rnd)
    F = state[0]
    assert F.degree() == 5 ** 7, (F.degree(), 5 ** 7)
    return F


def square_root_mod(x):
    """Tonelli-Shanks in Pallas, returning one root or None."""
    x %= P
    if x == 0:
        return 0
    if pow(x, (P - 1) // 2, P) != 1:
        return None
    q, s = P - 1, 0
    while q % 2 == 0:
        s += 1; q //= 2
    z = 5
    while pow(z, (P - 1) // 2, P) != P - 1:
        z += 1
    c = pow(z, q, P)
    r = pow(x, (q + 1) // 2, P)
    t = pow(x, q, P)
    m = s
    while t != 1:
        i, u = 1, (t * t) % P
        while u != 1:
            u = (u * u) % P; i += 1
        b = pow(c, 1 << (m - i - 1), P)
        r = (r * b) % P; c = (b * b) % P
        t = (t * c) % P; m = i
    return r


def shifted_coeffs(F, c):
    d = F.degree(); fc = F.coeffs()
    fact = [1] * (d + 1)
    for i in range(1, d + 1): fact[i] = fact[i - 1] * i % P
    ifact = [1] * (d + 1); ifact[d] = pow(fact[d], P - 2, P)
    for i in range(d, 0, -1): ifact[i - 1] = ifact[i] * i % P
    arev = R([int(fc[d - i]) * fact[d - i] % P for i in range(d + 1)])
    C, cp = [], 1
    for m in range(d + 1):
        C.append(cp * ifact[m] % P); cp = cp * c % P
    conv = arev * R(C)
    return [int(conv[d - j]) * ifact[j] % P for j in range(d + 1)]


def one_centre(F, c, line, verify_limit=2):
    d = F.degree(); shifted = shifted_coeffs(F, c)
    g = R([shifted[2 * k + 1] for k in range((d + 1) // 2)]).monic()
    assert g.degree() == (d - 1) // 2
    e = (P - 1) // 2
    hs = (X.pow_mod(e, g) - 1) % g
    H = g.gcd(hs)
    rep = g.gcd(g.derivative())
    roots_poly = (X.pow_mod(P, g) - X) % g
    total_roots = g.gcd(roots_poly).degree()
    # Factor H (normally degree 0-3); roots() returns (root,multiplicity).
    witnesses = []
    if verify_limit:
        for root, _mult in H.roots()[:verify_limit]:
            s = square_root_mod(int(root))
            if s is None or s == 0: continue
            for sign in (1, P - 1):
                wp = (c + sign * s) % P
                tau = pow(wp, INV5, P)
                nk, rho = inputs_for_tau(tau, line)
                y0 = hash_reduced(nk, rho, 1)
                wm = (c - sign * s) % P
                taum = pow(wm, INV5, P)
                nk2, rho2 = inputs_for_tau(taum, line)
                y1 = hash_reduced(nk2, rho2, 1)
                assert y0 == y1, (int(root), y0, y1)
            witnesses.append(int(root))
    return {
        "center": str(c), "roots": int(total_roots),
        "nonzero_square_roots": int(H.degree()),
        "squarefree": rep.degree() == 0, "repeated_factor_degree": int(rep.degree()),
        "verified_square_roots": witnesses,
    }


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 18920261012
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else HERE / "d189_r1_results.jsonl"
    print("building real r=1 F degree 78125", flush=True)
    line = line_setup(0); F = build_F(line)
    for tau in (0, 1, 2, 7, 12345):
        nk, rho = inputs_for_tau(tau, line)
        # independent reference is the validation path for the polynomial.
        assert int(F.evaluate(pow(tau, 5, P))) == hash_reduced(nk, rho, 1)
    print("validated_degree", F.degree(), "direct_checks", 5, flush=True)
    rng = random.Random(seed); out.parent.mkdir(parents=True, exist_ok=True)
    rows = []; t0 = time.time()
    with out.open("w", encoding="utf-8") as fp:
        for i in range(n):
            c = rng.randrange(P)
            row = one_centre(F, c, line)
            row["index"] = i; row["seed"] = seed
            fp.write(json.dumps(row, sort_keys=True) + "\n"); fp.flush()
            rows.append(row)
            print("centre", i, "roots", row["roots"], "nonzero_square", row["nonzero_square_roots"], "squarefree", row["squarefree"], "verified", row["verified_square_roots"], flush=True)
    succ = sum(r["nonzero_square_roots"] > 0 for r in rows)
    print("SUMMARY", json.dumps({"n": n, "success": succ, "fraction": succ / n if n else None,
                                  "expected": 1 - math.exp(-.5), "elapsed_s": round(time.time() - t0, 3), "out": str(out)}), flush=True)


if __name__ == "__main__":
    main()
