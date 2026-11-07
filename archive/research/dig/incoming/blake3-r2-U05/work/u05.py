#!/usr/bin/env python3
"""blake3-r2-U05: relax the zero difference of E2 (scan once). Pure python, 1 process, bounded.
Own code written from the printed definitions (verifier/blake3.py is read as the spec only for
validation; it is imported as data via importlib to cross-check our compress)."""

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

import random, sys, json, time, importlib.util, struct

M = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
CALLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
         (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]
NAMES = ['K0', 'K1', 'K2', 'K3', 'D0', 'D1', 'D2', 'D3', 'C0', 'C1', 'C2', 'C3', 'E0', 'E1', 'E2', 'E3']


def ror(x, n): return ((x >> n) | (x << (32 - n))) & M
def rol(x, n): return ((x << n) | (x >> (32 - n))) & M


def g_q(a, b, c, d, x, y):
    """returns the 4 quarter-step outputs and final (a,b,c,d)"""
    a1 = (a + b + x) & M; d1 = ror(d ^ a1, 16)
    c1 = (c + d1) & M; b1 = ror(b ^ c1, 12)
    a2 = (a1 + b1 + y) & M; d2 = ror(d1 ^ a2, 8)
    c2 = (c1 + d2) & M; b2 = ror(b1 ^ c2, 7)
    return (a1, d1), (c1, b1), (a2, d2), (c2, b2), (a2, b2, c2, d2)


def g_inv(a2, b2, c2, d2, x, y):
    b1 = rol(b2, 7) ^ c2
    c1 = (c2 - d2) & M
    d1 = rol(d2, 8) ^ a2
    a1 = (a2 - b1 - y) & M
    c = (c1 - d1) & M
    b = rol(b1, 12) ^ c1
    d = rol(d1, 16) ^ a1
    a = (a1 - b - x) & M
    return a, b, c, d


def init_state(cv, ctr, blen, flags):
    return list(cv) + list(IV[:4]) + [ctr & M, ctr >> 32, blen, flags]


def compress(S, m, rounds=2, trace=None):
    """S: 16 state words; m: 16 msg words. returns v after rounds and the digest (8 words)."""
    v = list(S); mm = list(m)
    for r in range(rounds):
        for ci, (a, b, c, d) in enumerate(CALLS):
            q1, q2, q3, q4, out = g_q(v[a], v[b], v[c], v[d], mm[2 * ci], mm[2 * ci + 1])
            if trace is not None:
                trace[(r * 8 + ci)] = (q1, q2, q3, q4, (v[a], v[b], v[c], v[d]))
            v[a], v[b], v[c], v[d] = out
        mm = [mm[i] for i in PERM]
    return v


def digest(v): return tuple(v[i] ^ v[i + 8] for i in range(8))


def S_legal(blen, ctr=0, flags=11):
    return init_state(IV, ctr, blen, flags)


def load_verifier():
    p = _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/blake3.py')
    spec = importlib.util.spec_from_file_location('b3ver', p)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


R = random.Random(20261012)
LOG = []
def log(*a):
    s = ' '.join(str(x) for x in a); print(s); LOG.append(s); sys.stdout.flush()

t0 = time.time()
# ---------------------------------------------------------------- V1 validate compress vs verifier
ver = load_verifier()
ok = 0
for _ in range(2000):
    L = R.choice([1, 17, 55, 63, 64])
    data = bytes(R.getrandbits(8) for _ in range(L))
    h_ver = ver.blake3(data, 2)
    words = list(struct.unpack('<16I', data.ljust(64, b'\0')))
    v = compress(S_legal(L, 0, 1 | 2 | 8), words, 2)
    h_ours = struct.pack('<8I', *digest(v))
    ok += (h_ver == h_ours)
log('V1 compress vs verifier (rounds=2, single block root): %d/2000 equal' % ok)
assert ok == 2000

# ---------------------------------------------------------------- V2 G inverse round trip
ok = 0
for _ in range(100000):
    a, b, c, d, x, y = [R.getrandbits(32) for _ in range(6)]
    o = g_q(a, b, c, d, x, y)[4]
    ok += (g_inv(*o, x, y) == (a, b, c, d))
