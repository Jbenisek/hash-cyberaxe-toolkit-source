"""Step 1: are there z-period-closed sub-fields of the 1-round-affine family U320 and of the 2-round-affine family?
(1) self-checks: sponge == organizer sha3_256(rounds=6) for native and p-periodic lane 16; round 0 affine on U320.
(2) the per-row chi1 test reproduces W40 (native lane 16): 0 failing pairs expected.
(3) calibration: greedy minimum hitting subspace on the full native U320 (N=320) vs W40's 40.
(4) W40 vs rotation: dim(W40 cap Sym_p), dim(W40 cap rot_p W40), largest rot_p-invariant subspace of W40.
(5) for p = 8,16,32 (p-periodic lane 16) and for every p with the native lane 16: largest symmetric 2-round-affine
    subspace found by the greedy search inside Sym_p cap U320 (dim 5p). Saves bases to fields_out.json.
Usage: python fields.py SEED SECONDS_PER_CONFIG"""
import sys, json, time, random
import symlib as S

seed, budget = int(sys.argv[1]), float(sys.argv[2])
rng = random.Random(seed)
out = {'seed': seed}
P_ALL = (1, 2, 4, 8, 16, 32)

# (1) self-checks
for p in (None, 8, 16, 32):
    l16 = S.lane16_for(p)
    out[f'selfcheck_l16_{p or 64}'] = {'lane16': hex(l16), 'sponge_vs_organizer': S.selfcheck(l16, rng),
                                       'round0_second_diff_nonzero_words': S.round0_affine_check(l16, rng)}
print(json.dumps({k: v for k, v in out.items() if k.startswith('selfcheck')}), flush=True)

# (2) native chi1 forms over U320 and the W40 check
c_nat, F_nat = S.affine_map(S.NATIVE, 'chi1in')
P_nat = S.chi_pairs(F_nat)
W = S.cd.W
out['native_nontrivial_pairs_U320'] = len(P_nat)
out['W40_rank'] = S.rank(W)
out['W40_failing_pairs'] = S.check_pairs_on(P_nat, W)
print(json.dumps({k: out[k] for k in ('native_nontrivial_pairs_U320', 'W40_rank', 'W40_failing_pairs')}), flush=True)


def search(pairs, N, secs, tag):
    t0 = time.time(); best = None; runs = 0; hist = {}
    while time.time() - t0 < secs:
        slack = rng.choice((0, 0, 1, 2))
        Q = S.hitting_greedy(pairs, rng, slack)
        d = N - S.rank(Q)
        hist[d] = hist.get(d, 0) + 1
        runs += 1
        if best is None or d > best[0]:
            best = (d, Q)
    d, Q = best
    V = S.annihilator(Q, N)
    assert len(V) == d
    bad = S.check_pairs_on(pairs, V)
    print(json.dumps({'config': tag, 'N': N, 'pairs': len(pairs), 'best_dim': d, 'runs': runs,
                      'dim_histogram': dict(sorted(hist.items())), 'verify_failing_pairs': bad}), flush=True)
    return d, V, bad, runs, hist


# (3) calibration on the full native space
d, V, bad, runs, hist = search(P_nat, 320, budget, 'native_full_U320')
out['calib_native_full'] = {'best_dim': d, 'runs': runs, 'hist': hist, 'failing': bad}

# (4) W40 vs rotations
w40 = {}
for p in P_ALL:
    sym = S.sym_basis(p)
    rotW = [S.rot_src(w, p) for w in W]
    inv = list(W)
    for k in range(1, 64 // p):
        inv = S.intersect(inv, [S.rot_src(w, k * p) for w in W], 320) if inv else []
    w40[p] = {'dim_W40_cap_Sym_p': len(S.intersect(W, sym, 320)),
              'dim_W40_cap_rot_p_W40': len(S.intersect(W, rotW, 320)),
              'dim_largest_rot_p_invariant_subspace': len(inv)}
out['W40_rotation'] = w40
print(json.dumps({'W40_rotation': w40}), flush=True)

# (5) symmetric sub-fields
res = {}
bases = {}
for p in P_ALL:
    sym = S.sym_basis(p)
    variants = [('native_l16', S.NATIVE)] + ([('periodic_l16', S.lane16_for(p))] if p >= 8 else [])
    for name, l16 in variants:
        c, F = (c_nat, F_nat) if l16 == S.NATIVE else S.affine_map(l16, 'chi1in')
        Fr = [S.restrict(f, sym) for f in F]
        per_ok = all(Fr[64 * L + z] == Fr[64 * L + (z + p) % 64] for L in range(25) for z in range(64))
        pairs = S.chi_pairs(Fr)
        N = 5 * p
        if pairs:
            d, Vc, bad, runs, hist = search(pairs, N, budget if p >= 8 else min(budget, 20), f'p{p}_{name}')
        else:
            d, Vc, bad, runs, hist = N, [1 << i for i in range(N)], 0, 0, {}
        V320 = [S.combine(v, sym) for v in Vc]
        res[f'p{p}_{name}'] = {'lane16': hex(l16), 'sym_dim': N, 'forms_p_periodic': per_ok,
                               'nontrivial_pairs': len(pairs), 'best_2round_affine_dim': d,
                               'failing_pairs': bad, 'runs': runs}
        bases[f'p{p}_{name}'] = [hex(v) for v in V320]
out['symmetric'] = res
json.dump({'summary': out, 'bases': bases}, open('fields_out.json', 'w'), indent=1)
print(json.dumps({'symmetric': res}), flush=True)
