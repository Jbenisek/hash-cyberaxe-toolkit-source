"""Count r1 NTT table accesses from the checked-in loop structure.

This is a source-level arithmetic model, not an execution of the participant
binary. It follows the pass/group/butterfly loops in lean_r1_mem/ntt.c and
lean.c for m=39062, amax=15, and the recorded 238 powering steps.
"""

AMAX = 15
M = 39062
STEPS = 238

def plan(a):
    rem = a
    kk = [0] * ((a + 3) // 4)
    for i in range(len(kk) - 1, -1, -1):
        k = min(4, rem)
        kk[i] = k
        rem -= k
    n = 1 << a
    return {"a": a, "n": n, "N": 3 * n, "rows": 3, "shift": AMAX - a, "kk": kk, "npass": len(kk)}

def p3(length):
    for a in range(2, AMAX + 1):
        if 3 * (1 << a) >= length:
            return plan(a)
    raise ValueError(length)

def blk(P, l0, k, b, inverse=False):
    # One table load for each nonzero idx in blk_fwd/blk_inv. The inverse has
    # the same idx test and therefore the same count.
    s = P["n"] >> (l0 + k)
    total = 0
    for j in range(k):
        half = 1 << (k - 1 - j)
        for tp in range(half):
            idx = (b + tp * s) << (l0 + j)
            total += idx != 0
    return total

def pass_g(P, l0, k, g0, g1):
    s = P["n"] >> (l0 + k)
    return sum(blk(P, l0, k, b) for _grp in range(g0, g1) for b in range(s))

def pass_full(P, l0, k):
    return pass_g(P, l0, k, 0, 1 << l0)

def fused_g(P, l0, k, g0, g1):
    # pass_fused_g invokes blk_fwd and blk_inv once per group, both with b=0.
    return sum(2 * blk(P, l0, k, 0) for _grp in range(g0, g1))

def fused(P, l0, k):
    return fused_g(P, l0, k, 0, P["n"] >> k)

def conv_core(P):
    out = 0
    for _r in range(3):
        l0 = 0
        for p in range(P["npass"] - 1):
            k = P["kk"][p]
            out += pass_full(P, l0, k)
            l0 += k
        out += fused(P, l0, P["kk"][-1])
        for p in range(P["npass"] - 2, -1, -1):
            l0 -= P["kk"][p]
            out += pass_full(P, l0, P["kk"][p])
    return out

def conv_sq(P):
    return conv_core(P)

def ntt_inv_fetches(P):
    """Twiddle loads in ntt_inv(P,...): all inverse radix-2 passes, no fused pass."""
    out = 0
    for _r in range(P["rows"]):
        l0 = P["a"]
        for p in range(P["npass"] - 1, -1, -1):
            l0 -= P["kk"][p]
            out += pass_full(P, l0, P["kk"][p])
    return out

def build_g_fetches():
    # build_g uses plan_for_len(m+1,1), one plan_theta lookup, then one
    # inverse NTT.  The optional debug inverse is disabled in lean_attack.
    P = p3(M + 1)
    return 1 + ntt_inv_fetches(P), P

def conv_otf(P):
    # conv_mulc_otf fallback for np < 3.
    out = 0
    for _r in range(3):
        l0 = 0
        for p in range(P["npass"]):
            out += pass_full(P, l0, P["kk"][p])
            l0 += P["kk"][p]
        out += fused(P, l0 - P["kk"][-1], P["kk"][-1])
        for p in range(P["npass"] - 2, -1, -1):
            l0 -= P["kk"][p]
            out += pass_full(P, l0, P["kk"][p])
    return out

def conv_half(P):
    if P["npass"] < 3:
        return conv_otf(P)
    out = 0
    npass = P["npass"]
    kl = P["kk"][-1]
    nb = P["n"] >> kl
    for _r in range(3):
        out += pass_full(P, 0, P["kk"][0])
        for h in range(2):
            l0 = P["kk"][0]
            for p in range(1, npass - 1):
                ng = 1 << l0
                out += pass_g(P, l0, P["kk"][p], h * ng // 2, (h + 1) * ng // 2)
                l0 += P["kk"][p]
            # bhalf_gen: h=1 uses tw[j<<shift] for j=1..n/2-1.
            if h == 1:
                out += (P["n"] // 2) - 1
            out += fused_g(P, l0, kl, h * nb // 2, (h + 1) * nb // 2)
            for p in range(npass - 2, 0, -1):
                l0 -= P["kk"][p]
                ng = 1 << l0
                out += pass_g(P, l0, P["kk"][p], h * ng // 2, (h + 1) * ng // 2)
        out += pass_full(P, 0, P["kk"][0])
    return out

def newton_calls():
    L = M - 1
    l = 1
    total = 0
    calls = 0
    while l < L:
        l2 = min(2 * l, L)
        total += conv_half(p3(l2 + l - 1)); calls += 1
        total += conv_half(p3(l2 - 1)); calls += 1
        l = l2
    return total, calls

n_newton, c_newton = newton_calls()
PN = p3(2 * M - 1)
PNP = p3(M + 1)
n_step = conv_sq(PN) + conv_half(PN) + conv_half(PNP)
build_g, PG = build_g_fetches()
lean_total = n_newton + STEPS * n_step
total = build_g + lean_total
print({
    "m": M,
    "newton_calls": c_newton,
    "newton_twiddle_fetches": n_newton,
    "power_step_twiddle_fetches": n_step,
    "power_steps": STEPS,
    "build_g_twiddle_fetches": build_g,
    "build_g_plan": {"a": PG["a"], "n": PG["n"], "N": PG["N"], "rows": PG["rows"]},
    "lean_power_twiddle_fetches": lean_total,
    "total_twiddle_fetches": total,
    "reconstructable_upper_bound": total,
})
