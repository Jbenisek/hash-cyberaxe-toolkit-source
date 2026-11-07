"""Independent large-sample check of crossline-XF2 (Grok 52), numpy, one process.
Context words: the scored LINES evaluated here on numpy arrays (own evaluator), cross-checked against the scored co_ctx and
co_ref. Per context, ALL 16384 clusters' representatives (j = 0) are evaluated; on a subset of contexts all 2^19 members.
Measures: new-gate open rate (rep omega mod 128 in S7), old two-borrow gate rate, Grok's straddle guard rate (H from the
rep's own y8, and from Grok's 4-entry table), and, on the full-member subset: prefix splits, splits outside the guard,
false closes of the new gate (some member's omega mod 128 in S7 while the gate closed).
Usage: python -B rate_np.py <n_ctx_reps> <n_ctx_full> <seed>"""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys
import time
import numpy as np

sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/grok/work/job52_xf2_repgate'))
import frontline_full as F  # noqa: E402

U = np.uint32
M = F.M


def rorn(x, r):
    r &= 31
    return x if r == 0 else (x >> U(r)) | (x << U(32 - r))


def roln(x, r):
    return rorn(x, 32 - (r & 31))


def ev(e, env):
    if isinstance(e, int):
        return U(e)
    if isinstance(e, str):
        return env[e]
    if e[0] == "sum":
        acc = None
        for t in e[1]:
            if isinstance(t, tuple) and t[0] == "neg":
                v = U(0) - ev(t[1], env)
            else:
                v = ev(t, env)
            acc = v if acc is None else acc + v
        return acc
    if e[0] == "xor":
        return ev(e[1], env) ^ ev(e[2], env)
    if e[0] == "ror":
        return rorn(ev(e[1], env), e[2])
    raise ValueError(e)


def contexts(ow):
    """ow: (7, n) uint32 outer words in OUTER_WORDS order. Returns dict of the 39 context lines."""
    env = {F.OUTER_WORDS[i]: ow[i] for i in range(7)}
    env["fl"] = np.full(ow.shape[1], F.FLAGS, dtype=U)
    for n in F.CONTEXT_LINES:
        env[n] = ev(F.DEF[n], env)
    return env


S7T = np.array([F.S7 >> w & 1 for w in range(128)], dtype=bool)
E1REP = np.array([F.cmember(g, 0)[0] for g in range(1 << 14)], dtype=U)
E1ALL = np.array([[F.cmember(g, j)[0] for j in range(32)] for g in range(1 << 14)], dtype=U)   # (16384, 32)
Y3 = U(F.Y3)
RX15 = U(F.rol(F.X15, 8))
LQ0 = U(F.rol(F.X15, 24))
YHI = np.array([0xF2, 0xFA, 0x02, 0x0A], dtype=U)


def omega(e1, b, c, d, A, S15, SS):
    y = e1 - Y3
    y8 = roln(y, 7) ^ b
    y12 = y8 - c
    y0 = roln(y12, 8) ^ d
    x0 = y0 - A
    d0a1 = rorn(x0 ^ RX15, 16) ^ S15
    om = e1 + d0a1 - SS
    return om, y0, y8


