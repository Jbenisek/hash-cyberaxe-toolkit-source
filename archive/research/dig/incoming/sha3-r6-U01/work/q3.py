"""Q3: log2 freedom. (a) leader route (z-space dim 32, 128 sparse conditions) in F64 and F135.
(b) linstruct 2-round spaces re-measured with OUR Keccak: rank of the direction set, rank of conditions, outer freedom, and a D_aD_b check."""

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

import json, random, re
import numpy as np
from sha3lab import *
import q12

out = {}
# (a) leader route
for fmt, nv in (('F64', 512), ('F135', 1080)):
    F, dirs, conds = q12.setup(fmt)
    S, st = q12.build_sys(F, conds)
    r = S.rank()
    # rank of the 32 z directions
    zr = 32
    out[fmt] = dict(nvars=nv, cond_rank=r, z_dim=zr, log2_solutions=nv - r, log2_groups=nv - r - zr, need_log2_groups_for_N128=128 - zr,
                    headroom_bits=nv - r - zr - (128 - zr))
# leader's own 256 equations (L3,L4,L6,L7 fixed): groups
out['F64_leader_prefix'] = dict(cond_bits=256, log2_prefixes=256, note='4867f093 draws 256 random bits for L0,L1,L2,L5 and sets L3,L4,L6,L7 affinely; z lives in L0,L5 low 32 bits, so distinct groups <= 2^256 (minus the 2^32 z overlap = 2^224)')

# (b) linstruct spaces
def vint(v):
    return int.from_bytes(np.packbits(v.astype(np.uint8), bitorder='little').tobytes(), 'little')
def rank_ints(vs):
    piv = {}
    rk = 0
    for v in vs:
        while v:
            b = v.bit_length() - 1
            if b in piv: v ^= piv[b]
            else:
                piv[b] = v; rk += 1; break
    return rk
LS = _hca_public_path_text('__HCA_WORKSPACE__/research/sha3r6/linstruct/')
F135 = Forms('F135')
def two_round(Aint):
    return to_int(f_(to_lanes(Aint), 2))
def dadb(dirs_msg, cond_sys, rng, n):
    """dirs_msg: list of 1600-bit ints (message-bit directions); base msg satisfies cond_sys; test D_a D_b F2 = 0 on random span elements"""
    fails = 0
    for _ in range(n):
        m = cond_sys.sample(1080, rng) if cond_sys else rng.getrandbits(1080)
        # random coset point inside span
        def comb():
            a = 0
            for v in dirs_msg:
                if rng.getrandbits(1): a ^= v
            return a
        x = comb(); a = comb(); b = comb()
        base = state_of(m ^ x, 'F135')
        def F(dm): return two_round(to_int(base) ^ dm)
        if F(0) ^ F(a) ^ F(b) ^ F(a ^ b) != 0: fails += 1
    return fails
rng = random.Random(77)
for name in ('best_1', 'best_5'):
    V = np.load(LS + 'V_%s.npy' % name)
    cond = json.load(open(LS + 'cond_%s.json' % name))
    vs = [vint(v) for v in V]
    S = Sys()
    stat = {'new': 0, 'dep': 0, 'incons': 0}
    for q, val in cond.items():
        q = int(q)
        # chi1-input bit q value = row.m ^ const
        stat[S.add(F135.rows[q], int(val) ^ ((F135.const >> q) & 1))] += 1
    d = rank_ints(vs)
    # directions must lie in the free variables (bits < 1080)
    inside = all(v >> 1080 == 0 for v in vs)
    # z-form check: conditions must not depend on the directions
    zdep = sum(1 for v in vs for q in cond if parity(F135.rows[int(q)] & v))
    out['linstruct_' + name] = dict(listed=len(vs), gf2_rank=d, cond_bits=len(cond), cond_rank=S.rank(), cond_stat=stat, dirs_in_free_bits=inside,
                                   cond_dep_on_dirs=zdep, outer_freedom=1080 - d - S.rank(),
                                   dadb_fails=dadb(vs, S, rng, 300), dadb_checks=300)
# SOL16 35-dim space
txt = open(_hca_public_path_text('__HCA_WORKSPACE__/SOL6Cloud/SOLCLOUD_16/SOLCLOUD_16_REPORT.md'), encoding='utf-8').read().split('## Appendix B')[1]
W = [int(h, 16) for h in re.findall(r'\|PROVED\|\d+\|([0-9a-f]{80})\|', txt)]
M = (1 << 64) - 1
def lift(p):  # 320-bit source -> 1080-bit message bits: lanes 0-4 and 10-14 hold u0..u4
    m = 0
    for k in range(5):
        u = (p >> (64 * k)) & M
        m |= u << (64 * k); m |= u << (64 * (10 + k))
    return m
Wm = [lift(w) for w in W]
fails = 0
for _ in range(300):
    base = lift(rng.getrandbits(320))
    def comb():
        a = 0
        for v in Wm:
            if rng.getrandbits(1): a ^= v
        return a
    x = comb(); a = comb(); b = comb()
    st0 = to_int(state_of(base ^ x, 'F135'))
    Fn = lambda dm: two_round(st0 ^ dm)
    if Fn(0) ^ Fn(a) ^ Fn(b) ^ Fn(a ^ b) != 0: fails += 1
out['sol16_35'] = dict(listed=len(W), gf2_rank=rank_ints(Wm), source_free_bits=320, fixed_bits=760, outer_freedom=320 - rank_ints(Wm), dadb_fails=fails, dadb_checks=300,
                       note='message lifted so lanes 0-4 and 10-14 carry u0..u4; sponge match not rechecked here (done in verify_sol16.py)')
json.dump(out, open('q3_out.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
