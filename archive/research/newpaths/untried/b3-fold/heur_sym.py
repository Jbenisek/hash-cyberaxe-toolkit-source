"""Heuristic and symmetry checks at the fold, on REAL pinned 55/63 pairs (2-round BLAKE3).

H1 avalanche: flip one bit of one of the 9 free words (a neighbour inside the real family); Hamming distance of
   the 128-bit residual R = (dh1, dh3, dh4, dh6) and of the fold-algebra words.
H2 greedy descent on HW(R) over all 288 one-bit neighbours vs random sampling with the same number of evaluations.
S1 fold involution i <-> i+8 on the round-1 diagonal calls (index check).
S2 G role-swap equivariance (a c)(b d): swap(G(a,b,c,d;x,y)) vs G(c,d,a,b;x,y) on random inputs.
S3 swap-collision special case on real pairs: Z^B_w = Z^A_{w+8} and Z^B_{w+8} = Z^A_w.
Usage: python -B heur_sym.py [seed]
"""
import json
import os
import sys
import time
import numpy as np
import b3fold_gen as g

U = np.uint32
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 99
HERE = os.path.dirname(os.path.abspath(__file__))
t0 = time.time()
res = {}


def residual(F):
    WA, WB, tl = g.build_pairs_v(F)
    ZA = g.compress2_v(WA, tl, g.LEN_A)
    ZB = g.compress2_v(WB, tl, g.LEN_B)
    d = {i: ZA[i] ^ ZB[i] for i in (1, 3, 4, 6, 9, 11, 12, 14)}
    r = [d[w] ^ d[w + 8] for w in (1, 3, 4, 6)]
    return r, ZA, ZB


def hw(r):
    return sum(np.bitwise_count(x).astype(np.int32) for x in r)


rng = np.random.default_rng(SEED)

# ---- H1 avalanche
M = 1 << 18
F = rng.integers(0, 2**32, size=(9, M), dtype=U)
j = rng.integers(0, 9, size=M)
b = rng.integers(0, 32, size=M).astype(U)
F2 = F.copy()
F2[j, np.arange(M)] ^= (U(1) << b)
r0, _, _ = residual(F)
r1, _, _ = residual(F2)
hd = hw([x ^ y for x, y in zip(r0, r1)])
w4a = r0[2] ^ g.rv(r0[0], 8); w4b = r1[2] ^ g.rv(r1[0], 8)
w6a = r0[3] ^ g.rv(r0[1], 8); w6b = r1[3] ^ g.rv(r1[1], 8)
hd4 = np.bitwise_count(w4a ^ w4b); hd6 = np.bitwise_count(w6a ^ w6b)
res["H1"] = dict(M=M, mean_hd_R=float(hd.mean()), sd_hd_R=float(hd.std()), min_hd_R=int(hd.min()),
                 frac_hd_le_48=float((hd <= 48).mean()), frac_hd_le_32=float((hd <= 32).mean()),
                 mean_hd_w4p=float(hd4.mean()), mean_hd_w6p=float(hd6.mean()),
                 per_free_word_mean_hd=[float(hd[j == k].mean()) for k in range(9)],
                 per_free_word_min_hd=[int(hd[j == k].min()) for k in range(9)],
                 mean_hw_R=float(hw(r0).mean()))

# ---- H2 greedy descent vs random sampling, equal evaluation budget
S, T = 1024, 20
cur = rng.integers(0, 2**32, size=(9, S), dtype=U)
cur_hw = hw(residual(cur)[0])
start_hw = cur_hw.copy()
evals = 0
steps_improved = np.zeros(S, dtype=np.int32)
for step in range(T):
    best_hw = cur_hw.copy(); best_F = cur.copy()
    for k in range(9):
        Fk = np.repeat(cur, 32, axis=1)              # (9, S*32): each start repeated for 32 bits
        bits = np.tile(np.arange(32, dtype=U), S)
        Fk[k] ^= (U(1) << bits)
        h = hw(residual(Fk)[0]).reshape(S, 32)
        evals += S * 32
        arg = h.argmin(axis=1)
        hmin = h[np.arange(S), arg]
        better = hmin < best_hw
        best_hw = np.where(better, hmin, best_hw)
        cand = cur.copy(); cand[k] ^= (U(1) << arg.astype(U))
        best_F[:, better] = cand[:, better]
    improved = best_hw < cur_hw
    steps_improved += improved
    cur, cur_hw = best_F, best_hw