log('V2 G inverse round trip: %d/100000' % ok)
assert ok == 100000

# ---------------------------------------------------------------- V3 Fact P known answer (pkgCK proof constants)
X3, X7, X11, X15 = 0x29d4fa98, 0xbee3af28, 0x44036000, 0x40c58500
W4, W4p, W13 = 0x97475638, 0x97475640, 0x0007c006
oA = g_q(X3, X7, X11, X15, W4, W13)[4]; oB = g_q(X3, X7, X11, X15, W4p, W13)[4]
log('V3 Fact P: C3 out A (a,b,c,d)=%s' % ' '.join('%08x' % z for z in oA))
log('V3 Fact P: C3 out B (a,b,c,d)=%s' % ' '.join('%08x' % z for z in oB))
assert oA[1] == oB[1] and oA[3] == oB[3] and oA[0] != oB[0] and oA[2] != oB[2]
assert (oA[0], oA[2], oB[0], oB[2]) == (0x8127c181, 0x7af77f38, 0x7edf3e7e, 0x850000c3) or \
       (oA[0], oA[2]) in ((0x8127c181, 0x7af77f38), (0x7edf3e7e, 0x850000c3))
log('V3 matches documented Y3 8127c181/7edf3e7e, Y11 7af77f38/850000c3, b,d equal (76f7aefd, bbfbdffe): %s' %
    (oA[1] == 0x76f7aefd and oA[3] == 0xbbfbdffe))

# ---------------------------------------------------------------- V4 Lemma L (K2 absorption of the length difference 55^63)
K = (IV[2] + IV[6]) & M
def lemma_L_pair():
    m = [R.getrandbits(32) for _ in range(16)]
    m[13] &= 0x00FFFFFF; m[14] = 0; m[15] = 0
    mA = list(m); mB = list(m)
    w4 = m[4]; w5 = m[5]
    w4p = ((((K + w4) & M) ^ 8) - K) & M
    w5p = (w5 + w4 - w4p) & M
    mB[4] = w4p; mB[5] = w5p
    return mA, mB
ok = 0
for _ in range(2000):
    mA, mB = lemma_L_pair()
    vA = compress(S_legal(55), mA, 1); vB = compress(S_legal(63), mB, 1)
    ok += (vA == vB)
log('V4 Lemma L (round 0 identical for 55 vs 63 with w4,w5 recipe): %d/2000' % ok)
assert ok == 2000

log('validation time %.1fs' % (time.time() - t0))

# ---------------------------------------------------------------- B: round-1 level baseline (pins)
def round1(X, m1):
    """round 1 from state X with round-1 message order m1 (m1 = permuted message). returns v and trace."""
    tr = {}
    v = list(X)
    for ci, (a, b, c, d) in enumerate(CALLS):
        q1, q2, q3, q4, out = g_q(v[a], v[b], v[c], v[d], m1[2 * ci], m1[2 * ci + 1])
        tr[ci] = (q1, q2, q3, q4, (v[a], v[b], v[c], v[d]))
        v[a], v[b], v[c], v[d] = out
    return v, tr

def baseline_pair():
    """round-1 level pair: X equal with pinned X3,X7,X11,X15; w4=W4 / W4', w13=W13, w5 recipe; rest random."""
    X = [R.getrandbits(32) for _ in range(16)]
    X[3], X[7], X[11], X[15] = X3, X7, X11, X15
    m = [R.getrandbits(32) for _ in range(16)]
    m[4] = W4; m[13] = W13; m[14] = 0; m[15] = 0
    mA = list(m); mB = list(m)
    mB[4] = W4p; mB[5] = (m[5] + W4 - W4p) & M
    return X, mA, mB

def perm_msg(m): return [m[i] for i in PERM]

