"""Validation of the exact pipeline on known positives + certificate checks on the organizer reference keccak.py.
1. Known rank-2 field (isd verify2: wordsC_3 words 0 and 46, stopped chi1): pattern_z3 must be SAT, native must pass.
2. A rank-2 field whose chi1 transitions are NOT the identity (from stage2 compatible variant pairs, tau != 0).
Certificate per field: D_aD_b = 0 on the full 1600-bit state after 3 rounds of hash-smash/verifier/keccak.py
_permute_lanes, on base points solving all conditions; controls: 4 rounds, unconditioned base; message encoding
checked against keccak.sha3_256(msg135, rounds) (first 32 bytes) and padding byte 0x86."""

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

import sys, json, random, importlib.util
import numpy as np
from exact import *

spec = importlib.util.spec_from_file_location('kref', _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/keccak.py'))
kref = importlib.util.module_from_spec(spec); spec.loader.exec_module(kref)
S = json.load(open(HERE + 'stage1_stats.json')); words = [tuple(w) for w in S['words']]
widx = {w: i for i, w in enumerate(words)}
d = np.load(HERE + 'stage1_kp.npz'); tau = d['tau']; wid = d['wid']


def lanes_of(m):
    return ls.msg_lanes(m)


def F(m, R):
    L = lanes_of(m); kref._permute_lanes(L, 64, R); return L


def certify(st, Vi, nb=2000, tag=''):
    piv = ls3.rref_rows(st.rows); rng = random.Random(99)
    def solve():
        pbs = {pb for (_, _, pb) in piv}; m = 0
        for i in range(ls.NF):
            if i not in pbs and rng.getrandbits(1): m |= 1 << i
        for (r, v, pb) in piv:
            if v ^ (bin(r & m & ~(1 << pb)).count('1') & 1): m |= 1 << pb
        return m
    nd = len(Vi)
    def comb(c):
        a = 0
        for j in range(nd):
            if (c >> j) & 1: a ^= Vi[j]
        return a
    def dd(y, a, b, R):
        r = [F(y, R), F(y ^ a, R), F(y ^ b, R), F(y ^ a ^ b, R)]
        return any(r[0][k] ^ r[1][k] ^ r[2][k] ^ r[3][k] for k in range(25))
    def pick():
        ca = rng.randrange(1, 1 << nd); cb = rng.randrange(1, 1 << nd)
        while cb == ca: cb = rng.randrange(1, 1 << nd)
        return comb(ca), comb(cb)
    f3 = sum(dd(solve() ^ comb(rng.getrandbits(nd)), *pick(), 3) for _ in range(nb))
    f4 = sum(dd(solve() ^ comb(rng.getrandbits(nd)), *pick(), 4) for _ in range(300))
    fu = sum(dd(rng.getrandbits(ls.NF), *pick(), 3) for _ in range(300))
    # message encoding vs the organizer sponge
    enc_ok = True; pad_ok = True
    for _ in range(5):
        m = solve(); L = lanes_of(m)
        raw = b''.join(x.to_bytes(8, 'little') for x in L[:17])
        pad_ok &= raw[135] == 0x86 and all(L[k] == 0 for k in range(17, 25))
        msg = raw[:135]
        for R in (3, 6):
            st6 = list(L); kref._permute_lanes(st6, 64, R)
            enc_ok &= kref.sha3_256(msg, rounds=R) == b''.join(x.to_bytes(8, 'little') for x in st6)[:32]
    return {'field': tag, 'gf2_rank': nd, 'cond_rank': len(piv), 'free_outer': ls.NF - nd - len(piv),
            'r3_DaDb_checks': nb, 'r3_fails': f3, 'r4_control_fails': f'{f4}/300', 'unconditioned_r3_fails': f'{fu}/300',
            'encoding_matches_sha3_256_r3_r6': bool(enc_ok), 'padding_0x86_and_zero_capacity': bool(pad_ok)}


def build(pairs):
    """pairs: list of (word index, tau). Returns (status, info, st, Vi)."""
    ch = [chi1_choice(words[w], int(t)) for (w, t) in pairs]
    merged = {}
    for (_, _, pr) in ch:
        for q, v in pr.items():
            if merged.get(q, v) != v: return 'chi1 clash', None, None, None
            merged[q] = v
    A2s = [ls.Pb(b1)[0] for (_, b1, _) in ch]
    stt, sol = pattern_z3(A2s)
    if stt != 'sat': return 'z3 ' + stt, None, None, None
    ok, info, st, Vi = native([words[w] for (w, _) in pairs], [pr for (_, _, pr) in ch], sol)
    if not ok: return 'native: ' + info, None, None, None
    nonid1 = sum(1 for (a1, b1, _) in ch for _ in [0] if (b1 != a1).any())
    info['chi1_nonidentity_directions'] = nonid1
    # chi2 non-identity transitions actually used
    nonid2 = 0
    for k, a2 in enumerate(st.A2s):
        for p in np.nonzero(a2)[0]:
            if st.c2.get(int(NBp[p]), 0) == 1 or st.c2.get(int(NBm[p]), 1) == 0: nonid2 += 1
    info['chi2_nonidentity_bits'] = nonid2
    return 'ok', info, st, Vi


out = {}
WC = np.load(_hca_public_path_text('__HCA_WORKSPACE__/research/sha3r6/isd/wordsC_3.npy')).astype(bool)
FREE = np.array(ls.FREE)
wa, wb = (widx[tuple(sorted(FREE[WC[i]].tolist()))] for i in (0, 46))
s, info, st, Vi = build([(wa, 0), (wb, 0)])
out['known_isd_pair_stop'] = {'status': s, 'info': info}
if s == 'ok': out['known_isd_pair_stop']['cert'] = certify(st, Vi, tag='isd words 0+46, stop chi1')
print(json.dumps(out), flush=True)

# a rank-2 field with non-identity chi1 transitions
vp = json.load(open(HERE + 'stage2.json'))['vpairs']
rng = random.Random(3); keys = list(vp); rng.shuffle(keys)
tried = 0; stats = {}; import time; t0 = time.time()
for kk in keys:
    if time.time() - t0 > 300: break
    a, b = map(int, kk.split(','))
    cand = [(i, j) for (i, j) in vp[kk] if tau[i] != 0 and tau[j] != 0]
    if not cand: continue
    i, j = cand[rng.randrange(len(cand))]
    tried += 1
    s, info, st, Vi = build([(a, int(tau[i])), (b, int(tau[j]))])
    stats[s] = stats.get(s, 0) + 1
    if s == 'ok':
        out['nonidentity_pair'] = {'words': [a, b], 'taus': [int(tau[i]), int(tau[j])], 'info': info,
                                   'cert': certify(st, Vi, tag='non-identity chi1 pair')}
        json.dump({'words': [list(words[a]), list(words[b])], 'rows': [[hex(R), v] for (R, v) in st.rows],
                   'c1': {str(k): v for k, v in st.c1.items()}, 'c2': {str(k): v for k, v in st.c2.items()}},
                  open(HERE + 'rank2_nonidentity_field.json', 'w'))
        break
    if tried >= 400: break
out['nonidentity_search'] = {'tried': tried, 'outcomes': stats}
print(json.dumps(out), flush=True)
json.dump(out, open(HERE + 'validate_result.json', 'w'))
