"""Two-block combined model (variant e, 'two-level'): block 1 is a full 2-round compression with all 16 message
words free (IV, counter 0, len 64, flags CHUNK_START); its chaining value o_i = v_i ^ v_{i+8} (i<8) feeds block 2,
which is modelled as in gd_var.build (fixed / partial / outhalf on half 02 or 13).  Family freedom = 16 + F2."""
from gd_var import PERM, COLS, DIAG, HALF, OUTW, e_inputs


def compress(prefix, init, msg, eqs, keep_diag=(0, 1, 2, 3)):
    state = list(init)
    order = list(range(16))
    ystate = None

    def G(name, idx, x, y):
        a, b, c, d = (state[i] for i in idx)
        a1, d1, c1, b1, a2, d2, c2, b2 = (f"{name}.{t}" for t in ("a1", "d1", "c1", "b1", "a2", "d2", "c2", "b2"))
        eqs.extend([
            (f"{name}:a1", (a1, a, b, x)), (f"{name}:d1", (d1, d, a1)), (f"{name}:c1", (c1, c, d1)),
            (f"{name}:b1", (b1, b, c1)), (f"{name}:a2", (a2, a1, b1, y)), (f"{name}:d2", (d2, d1, a2)),
            (f"{name}:c2", (c2, c1, d2)), (f"{name}:b2", (b2, b1, c2)),
        ])
        for i, v in zip(idx, (a2, b2, c2, d2)):
            state[i] = v

    for r, pref in ((0, ("K", "D")), (1, ("C", "E"))):
        s = [msg[order[i]] for i in range(16)]
        for j, idx in enumerate(COLS):
            G(f"{prefix}{pref[0]}{j}", idx, s[2 * j], s[2 * j + 1])
        if r == 1:
            ystate = list(state)
        for j, idx in enumerate(DIAG):
            if r == 1 and j not in keep_diag:
                continue
            G(f"{prefix}{pref[1]}{j}", idx, s[8 + 2 * j], s[9 + 2 * j])
        order = [order[p] for p in PERM]
    return state, ystate


def build_two(half="02", mode="fixed", length2=64, held=None, length1=64):
    eqs, const = [], set()
    init1 = [f"b1init{i}" for i in range(16)]
    const.update(init1)
    msg1 = [f"b1m{i}" for i in range(16)]
    st1, _ = compress("b1", init1, msg1, eqs)
    cv = [f"o{i}" for i in range(8)]
    for i in range(8):
        eqs.append((f"o{i}", (cv[i], st1[i], st1[i + 8])))
    init2 = cv + [f"init{i}" for i in range(8, 16)]
    const.update(init2[8:])
    msg2 = [f"m{i}" for i in range(16)]
    if length2 == 55:
        const.update(["m14", "m15"])
    keep = HALF[half] if mode == "outhalf" else ()
    st2, y2 = compress("", init2, msg2, eqs, keep)
    if mode == "fixed":
        held = e_inputs(half)
    if mode in ("fixed", "partial"):
        const.update(y2[int(h[1:])] if h[0] == "Y" else h for h in held)
    else:
        for i in OUTW[half]:
            eqs.append((f"out{i}", (st2[i], st2[i + 8])))
    vars_ = sorted({v for _, vs in eqs for v in vs} - const)
    return eqs, const, vars_
