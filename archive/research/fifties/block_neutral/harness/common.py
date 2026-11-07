'''Shared definitions for the block-neutrality harness (Python side).

- imports the split_e3 design (ev.py, read-only), halfsearch constants (via ev/rels) and the ORGANIZER blake3.py
- the three coordinate frames (D = design, O = outer basis, R = real compression inputs)
- ref_derive(frame, coords) -> real inputs; ref_obs(real) -> observables from the organizer compression;
  ref_apply(config, frame, mask) -> (damage, info, chk, obs) : the pure-Python reference that the C harness is checked against.
'''

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

import sys, os, importlib.util
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SPLIT = _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3')
sys.path.insert(0, SPLIT)
import ev                                    # noqa: E402  (also loads rels and halfsearch)
hs = ev.hs; rels = ev.rels; M = 0xFFFFFFFF
_spec = importlib.util.spec_from_file_location('org_blake3', _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/blake3.py'))
B3 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(B3)
ROUNDS, FLAGS, LEN_A, LEN_B = 2, hs.CTR_FLAGS, hs.LEN_A, hs.LEN_B
DESIGN = ev.Design(*ev.DESIGN)
def rol(x, n): return ((x << n) | (x >> (32 - n))) & M if n % 32 else x
def ror(x, n): return rol(x, (32 - n) % 32)

# ---------------- frames ----------------
FRAME_D = ['Y4', 'Y9', 'w8', 'D2.b1', 'D3.a1', 'K0.b1', 'K3.d1', 'S14', 'S15', 'C0.b1', 'Y14']
FRAME_O = ['C0.d1', 'D2.a1', 'D2.b1', 'S11', 'S4', 'X9', 'w6', 'Y4', 'T1', 'E1.c1']
FRAME_R = ['w0', 'w1', 'w2', 'w3', 'w5', 'w6', 'w7', 'w8', 'w9', 'w10', 'w11', 'w12', 'T0', 'T1']
FRAMES = {'D': FRAME_D, 'O': FRAME_O, 'R': FRAME_R}
FRAME_ID = {'D': 0, 'O': 1, 'R': 2}
assert tuple(FRAME_D[:3]) == DESIGN.F and tuple(FRAME_D[3:9]) == DESIGN.B and FRAME_D[9] == DESIGN.g
O_BASIS = FRAME_O[:9]
O_ORDER, _o_checks, _kn = ev.order(set(O_BASIS))
assert not _o_checks and _kn >= set(ev.WORDS)

def trial_words(v, c1):
    '''the starred lines of hs.ctr_trial for E1.c1 = c1, without the T0 = 0 rejection (counter 2 has T1 >= 1).'''
    v = dict(v); v['E1.c1'] = c1; v['E1.d1'] = (c1 - hs.Y11) & M
    v['E1.a1'] = rol(v['E1.d1'], 16) ^ v['Y12']; v['Y6'] = (v['E1.a1'] - v['Y1'] - v['w12']) & M
    v['Y10'] = rol(v['Y6'], 7) ^ v['C2.b1']; v['Y14'] = (v['Y10'] - v['C2.c1']) & M
    v['Y2'] = rol(v['Y14'], 8) ^ v['C2.d1']; v['w0'] = (v['Y2'] - v['C2.a1'] - v['C2.b1']) & M
    v['K0.a1'] = (hs.IV[0] + hs.IV[4] + v['w0']) & M; v['T0'] = rol(v['K0.d1'], 16) ^ v['K0.a1']
    v['w1'] = (v['S0'] - v['K0.a1'] - v['K0.b1']) & M
    r = hs.ctr_trial(v, c1)                      # cross-check against the halfsearch code where it is defined
    if r is not None:
        tv = r[3]
        assert all(tv[k] == v[k] for k in ('Y14', 'w0', 'w1', 'T0', 'Y6')), 'trial lines disagree with hs.ctr_trial'
    return v

def check_value(v):
    r = ev.REL[DESIGN.chk]
    if r[0] == 'add': return (sum(c * v[w] for w, c in r[1].items()) + r[2]) & M
    x = r[2]
    for w, k in r[1]: x ^= rol(v[w], k)
    return x

def ref_derive(frame, c):
    '''coords (list of 32-bit words in frame order) -> (all words dict, frame-D check value or 0).'''
    if frame == 'R':
        return dict(zip(FRAME_R, c)), 0
    if frame == 'D':
        start = dict(zip(FRAME_D[:10], c[:10]))
        v, _ = DESIGN.run(start)
        chk = check_value(v)
        c1 = ev.c1_from_y14(v, c[10])
        return trial_words(v, c1), chk
    v = dict(zip(O_BASIS, c[:9]))
    for i, w in O_ORDER: v[w] = ev.solve1(ev.REL[i], w, v)
    return trial_words(v, c[9]), 0

def real_of(v): return [v[k] for k in FRAME_R]

# ---------------- organizer compression with intermediates ----------------
def compress_trace(words, counter, block_len, flags):
    '''mirror of the organizer _compress (blake3.py, rounds = 2) using its own _g; records S (after round-1 columns),
    X (after round 1), Y (after round-2 columns), Z (final). Asserts equality with B3._compress.'''
    v = list(B3.IV) + list(B3.IV[:4]) + [counter & M, counter >> 32, block_len, flags]
    m = list(words); tr = {}
    for r in range(ROUNDS):
        B3._g(v, 0, 4, 8, 12, m[0], m[1]); B3._g(v, 1, 5, 9, 13, m[2], m[3])
        B3._g(v, 2, 6, 10, 14, m[4], m[5]); B3._g(v, 3, 7, 11, 15, m[6], m[7])
        tr['S' if r == 0 else 'Y'] = list(v)
        B3._g(v, 0, 5, 10, 15, m[8], m[9]); B3._g(v, 1, 6, 11, 12, m[10], m[11])
        B3._g(v, 2, 7, 8, 13, m[12], m[13]); B3._g(v, 3, 4, 9, 14, m[14], m[15])
        tr['X' if r == 0 else 'Z'] = list(v)
        m = [m[i] for i in B3.PERMUTATION]
    out = tuple(v[i] ^ v[i + 8] for i in range(8)) + tuple(v[i + 8] ^ B3.IV[i] for i in range(8))
    assert out == B3._compress(B3.IV, words, counter, block_len, flags, ROUNDS)
    tr['dig'] = list(out[:8])
    return tr

def messages(real):
    r = dict(zip(FRAME_R, real))
    wa = [r.get('w%d' % i, 0) for i in range(16)]; wa[4], wa[13], wa[14], wa[15] = hs.W4, hs.W13, 0, 0
    wb = list(wa); wb[4], wb[5] = hs.W4B, (wa[5] + hs.DELTA5) & M
    return wa, wb, r['T0'] | (r['T1'] << 32)

OBS_FIELDS = (['r%d' % i for i in range(14)] + ['Y3', 'Y4', 'Y9', 'Y14', 'w8', 'Y3B', 'Y11', 'Y11B', 'dY7', 'dY15',
              'X3', 'X7', 'X11', 'X15', 'r0diff', 'T0', 'T1', 'cls', 'eta'] + ['dd%d' % i for i in range(8)] +
              ['Y1', 'Y6', 'Y11e', 'Y12', 'w12', 'w5', 'K', 'c1'] + ['k1_%d' % i for i in range(4)] +
              ['k3_%d' % i for i in range(4)] + ['res%d' % i for i in range(4)])

def ref_obs(real):
    wa, wb, t = messages(real)
    A = compress_trace(wa, t, LEN_A, FLAGS); B = compress_trace(wb, t, LEN_B, FLAGS)
    ya, yb, za, zb = A['Y'], B['Y'], A['Z'], B['Z']
    e3a, e3b = (ya[3] + ya[4] + wa[15]) & M, (yb[3] + yb[4] + wb[15]) & M
    r0 = 0
    for i in range(16): r0 |= A['X'][i] ^ B['X'][i]
    dd = [A['dig'][i] ^ B['dig'][i] for i in range(8)]
    k1 = [za[1] ^ zb[1], za[11] ^ zb[11], za[12] ^ zb[12], za[6] ^ zb[6]]       # (a2, c2, d2, b2) of E1
    k3 = [za[9] ^ zb[9], za[3] ^ zb[3], za[4] ^ zb[4], za[14] ^ zb[14]]         # (g2, e2, f2, h2) of E3
    res = [dd[1], dd[3], dd[4], dd[6]]
    assert res == [a ^ b for a, b in zip(k1, k3)], 'D5 split identity failed'
    c1 = (ya[11] + ror(ya[12] ^ ((ya[1] + ya[6] + wa[12]) & M), 16)) & M
    o = list(real) + [ya[3], ya[4], ya[9], ya[14], wa[8], yb[3], ya[11], yb[11], ya[7] ^ yb[7], ya[15] ^ yb[15],
                      A['X'][3], A['X'][7], A['X'][11], A['X'][15], r0, t & M, t >> 32,
                      int(e3a & hs.CLASS_MASK == hs.CLASS_VALUE), int(ror(e3a ^ e3b, 16) == hs.ETA)] + dd + \
        [ya[1], ya[6], ya[11], ya[12], wa[12], wa[5], (ya[1] + wa[12]) & M, c1] + k1 + k3 + res
    return dict(zip(OBS_FIELDS, o))

# ---------------- damage / steering ----------------
DAMAGE_BITS = ['Y3', 'Y4', 'Y9', 'Y14', 'w8', 'Y3B', 'X3', 'X7', 'X11', 'X15', 'Y11', 'Y11B', 'dY7', 'dY15',
               'T1RANGE', 'CLASS', 'ETA', 'DIG0257', 'K3', 'R0EQ']
INFO_BITS = ['T1', 'T0', 'CTR0', 'SAME_POINT']
def t1_ok(t1): return 1 <= t1 < (1 << 19)
def damage_of(base, now):
    d = 0
    for k, name in enumerate(DAMAGE_BITS):
        if name in ('Y3', 'Y4', 'Y9', 'Y14', 'w8', 'Y3B', 'X3', 'X7', 'X11', 'X15', 'Y11', 'Y11B'):
            bad = now[name] != base[name]
        elif name in ('dY7', 'dY15'): bad = now[name] != 0
        elif name == 'T1RANGE': bad = t1_ok(base['T1']) and not t1_ok(now['T1'])
        elif name == 'CLASS': bad = now['cls'] != 1
        elif name == 'ETA': bad = now['eta'] != 1
        elif name == 'DIG0257': bad = any(now['dd%d' % i] for i in (0, 2, 5, 7))
        elif name == 'K3': bad = any(now['k3_%d' % i] != base['k3_%d' % i] for i in range(4))
        elif name == 'R0EQ': bad = now['r0diff'] != 0
        d |= int(bad) << k
    info = int(now['T1'] != base['T1']) | int(now['T0'] != base['T0']) << 1 | int(now['T0'] == 0 and now['T1'] == 0) << 2
    info |= int(all(now['r%d' % i] == base['r%d' % i] for i in range(14))) << 3
    return d, info

STEER = ['Y1', 'Y6', 'Y11e', 'Y12', 'w12', 'w5', 'K', 'c1']
def steering_of(base, now):
    s = {k: now[k] ^ base[k] for k in STEER}
    s['dK1'] = [now['k1_%d' % i] ^ base['k1_%d' % i] for i in range(4)]
    s['hwK1'] = sum(bin(x).count('1') for x in s['dK1'])
    return s

def ref_apply(cfg, frame, mask):
    '''cfg: dict with 'D','O','R' coordinate lists and 'obs' (base observables). mask: XOR words in frame order.'''
    c = [a ^ b for a, b in zip(cfg[frame], mask)]
    v, chk = ref_derive(frame, c)
    now = ref_obs(real_of(v))
    dmg, info = damage_of(cfg['obs'], now)
    return dmg, info, chk, now