N1 = 20000
ok_dig = 0; zero_e0 = 0; zero_e2 = 0; other_zero = {n: 0 for n in NAMES[8:]}
for _ in range(N1):
    X, mA, mB = baseline_pair()
    vA, tA = round1(X, perm_msg(mA)); vB, tB = round1(X, perm_msg(mB))
    dA = digest(vA); dB = digest(vB)
    eq = [dA[i] == dB[i] for i in range(8)]
    ok_dig += (eq == [True, False, True, False, False, True, False, True])
    for ci in range(8):
        same = all(tA[ci][k] == tB[ci][k] for k in range(4))
        other_zero[NAMES[8 + ci]] += same
log('B1 baseline (pins) %d trials: digest equal exactly on words {0,2,5,7}: %d ; calls with zero difference in all four quarter-steps: %s' %
    (N1, ok_dig, other_zero))
assert ok_dig == N1

# ---------------------------------------------------------------- Q2: relax each quarter-step of E2 (E0 stays zero)
# quarter-step input words (a,b,c,d are the E2 input words; intermediates are after earlier quarters)
# q1: (a,b,d,mx) -> (a1,d1); q2: (c,d1,b) -> (c1,b1); q3: (a1,b1,d1,my) -> (a2,d2); q4: (c1,d2,b1) -> (c2,b2)
def e2_with_injection(inp, mx, my, qk, dlt):
    """run E2 where we inject XOR/ADD differences at the inputs of quarter-step qk (dlt: dict name->(kind,val))."""
    a, b, c, d = inp
    def ap(name, val):
        if name in dlt:
            kind, dv = dlt[name]
            return (val ^ dv) & M if kind == 'x' else (val + dv) & M
        return val
    # quarter 1
    if qk == 1:
        a, b, d = ap('a', a), ap('b', b), ap('d', d)
        mx = ap('mx', mx)
    a1 = (a + b + mx) & M; d1 = ror(d ^ a1, 16)
    if qk == 2:
        c = ap('c', c); d1 = ap('d1', d1); b = ap('b', b)
    c1 = (c + d1) & M; b1 = ror(b ^ c1, 12)
    if qk == 3:
        a1 = ap('a1', a1); b1 = ap('b1', b1); d1 = ap('d1', d1); my = ap('my', my)
    a2 = (a1 + b1 + my) & M; d2 = ror(d1 ^ a2, 8)
    if qk == 4:
        c1 = ap('c1', c1); d2 = ap('d2', d2); b1 = ap('b1', b1)
    c2 = (c1 + d2) & M; b2 = ror(b1 ^ c2, 7)
    return a2, b2, c2, d2

QIN = {1: ['a', 'b', 'd', 'mx'], 2: ['c', 'd1', 'b'], 3: ['a1', 'b1', 'd1', 'my'], 4: ['c1', 'd2', 'b1']}
NQ = 150000
q2res = {}
for qk in (1, 2, 3, 4):
  for allow_msg in (False, True):
    names = [n for n in QIN[qk] if allow_msg or n not in ('mx', 'my')]
    if allow_msg and len(names) == len(QIN[qk]) - 0 and not any(n in ('mx', 'my') for n in QIN[qk]):
        continue
    trials = 0; outeq = 0
    for t in range(NQ):
        X, mA, mB = baseline_pair()
        m1 = perm_msg(mA)
        _, tr = round1(X, m1)
        inp = tr[6][4]
        mx, my = m1[12], m1[13]
        base = e2_with_injection(inp, mx, my, qk, {})
        mode = t % 4
        dl = {}
        if mode == 0:
            nm = R.choice(names); dl[nm] = ('x', R.getrandbits(32) or 1)
        elif mode == 1:
            nm = R.choice(names); dl[nm] = ('a', R.getrandbits(32) or 1)
        elif mode == 2 and len(names) >= 2:
            x = R.getrandbits(32) or 1
            n1, n2 = R.sample(names, 2); dl[n1] = ('a', x); dl[n2] = ('a', (-x) & M)
        else:
            for nm in names:
                if R.random() < 0.6: dl[nm] = ('x', R.getrandbits(32))
            if not dl or all(v[1] == 0 for v in dl.values()): dl[names[0]] = ('x', 1)
        out = e2_with_injection(inp, mx, my, qk, dl)
        trials += 1
        outeq += (out == base)
    q2res[(qk, allow_msg)] = (trials, outeq)
    log('Q2 E2.q%d %s: nonzero difference injected at quarter-step inputs (%s): %d trials, event (all E2 outputs equal, so digest words 0,2,5,7 equal) held in %d' %
        (qk, 'WITH message word allowed' if allow_msg else 'state words only (messages equal)', ','.join(names), trials, outeq))
