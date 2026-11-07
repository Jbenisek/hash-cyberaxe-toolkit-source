
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

import csv, math, collections, sys
csv.field_size_limit(10**8)
p = _hca_public_path_text('__HCA_WORKSPACE__/research/rivals/BOARDS_TABLE.tsv')
rows = list(csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"))
cnt = collections.Counter(r["track"] for r in rows)
print("TSV rows per track:", dict(cnt))
for t in ("sha256-r37-exploratory", "sha256-r38-exploratory"):
    rr = [r for r in rows if r["track"] == t]
    rr.sort(key=lambda r: r["created"], reverse=True)
    print(t, "newest 4:", [(r["id8"], r["user"], r["status"], r["official"], r["created"]) for r in rr[:4]])

L = math.log2
print("\n--- r37 leader arithmetic (inputs DERIVED from d3ec5c41 / 7319bba9 / 1c368173 notes) ---")
T = 10005628052435696944197 / 2644
print("T units log2 =", round(L(T), 5))
A_C, A_S, DEV = 2**60, 2**50, 2**40
online = T - A_C - A_S - DEV
print("online (T - allowances) log2 =", round(L(online), 4), " A_C share =", round(A_C / T, 4))
NFB = 358768880796199274
print("N_FB log2 =", round(L(NFB), 4), " per-FB units =", round(online / NFB, 3))
q3 = 2**-74.03
mu0 = 0.49466253
cand = mu0 / q3
print("Step-3 candidates needed log2 =", round(L(cand), 3), " per FB log2 =", round(L(cand / NFB), 3))
gp = cand / 32
print("good pairs needed log2 =", round(L(gp), 3))
for ops in (17, 10, 5):
    fl = gp * ops / 2644
    print(f"floor if only good-pair stage at {ops} ops: online 2^{L(fl):.3f}, total with A_C 2^{L(fl + A_C):.3f}")
# first-block compression share and SWAR replacement
fb = NFB * 1.0
for c in (0.15, 0.08):
    t2 = T - fb + NFB * c
    print(f"first block charged {c} units instead of 1: total 2^{L(t2):.4f} (delta {L(t2) - L(T):+.4f})")
# q3 gain sensitivity
for g in (1.18, 1.3, 2, 4):
    t2 = online / g + A_C + A_S + DEV
    print(f"q3 x{g}: total 2^{L(t2):.4f} (delta {L(t2) - L(T):+.4f}); with A_C=2^46: 2^{L(online / g + 2**46 + A_S + DEV):.4f}")
print("A_C=2^46 alone:", round(L(online + 2**46 + A_S + DEV), 4))

print("\n--- r38 leader arithmetic (inputs DERIVED from 0ae69bcb / c99df2dc notes) ---")
NG = 2**68.43337
per = 1 + 256 * 117 / 2728
print("per group units =", round(per, 3), " online log2 =", round(L(NG * per), 4), "(note says 2^72.016)")
allow = 2**70 + 2**70 + 2**64
tot = 2**72.01600 + 2**67.21233 + allow
print("total log2 =", round(L(tot), 4), "(note: 72.633442)")
for f in (0.5, 0.25):
    o = NG * (1 + 256 * 117 * f / 2728)
    print(f"per-(CV,A0) work x{f}: online 2^{L(o):.3f}, total 2^{L(o + 2**67.21233 + allow):.3f}, with A_C=A_S=2^50: 2^{L(o + 2**67.21233 + 2**51 + 2**64):.3f}")
for g in (1.3, 2, 4):
    o = 2**72.016 / g
    print(f"q3 x{g}: total 2^{L(o + 2**67.21233 + allow):.3f}")
print("allowances only (A_C=A_S=2^50, DEV 2^64):", round(L(2**72.016 + 2**67.21233 + 2**51 + 2**64), 4))

print("\n--- GPU sizing (GUESS inputs: RTX 3090 ~2^33.1 full SHA-256/s) ---")
rate64 = 2**33.1
rate37 = rate64 * 64 / 37
print("37-step comps per 30 min log2 =", round(L(rate37 * 1800), 2), " per day log2 =", round(L(rate37 * 86400), 2))
print("days for 2^58.32 first blocks =", round(2**58.32 / (rate37 * 86400), 1))
print("2^51 simple ops at ~2^44 int ops/s (GUESS): seconds =", round(2**51 / 2**44, 1))
