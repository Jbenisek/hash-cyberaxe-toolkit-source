"""Side check: the greedy hitting search on the NATIVE 1-round-affine space U320 (lane 16 = 0x86<<56) found a 2-round-
affine subspace of dimension > 40 (W40's). Regenerate, save, and spot-check it:
 (a) per-row chi1 test (exact linear algebra; round 0 is affine on all of U320, checked in fields.py);
 (b) state after round 2 affine: second differences on random cosets;
 (c) cube sums: dim 2 zero after round 2; dim 17 zero / dim 16 nonzero on the digest after round 6.
Usage: python native_bigger.py SEED SECONDS NCUBES"""
import sys, json, time, random
import numpy as np
import symlib as S

seed, secs, ncub = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
rng = random.Random(seed)
c, F = S.affine_map(S.NATIVE, 'chi1in')
pairs = S.chi_pairs(F)
best = None; runs = 0; hist = {}; t0 = time.time()
while time.time() - t0 < secs:
    Q = S.hitting_greedy(pairs, rng, rng.choice((0, 0, 1, 2)))
    d = 320 - S.rank(Q); runs += 1; hist[d] = hist.get(d, 0) + 1
    if best is None or d > best[0]:
        best = (d, Q)
V = S.annihilator(best[1], 320)
rec = {'best_dim': len(V), 'runs': runs, 'top_of_histogram': dict(sorted(hist.items())[-5:]),
       'failing_pairs': S.check_pairs_on(pairs, V), 'rank': S.rank(V),
       'dim_cap_W40': len(S.intersect(V, S.cd.W, 320))}
print(json.dumps(rec), flush=True)
json.dump({'basis': [hex(v) for v in V], **rec}, open('native_bigger_field.json', 'w'))

# (b) second differences of the state after round 2 on random cosets
bad = 0; pts = []
for _ in range(256):
    t = rng.getrandbits(320); a = S.combine(rng.getrandbits(len(V)), V); b = S.combine(rng.getrandbits(len(V)), V)
    pts += [t, t ^ a, t ^ b, t ^ a ^ b]
A = None
for r, A in S.states(S.unpack_src(pts), S.NATIVE, 2):
    pass
for L in A:
    v = L.reshape(-1, 4)
    bad += int(np.count_nonzero(v[:, 0] ^ v[:, 1] ^ v[:, 2] ^ v[:, 3]))
print(json.dumps({'round2_second_diff_nonzero_words_of_256x25': bad}), flush=True)

# (c) cube sums
for k, r in ((2, 2), (3, 3), (16, 6), (17, 6)):
    nz = 0
    for _ in range(ncub):
        t = rng.getrandbits(320)
        while True:
            dd = [S.combine(rng.getrandbits(len(V)) or 1, V) for _ in range(k)]
            if S.rank(dd) == k:
                break
        for rr, A in S.states(S.cd.points(t, dd), S.NATIVE, r):
            pass
        s = [int(np.bitwise_xor.reduce(a)) for a in (A if r < 6 else A[:4])]
        nz += any(s)
    print(json.dumps({'cube_dim': k, 'after_round': r, 'nonzero_sums': nz, 'cubes': ncub}), flush=True)