log('Q2 time %.1fs' % (time.time() - t0))

# Exhaustive proof-by-computation at a small width: G with word width w is a bijection on (a,b,c,d) for fixed m,
# so zero output difference with equal messages forces zero input difference. Check at w=4..6 (rotations mod w).
def g_w(a, b, c, d, x, y, w, rots=(16, 12, 8, 7)):
    mk = (1 << w) - 1
    def r(v, n):
        n %= w
        return ((v >> n) | (v << (w - n))) & mk if n else v
    a1 = (a + b + x) & mk; d1 = r(d ^ a1, rots[0])
    c1 = (c + d1) & mk; b1 = r(b ^ c1, rots[1])
    a2 = (a1 + b1 + y) & mk; d2 = r(d1 ^ a2, rots[2])
    c2 = (c1 + d2) & mk; b2 = r(b1 ^ c2, rots[3])
    return a2, b2, c2, d2
for w in (3, 4):
    seen = set(); n = 1 << w
    mx, my = R.getrandbits(w), R.getrandbits(w)
    for a in range(n):
        for b in range(n):
            for c in range(n):
                for d in range(n):
                    seen.add(g_w(a, b, c, d, mx, my, w))
    log('Q2 toy width %d: G is a bijection on %d states: %s' % (w, n ** 4, len(seen) == n ** 4))

# ---------------------------------------------------------------- Q4a: alternatives exist only crossed with E0 ; positive control
def cross_event_pair():
    """construct inputs for E0 and E2 so that digest words 0,2,5,7 are equal while E2 inputs differ, by inversion."""
    mx0, my0, mx2, my2 = [R.getrandbits(32) for _ in range(4)]   # equal messages for A and B (zero message diff)
    # E2 outputs pair
    zA = [R.getrandbits(32) for _ in range(4)]          # (a2,b2,c2,d2) for A
    zB = [R.getrandbits(32) for _ in range(4)]
    # E0 outputs pair: want  E2.a ^ E0.c equal across A,B ; E2.b ^ E0.d ; E2.c ^ E0.a ; E2.d ^ E0.b
    wA = [R.getrandbits(32) for _ in range(4)]
    wB = [0] * 4
    # E0 out order (a,b,c,d); cross: E0.c <-> E2.a, E0.d <-> E2.b, E0.a <-> E2.c, E0.b <-> E2.d
    wB[2] = wA[2] ^ zA[0] ^ zB[0]
    wB[3] = wA[3] ^ zA[1] ^ zB[1]
    wB[0] = wA[0] ^ zA[2] ^ zB[2]
    wB[1] = wA[1] ^ zA[3] ^ zB[3]
    e2A = g_inv(*zA, mx2, my2); e2B = g_inv(*zB, mx2, my2)
    e0A = g_inv(*wA, mx0, my0); e0B = g_inv(*wB, mx0, my0)
    return (e0A, e2A, e0B, e2B, (mx0, my0, mx2, my2))
okc = 0; ndiff = 0
for _ in range(20000):
    e0A, e2A, e0B, e2B, (mx0, my0, mx2, my2) = cross_event_pair()
    oA0 = g_q(*e0A, mx0, my0)[4]; oA2 = g_q(*e2A, mx2, my2)[4]
    oB0 = g_q(*e0B, mx0, my0)[4]; oB2 = g_q(*e2B, mx2, my2)[4]
    # digest words: o0=Z0^Z8 (E0.a ^ E2.c), o2=Z2^Z10 (E2.a ^ E0.c), o5=Z5^Z13 (E0.b ^ E2.d), o7=Z7^Z15 (E2.b ^ E0.d)
    dA = (oA0[0] ^ oA2[2], oA2[0] ^ oA0[2], oA0[1] ^ oA2[3], oA2[1] ^ oA0[3])
    dB = (oB0[0] ^ oB2[2], oB2[0] ^ oB0[2], oB0[1] ^ oB2[3], oB2[1] ^ oB0[3])
    okc += (dA == dB)
    ndiff += (e2A != e2B and e0A != e0B)