def run(n_rep, n_full, seed):
    rng = np.random.default_rng(seed)
    t0 = time.time()
    tot = dict(cl=0, new_open=0, old_open=0, guard=0, guard_tab=0, guard_tab_mismatch=0, byte_eq=0,
               guard_not_block_const=0, blocks_off=0, blocks_off_not_26=0, blocks_off_not_parity_class=0,
               extra_opens_on_guard=0, ctx_over_6656_plus_fires=0, beq_clusters_full=0, beq_split=0,
               beq_split_outside_guard=0, beq_false_close=0, beq_rep_mismatch=0,
               full_cl=0, split=0, split_out=0, false_close=0, guard_full=0, gate_open_full=0, ctx_rates=[])
    # cross-check of the evaluator against the scored co_ctx / co_ref on 64 contexts x 4 members
    ow = rng.integers(0, 1 << 32, size=(7, 64), dtype=np.uint64).astype(U)
    env = contexts(ow)
    xbad = 0
    for i in range(64):
        w = [int(ow[k, i]) for k in range(7)]
        cx = F.co_ctx(*w, F.FLAGS)
        xbad += any(int(env[n][i]) != cx[F.nm(n)] for n in F.CONTEXT_LINES)
        b, c, d = (env["C0.b1"][i], env["C0.c1"][i], env["C0.d1"][i])
        A = b + env["w6"][i] + env["X4"][i] + env["w2"][i]
        SS = env["S0"][i] + env["S5"][i]
        for g in (0, 1, 777, 16383):
            for j in (0, 9, 31):
                e1 = U(F.cmember(g, j)[0])
                om = omega(np.array([e1]), b, c, d, A, env["S15"][i] ^ LQ0 ^ LQ0, SS)[0][0]
                ref = F.co_ref(*w, (int(e1) - F.Y3) & M, F.FLAGS)[0]
                xbad += int(om) != ref
    print("evaluator_vs_scored_mismatches", xbad, flush=True)
    assert xbad == 0
    CH = 64
    done = 0
    while done < n_rep:
        n = min(CH, n_rep - done)
        ow = rng.integers(0, 1 << 32, size=(7, n), dtype=np.uint64).astype(U)
        env = contexts(ow)
        b, c, d = env["C0.b1"][:, None], env["C0.c1"][:, None], env["C0.d1"][:, None]
        A = (env["C0.b1"] + env["w6"] + env["X4"] + env["w2"])[:, None]
        S15 = env["S15"][:, None]
        SS = (env["S0"] + env["S5"])[:, None]
        e1 = E1REP[None, :]
        om, y0, y8 = omega(e1, b, c, d, A, S15, SS)
        new = S7T[om & U(127)]
        # old gate: a = (Y0>>16) - (A>>16) mod 128 , c = e1 - SS mod 128, q = L mod 128
        a = ((y0 >> U(16)) - (A >> U(16))) & U(127)
        cc = (e1 - SS) & U(127)
        q = (LQ0 ^ S15) & U(127)
        old = S7T[((a ^ q) + cc) & U(127)] | S7T[(((a - U(1)) & U(127)) ^ q) + cc & U(127)]
        # Grok's straddle guard, H from the rep's own y8 (reference) and from the 4-entry table
        H = ((y8 >> U(24)) - (c >> U(24))) & U(255)
        d0 = d & U(255)
        lo0, lo1 = H ^ d0, ((H - U(1)) & U(255)) ^ d0
        Alo = A & U(255)
        beq = ((y0 >> U(8)) & U(255)) == ((A >> U(8)) & U(255))
        strad = (np.minimum(lo0, lo1) < Alo) & (Alo <= np.maximum(lo0, lo1))
        guard = beq & strad
        Ht = ((YHI[(e1 >> U(20)) & U(3)] ^ (b >> U(24))) - (c >> U(24))) & U(255)
        lt0, lt1 = Ht ^ d0, ((Ht - U(1)) & U(255)) ^ d0
        guard_t = beq & (np.minimum(lt0, lt1) < Alo) & (Alo <= np.maximum(lt0, lt1))
        gate_new = np.where(guard, old, new)
        # block lemma (DERIVED in RESULT.md): for fixed g bits 6..13 (64-cluster block) the guard is constant and,
        # when it is off, the 64 representatives' omega mod 128 are the 64 residues of one parity class -> 26 in S7
        gb = guard.reshape(n, 256, 64)
        tot["guard_not_block_const"] += int((gb.any(axis=2) != gb.all(axis=2)).sum())
        nb = new.reshape(n, 256, 64).sum(axis=2)
        offb = ~gb[:, :, 0]
        tot["blocks_off"] += int(offb.sum())
        tot["blocks_off_not_26"] += int(((nb != 26) & offb).sum())
        res = np.sort((om & U(127)).reshape(n, 256, 64), axis=2)
        par = res[:, :, :1] & U(1)
        full_class = (res == (np.arange(64, dtype=U)[None, None, :] * U(2) + par)).all(axis=2)
        tot["blocks_off_not_parity_class"] += int((~full_class & offb).sum())
        tot["extra_opens_on_guard"] += int((guard & old & ~new).sum())
        tot["ctx_over_6656_plus_fires"] += int((gate_new.sum(axis=1) > 6656 + guard.sum(axis=1)).sum())
        # all 32 members of every cluster with Y0[8..15] == A[8..15] (the only clusters whose borrow into x0 bit 16
        # can move), in every context: real prefix splits, splits outside Grok's guard, false closes of the new gate
        ci, gi = np.nonzero(beq)
        if ci.size:
            omb = omega(E1ALL[gi], b[ci], c[ci], d[ci], A[ci], S15[ci], SS[ci])[0]             # (m, 32)
            pb = omb & U(511)
            spl = (pb != pb[:, :1]).any(axis=1)
            tot["beq_clusters_full"] += int(ci.size)
            tot["beq_split"] += int(spl.sum())
            tot["beq_split_outside_guard"] += int((spl & ~guard[ci, gi]).sum())
            tot["beq_false_close"] += int((S7T[omb & U(127)].any(axis=1) & ~gate_new[ci, gi]).sum())
            tot["beq_rep_mismatch"] += int((omb[:, 0] != om[ci, gi]).sum())
        tot["cl"] += new.size
        tot["new_open"] += int(gate_new.sum())
        tot["old_open"] += int(old.sum())
        tot["guard"] += int(guard.sum())
        tot["guard_tab"] += int(guard_t.sum())
        tot["guard_tab_mismatch"] += int((guard != guard_t).sum())
        tot["byte_eq"] += int(beq.sum())
        tot["ctx_rates"].extend((gate_new.sum(axis=1) / 16384.0).tolist())
        # full-member check on the first contexts of the chunk while n_full lasts
        nf = min(n, n_full - tot["full_cl"] // 16384)
        for i in range(max(nf, 0)):
            omf = omega(E1ALL, b[i], c[i], d[i], A[i], S15[i], SS[i])[0]           # (16384, 32)
            p9 = omf & U(511)
            split = (p9 != p9[:, :1]).any(axis=1)
            alive_any = S7T[omf & U(127)].any(axis=1)
            tot["full_cl"] += 16384
            tot["split"] += int(split.sum())
            tot["split_out"] += int((split & ~guard[i]).sum())
            tot["false_close"] += int((alive_any & ~gate_new[i]).sum())
            tot["guard_full"] += int(guard[i].sum())
            tot["gate_open_full"] += int(gate_new[i].sum())
            assert (p9[:, 0] == (om[i] & U(511))).all()
        done += n
        if done % (CH * 256) == 0:
            print("progress", done, "sec %.1f" % (time.time() - t0), "rate", tot["new_open"] / tot["cl"], flush=True)
    r = np.array(tot.pop("ctx_rates"))
    p = tot["new_open"] / tot["cl"]
    se = r.std(ddof=1) / np.sqrt(len(r))
    print("contexts", len(r), "clusters", tot["cl"], "seconds %.1f" % (time.time() - t0))
    for k, v in tot.items():
        print(k, v)
    print("new_gate_open_rate", p, "se_over_contexts", se, "z_vs_52/128", (p - 52 / 128) / se,
          "ctx_rate_std", r.std(ddof=1))
    print("old_gate_open_rate", tot["old_open"] / tot["cl"])
    print("guard_rate", tot["guard"] / tot["cl"], "bound 9/65536", 9 / 65536, "byte_eq_rate", tot["byte_eq"] / tot["cl"])
    print("upper_99.9pct_one_sided", p + 3.09 * se)


if __name__ == "__main__":
    run(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