per_start = evals // S
# random baseline: same number of evaluations per start, min HW over them (sampled in chunks)
rand_min = np.full(S, 999, dtype=np.int32)
chunk = 1 << 20
done = 0
tot = per_start * S
while done < tot:
    n = min(chunk, tot - done)
    Fr = rng.integers(0, 2**32, size=(9, n), dtype=U)
    h = hw(residual(Fr)[0])
    idx = (np.arange(done, done + n) // per_start)
    np.minimum.at(rand_min, idx, h)
    done += n
res["H2"] = dict(starts=S, steps=T, evals_per_start=int(per_start),
                 greedy_final_hw_mean=float(cur_hw.mean()), greedy_final_hw_min=int(cur_hw.min()),
                 greedy_start_hw_mean=float(start_hw.mean()),
                 greedy_mean_improving_steps=float(steps_improved.mean()),
                 random_min_hw_mean=float(rand_min.mean()), random_min_hw_min=int(rand_min.min()))

# ---- S1 fold involution on round-1 diagonal calls
diag = {"E0": (0, 5, 10, 15), "E1": (1, 6, 11, 12), "E2": (2, 7, 8, 13), "E3": (3, 4, 9, 14)}
roles = "abcd"
pos2 = {p: (nm, roles[i]) for nm, t in diag.items() for i, p in enumerate(t)}
res["S1"] = {nm: [f"{roles[i]}->{pos2[(p + 8) % 16][0]}.{pos2[(p + 8) % 16][1]}" for i, p in enumerate(t)]
             for nm, t in diag.items()}

# ---- S2 G role-swap equivariance
n = 1 << 20
a, bb, c, dd, x, y = (rng.integers(0, 2**32, size=n, dtype=U) for _ in range(6))
o1 = g.Gv(a, bb, c, dd, x, y)
o2 = g.Gv(c, dd, a, bb, x, y)
sw = (o1[2], o1[3], o1[0], o1[1])   # role-swap of the first output
eqbits = sum(32 - np.bitwise_count(p ^ q).astype(np.int64) for p, q in zip(sw, o2))
eqwords = sum((p == q).astype(np.int64) for p, q in zip(sw, o2))
z = np.zeros(n, dtype=U)
o1z = g.Gv(a, bb, c, dd, z, z); o2z = g.Gv(c, dd, a, bb, z, z)
swz = (o1z[2], o1z[3], o1z[0], o1z[1])
eqbits_z = sum(32 - np.bitwise_count(p ^ q).astype(np.int64) for p, q in zip(swz, o2z))
res["S2"] = dict(n=n, frac_equal_bits=float(eqbits.mean() / 128), words_equal_total=int(eqwords.sum()),
                 frac_equal_bits_xy0=float(eqbits_z.mean() / 128))

# ---- S3 swap-collision special case on real pairs
n = 1 << 22
Fs = rng.integers(0, 2**32, size=(9, n), dtype=U)
_, ZA, ZB = residual(Fs)
sw_any = np.zeros(n, dtype=bool)
sw_lo16 = 0
for w in (1, 3, 4, 6):
    e = (ZB[w] == ZA[w + 8]) & (ZB[w + 8] == ZA[w])
    sw_any |= e
    sw_lo16 += int(((((ZB[w] ^ ZA[w + 8]) | (ZB[w + 8] ^ ZA[w])) & U(0xFF)) == 0).sum())
res["S3"] = dict(n=n, pairs_with_any_word_swapped=int(sw_any.sum()),
                 low8_swap_events_summed_over_4_words=int(sw_lo16),
                 low8_expected_if_random=float(4 * n * 2.0 ** -16))
res["seconds"] = round(time.time() - t0, 1)
with open(os.path.join(HERE, f"heur_sym_out_s{SEED}.json"), "w", encoding="utf-8") as fh:
    json.dump(res, fh, indent=1)
print(json.dumps(res, indent=1))