log('Q4a positive control by inversion: digest words 0,2,5,7 equal in %d/20000 with E2 inputs AND E0 inputs both different in %d' % (okc, ndiff))
assert okc == 20000 and ndiff == 20000

# Q4b: with E0 left at zero difference, crossed alternatives are impossible; with random (uncoupled) E0/E2 difference the event rate
# is 2^-128 per pair: measure the per-bit agreement (no bias) on 2^20 random difference pairs
agree = [0] * 4; NB = 100000
for _ in range(NB):
    e2A = tuple(R.getrandbits(32) for _ in range(4)); e2B = tuple(R.getrandbits(32) for _ in range(4))
    e0A = tuple(R.getrandbits(32) for _ in range(4)); e0B = tuple(R.getrandbits(32) for _ in range(4))
    mm = [R.getrandbits(32) for _ in range(4)]
    oA0 = g_q(*e0A, mm[0], mm[1])[4]; oA2 = g_q(*e2A, mm[2], mm[3])[4]
    oB0 = g_q(*e0B, mm[0], mm[1])[4]; oB2 = g_q(*e2B, mm[2], mm[3])[4]
    dA = (oA0[0] ^ oA2[2], oA2[0] ^ oA0[2], oA0[1] ^ oA2[3], oA2[1] ^ oA0[3])
    dB = (oB0[0] ^ oB2[2], oB2[0] ^ oB0[2], oB0[1] ^ oB2[3], oB2[1] ^ oB0[3])
    for i in range(4):
        agree[i] += 32 - bin(dA[i] ^ dB[i]).count('1')
log('Q4b random E0/E2 pairs: mean agreeing bits per digest word %s of 32 (expect 16.0; no bias => generic cost 4x32 = 128 bits)' %
    [round(x / NB, 3) for x in agree])

# ---------------------------------------------------------------- Q4c: in-call absorption at E2 (door 22 test): which input-difference supports can message differences absorb
def support_pattern(trials=200000):
    pats = {}
    for _ in range(trials):
        z = [R.getrandbits(32) for _ in range(4)]
        mx, my = R.getrandbits(32), R.getrandbits(32)
        dx, dy = R.getrandbits(32), R.getrandbits(32)
        kind = R.randrange(5)
        if kind == 0: dxx, dyy = dx, 0
        elif kind == 1: dxx, dyy = 0, dy
        elif kind == 2: dxx, dyy = dx, (-dx) & M
        elif kind == 3: dxx, dyy = dx, dy
        else: dxx, dyy = 0, 0
        i1 = g_inv(*z, mx, my); i2 = g_inv(*z, (mx + dxx) & M, (my + dyy) & M)
        sup = ''.join(n for n, p, q in zip('abcd', i1, i2) if p != q)
        key = (('mx' if dxx else '') + ('my' if dyy else ''), sup)
        pats[key] = pats.get(key, 0) + 1
    return pats
pats = support_pattern()
log('Q4c outputs equal, messages differ (msg-diff set -> input-diff support), counts of 200000:')
for k in sorted(pats): log('   ', k, pats[k])

# clean-state absorption (inputs equal, messages differ): zero solutions
bad = 0
for _ in range(500000):
    a, b, c, d, x, y = [R.getrandbits(32) for _ in range(6)]
    dx, dy = R.getrandbits(32), R.getrandbits(32)
    if dx == 0 and dy == 0: continue
    bad += (g_q(a, b, c, d, x, y)[4] == g_q(a, b, c, d, (x + dx) & M, (y + dy) & M)[4])
log('Q4c clean state (equal inputs), message differences nonzero: equal outputs in %d / 500000' % bad)
# structured: dy=-dx and dx chosen to cancel
bad = 0
for _ in range(500000):
    a, b, c, d, x, y = [R.getrandbits(32) for _ in range(6)]
    dx = R.getrandbits(32) or 1
    bad += (g_q(a, b, c, d, x, y)[4] == g_q(a, b, c, d, (x + dx) & M, (y - dx) & M)[4])
log('Q4c clean state, structured (dx,-dx): equal outputs in %d / 500000' % bad)

# ---------------------------------------------------------------- Q4d: legal source activity (what else can carry a difference to E2)
# pair: Lemma-L baseline, then extra legal message difference at word j; unpinned, plus pin emulation (Y7,Y15 of B := A after C3)
def quarter_active(tA, tB, ci):
    return [tA[ci][k] != tB[ci][k] for k in range(4)]

def run_pair(mA, mB, pinemu):
    tA, tB = {}, {}
    vA = list(S_legal(55)); vB = list(S_legal(63))
    mmA, mmB = list(mA), list(mB)
    for r in range(2):
        for ci, (a, b, c, d) in enumerate(CALLS):
            for (v, mm, tr) in ((vA, mmA, tA), (vB, mmB, tB)):
                q1, q2, q3, q4, out = g_q(v[a], v[b], v[c], v[d], mm[2 * ci], mm[2 * ci + 1])
                tr[r * 8 + ci] = (q1, q2, q3, q4, (v[a], v[b], v[c], v[d]))
                v[a], v[b], v[c], v[d] = out
            if pinemu and r == 1 and ci == 3:
                vB[7] = vA[7]; vB[15] = vA[15]
        mmA = [mmA[i] for i in PERM]; mmB = [mmB[i] for i in PERM]
    return vA, vB, tA, tB

MASKS = {j: M for j in range(16)}
MASKS[15] = 0x00FFFFFF
NA = 600
act_summary = {}
for j in [None] + list(range(16)):
    cnt = {n: 0 for n in NAMES}
    e2q = [0, 0, 0, 0]; e0q = [0, 0, 0, 0]
    dig_eq = {i: 0 for i in range(8)}
    for _ in range(NA):
        mA, mB = lemma_L_pair()
        if j is not None:
            mB[j] = (mB[j] ^ ((R.getrandbits(32) & MASKS[j]) or 1)) & M
            if j == 15: mB[15] &= 0x00FFFFFF
        vA, vB, tA, tB = run_pair(mA, mB, True)
        for ci in range(16):
            if any(tA[ci][k] != tB[ci][k] for k in range(4)): cnt[NAMES[ci]] += 1
        for k in range(4):
            e2q[k] += (tA[14][k] != tB[14][k]); e0q[k] += (tA[12][k] != tB[12][k])
        dA, dB = digest(vA), digest(vB)
        for i in range(8): dig_eq[i] += (dA[i] == dB[i])
    act_summary[j] = (cnt, e0q, e2q, dig_eq)
    act = [n for n in NAMES if cnt[n] > 0.5 * NA]
    log('Q4d source %s: active calls (>50%% trials): %s ; E0 q-active %s ; E2 q-active %s ; digest words equal (of %d trials) %s' %
        ('baseline' if j is None else 'dm%d' % j, ','.join(act), e0q, e2q, NA, [dig_eq[i] for i in range(8)]))
log('Q4d time %.1fs' % (time.time() - t0))

# unpinned baseline (without pin emulation): which of E0/E2 are active
cnt = {n: 0 for n in NAMES}; NAU = 600
for _ in range(NAU):
    mA, mB = lemma_L_pair()
    vA, vB, tA, tB = run_pair(mA, mB, False)
    for ci in range(16):
        if any(tA[ci][k] != tB[ci][k] for k in range(4)): cnt[NAMES[ci]] += 1
log('Q4d unpinned Lemma-L baseline active-call counts of %d: %s' % (NAU, {n: c for n, c in cnt.items() if c}))
log('TOTAL time %.1fs' % (time.time() - t0))
json.dump({'log': LOG}, open(_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming/blake3-r2-U05/work/u05_out.json'), 'w'), indent=1)
