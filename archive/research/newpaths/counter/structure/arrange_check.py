"""Part 2c: the arrangement on real 32-bit arithmetic (own code, written from proof.md section 4 with the
counter changes: flags 3, K1's d input v13 = T_HI (0), K0's d input v12 = t per trial).

Outer step: the eight words C0.c1, C0.d1, D3.d1, S15, S9, w5, X2 and Y4 (Y4 a member of the sub-class of
Lemma Q2) are drawn and steps O, M (without K0.a1/w0/w1), Y, T and C1, C2's first half are run once.
Trial: c1 drawn inside the T1 cube (c1 & 0e09818b) == 02008000, E1.d1 = c1 - Y11; then
  E1.a1 = ROL(d1,16) ^ Y12; Y6 = E1.a1 - Y1 - w12; Y10 = ROL(Y6,7) ^ C2.b1; Y14 = Y10 - C2.c1;
  Y2 = ROL(Y14,8) ^ C2.d1; w0 = Y2 - C2.a1 - C2.b1; K0.a1 = IV0 + IV4 + w0;
  t = ROL(K0.d1,16) ^ K0.a1 (the chunk counter, v12; v13 = 0); w1 = S0 - K0.a1 - K0.b1.
Checks per trial, on the ORGANIZER's verifier/blake3.py internals (_chunk_output, _compress, 2 rounds) and on
an own forward trace (b3own.py): see the printed list.  Part 3 scans the whole cube of a few outer steps with
numpy for small t and hashes the COMPLETE messages P||A, P||B (P = t identical chunks) with the organizer's
blake3().
usage: python -B arrange_check.py OUTER TRIALS_PER_OUTER SCAN_OUTERS SEED
"""

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

import sys, struct, random, time
import numpy as np
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
import blake3 as V
import b3own as O

M = 0xFFFFFFFF
IV = O.IV
ror, rol = O.ror, O.rol
X3, X7, X11, X15 = 0x29D4FA98, 0xBEE3AF28, 0x44036000, 0x40C58500
W4, W13 = 0x97475638, 0x0007C006
KK = (IV[2] + IV[6]) & M
W4B = ((((KK + W4) & M) ^ 8) - KK) & M
DELTA = (W4 - W4B) & M
import os
FLAGS, T_HI = 3, int(os.environ.get('THI', '0'))      # THI: v13 (high counter word), a per-run constant
Y3A, _, Y11A, _ = O.G(X3, X7, X11, X15, W4, W13)
Y3B, _, Y11B, _ = O.G(X3, X7, X11, X15, W4B, W13)
CUBE_MASK, CUBE_VAL = 0x0E09818B, 0x02008000
SUB_MASK, SUB_VAL = 0x07EF8303, 0x030C0303          # Lemma Q2 on e1 = Y3 + Y4
BETA_T1, ETA = 0x18B0E098, 0x830303CF


def sub_member(rng):
    free = [i for i in range(32) if not SUB_MASK >> i & 1]
    e1 = SUB_VAL
    for i in free:
        e1 |= rng.getrandbits(1) << i
    return (e1 - Y3A) & M


def outer(vc, vd, d3d1, S15, S9, w5, X2, y):
    v = dict(vc=vc, vd=vd, y=y, X2=X2, S15=S15, S9=S9, w5=w5)
    # step O
    K2a1 = (IV[2] + IV[6] + W4) & M; K2d1 = ror(55 ^ K2a1, 16); K2c1 = (IV[2] + K2d1) & M
    K2b1 = ror(IV[6] ^ K2c1, 12)
    S2 = (K2a1 + K2b1 + w5) & M; S14 = ror(K2d1 ^ S2, 8); S10 = (K2c1 + S14) & M; S6 = ror(K2b1 ^ S10, 7)
    D3a1 = rol(d3d1, 16) ^ S14; D3c1 = (S9 + d3d1) & M; D3b1 = (X3 - D3a1) & M
    S4 = rol(D3b1, 12) ^ D3c1; S3 = (D3a1 - S4) & M; X14 = ror(d3d1 ^ X3, 8); X9 = (D3c1 + X14) & M
    X4 = ror(D3b1 ^ X9, 7)
    K3d1 = rol(S15, 8) ^ S3; K3c1 = (IV[3] + K3d1) & M; K3b1 = ror(IV[7] ^ K3c1, 12)
    S11 = (K3c1 + S15) & M; S7 = ror(K3b1 ^ S11, 7); K3a1 = rol(K3d1, 16) ^ FLAGS
    w6 = (K3a1 - IV[3] - IV[7]) & M; w7 = (S3 - K3a1 - K3b1) & M
    X8 = (vc - vd) & M; C0b1 = ror(X4 ^ vc, 12)
    D2b1 = rol(X7, 7) ^ X8; D2c1 = rol(D2b1, 12) ^ S7; X13 = (X8 - D2c1) & M
    # step M
    D2a1 = (X2 - D2b1 - W13) & M; D2d1 = rol(X13, 8) ^ X2; S13 = rol(D2d1, 16) ^ D2a1
    S8 = (D2c1 - D2d1) & M; w12 = (D2a1 - S2 - S7) & M
    K1c1 = (S9 - S13) & M; K1d1 = (K1c1 - IV[1]) & M; K1a1 = rol(K1d1, 16) ^ T_HI
    K1b1 = ror(IV[5] ^ K1c1, 12); S1 = rol(S13, 8) ^ K1d1; S5 = ror(K1b1 ^ S9, 7)
    w2 = (K1a1 - IV[1] - IV[5]) & M; w3 = (S1 - K1a1 - K1b1) & M
    K0b1 = rol(S4, 7) ^ S8; K0c1 = rol(K0b1, 12) ^ IV[4]; K0d1 = (K0c1 - IV[0]) & M
    S12 = (S8 - K0c1) & M; S0 = rol(S12, 8) ^ K0d1
    # step Y
    Y8 = rol(y, 7) ^ C0b1; Y12 = (Y8 - vc) & M; Y0 = rol(Y12, 8) ^ vd; C0a1 = (Y0 - C0b1 - w6) & M
    X12 = rol(vd, 16) ^ C0a1
    D1c1 = (X11 - X12) & M; D1b1 = ror(S6 ^ D1c1, 12); X6 = ror(D1b1 ^ X11, 7); D1d1 = (D1c1 - S11) & M
    X1 = rol(X12, 8) ^ D1d1
    # step T
    X0 = (C0a1 - X4 - w2) & M
    D0d1 = rol(X15, 8) ^ X0; D0c1 = (S10 + D0d1) & M; X10 = (D0c1 + X15) & M; D0b1 = ror(S5 ^ D0c1, 12)
    X5 = ror(D0b1 ^ X10, 7); D0a1 = rol(D0d1, 16) ^ S15; w8 = (D0a1 - S0 - S5) & M
    w9 = (X0 - D0a1 - D0b1) & M
    D1a1 = rol(D1d1, 16) ^ S12; w10 = (D1a1 - S1 - S6) & M; w11 = (X1 - D1a1 - D1b1) & M
    # round 1: C1 forward, C2 first half
    Y1, Y5, Y9, Y13 = O.G(X1, X5, X9, X13, w3, w10)
    C2a1 = (X2 + X6 + w7) & M; C2d1 = ror(X14 ^ C2a1, 16); C2c1 = (X10 + C2d1) & M
    C2b1 = ror(X6 ^ C2c1, 12)
    loc = dict(locals())
    for k, val in loc.items():
        if k not in v and isinstance(val, int):
            v[k] = val
    return v


def inner(o, d1):
    a1 = rol(d1, 16) ^ o['Y12']
    Y6 = (a1 - o['Y1'] - o['w12']) & M
    Y10 = rol(Y6, 7) ^ o['C2b1']
    Y14 = (Y10 - o['C2c1']) & M
    Y2 = rol(Y14, 8) ^ o['C2d1']
    w0 = (Y2 - o['C2a1'] - o['C2b1']) & M
    K0a1 = (IV[0] + IV[4] + w0) & M
    t = rol(o['K0d1'], 16) ^ K0a1
    w1 = (o['S0'] - K0a1 - o['K0b1']) & M
    words = [w0, w1, o['w2'], o['w3'], W4, o['w5'], o['w6'], o['w7'], o['w8'], o['w9'], o['w10'],
             o['w11'], o['w12'], W13, 0, 0]
    return dict(E1a1=a1, Y6=Y6, Y10=Y10, Y14=Y14, Y2=Y2, w0=w0, K0a1=K0a1, t=t, w1=w1), words


def expected_trace(o, ii):
    """Construction values to compare with the forward trace: (call, field) -> value."""
    e = {}
    for c in ('K0', 'K1', 'K3', 'D0', 'D1', 'D2', 'D3'):
        for f in ('a1', 'd1', 'c1', 'b1'):
            key = c + f
            if key in o:
                e[(c, f)] = o[key]
            elif c == 'K0' and f == 'a1':
                e[(c, f)] = ii['K0a1']
    e[('C0', 'c1')] = o['vc']; e[('C0', 'd1')] = o['vd']; e[('C0', 'b1')] = o['C0b1']; e[('C0', 'a1')] = o['C0a1']
    e[('C2', 'a1')] = o['C2a1']; e[('C2', 'd1')] = o['C2d1']; e[('C2', 'c1')] = o['C2c1']; e[('C2', 'b1')] = o['C2b1']
    e[('D3', 'd1')] = o['d3d1']
    st = {}
    for k in range(16):
        for P in 'SXY':
            nm = f'{P}{k}'
            if nm in o:
                st[nm] = o[nm]
    st['X3'], st['X7'], st['X11'], st['X15'] = X3, X7, X11, X15
    st['Y4'] = o['y']; st['Y2'] = ii['Y2']; st['Y6'] = ii['Y6']; st['Y10'] = ii['Y10']; st['Y14'] = ii['Y14']
    st['Y3'], st['Y11'] = Y3A, Y11A
    st['X2'] = o['X2']; st['S9'] = o['S9']; st['S15'] = o['S15']
    return e, st


def main():
    n_outer = int(sys.argv[1]); per = int(sys.argv[2]); n_scan = int(sys.argv[3]); seed = int(sys.argv[4])
    rng = random.Random(seed)
    cnt = dict(trials=0, mism_int=0, mism_state=0, half=0, full_cv_equal=0, len_ok=0, zero_bytes=0, y4=0,
               d1=0, cube=0, beta=0, eta=0, x_equal=0, t_zero=0, desc=0, sub=0, r0_fixed=0, w_fixed=0)
    ts = []
    free_cube = [i for i in range(32) if not CUBE_MASK >> i & 1]
    t0 = time.time()
    outers = []
    for oi in range(n_outer):
        o = outer(*[rng.getrandbits(32) for _ in range(7)], sub_member(rng))
        outers.append(o)
        ref_X = ref_S = ref_w = None
        for _ in range(per):
            c1 = CUBE_VAL
            for i in free_cube:
                c1 |= rng.getrandbits(1) << i
            d1 = (c1 - Y11A) & M
            ii, words = inner(o, d1)
            t = ii['t'] | (T_HI << 32)          # full 64-bit chunk counter
            ts.append(t)
            cnt['trials'] += 1
            cnt['t_zero'] += t == 0
            A = struct.pack('<16I', *words)[:55]
            wb = list(words); wb[4] = W4B; wb[5] = (words[5] + DELTA) & M
            B = struct.pack('<16I', *wb)[:63]
            cnt['len_ok'] += len(A) == 55 and len(B) == 63
            cnt['zero_bytes'] += B[55:63] == bytes(8) and struct.pack('<16I', *wb)[63:] == b'\0'
            # organizer: last-chunk descriptor and CV for counter t
            oa = V._chunk_output(A, t, 2); ob = V._chunk_output(B, t, 2)
            cnt['desc'] += (oa[0] == V.IV and oa[2] == t and oa[3] == 55 and oa[4] == 3 and
                            ob[2] == t and ob[3] == 63 and ob[4] == 3 and list(oa[1]) == words and list(ob[1]) == wb)
            cvA = V._compress(*oa, 2)[:8]; cvB = V._compress(*ob, 2)[:8]
            cnt['half'] += all(cvA[i] == cvB[i] for i in (0, 2, 5, 7))
            cnt['full_cv_equal'] += cvA == cvB
            # own forward traces
            trA, trB = {}, {}
            outA, stA = O.compress_full(IV, words, t, 55, 3, trace=trA)
            outB, stB = O.compress_full(IV, wb, t, 63, 3, trace=trB)
            cnt['mism_state'] += (tuple(outA[:8]) != tuple(cvA)) + (tuple(outB[:8]) != tuple(cvB))
            e, st = expected_trace(o, ii)
            mi = sum(1 for (c, f), val in e.items() if trA[c][f] != val)
            ms = 0
            for nm, val in st.items():
                P, k = nm[0], int(nm[1:])
                ms += ({'S': stA['S'], 'X': stA['X'], 'Y': stA['Y']}[P][k] != val)
            cnt['mism_int'] += mi + ms
            cnt['y4'] += stA['Y'][4] == o['y'] and stB['Y'][4] == o['y']
            cnt['d1'] += trA['E1']['d1'] == d1 and trB['E1']['d1'] == d1
            cnt['cube'] += (trA['E1']['c1'] & CUBE_MASK) == CUBE_VAL
            cnt['beta'] += (trA['E1']['b1'] ^ trB['E1']['b1']) == BETA_T1
            cnt['eta'] += (trA['E3']['d1'] ^ trB['E3']['d1']) == ETA
            cnt['x_equal'] += stA['X'] == stB['X']
            cnt['sub'] += ((Y3A + o['y']) & M & SUB_MASK) == SUB_VAL
            if ref_X is None:
                ref_X, ref_S, ref_w = stA['X'], stA['S'], words
            cnt['r0_fixed'] += stA['X'] == ref_X and stA['S'] == ref_S
            cnt['w_fixed'] += words[2:] == ref_w[2:]
    n = cnt['trials']
    print(f'part 2c: {n_outer} outer steps x {per} trials = {n} trials, seed {seed}, {time.time() - t0:.0f}s')
    for k, txt in (('desc', 'organizer last-chunk descriptor (IV, words, counter t, len 55/63, flags 3)'),
                   ('len_ok', 'lengths 55 and 63'), ('zero_bytes', "B's bytes 55..63 zero (w14 = w15 = 0, top byte w13 = 0)"),
                   ('half', 'CV words 0,2,5,7 equal (organizer _compress, counter t, flags 3)'),
                   ('y4', 'Y4 = prescribed member (both messages)'), ('sub', 'Y4 in the sub-class (Lemma Q2)'),
                   ('d1', 'E1.d1 = prescribed value (both messages)'), ('cube', 'c1 in the T1 cube'),
                   ('beta', 'beta = b1 ^ b1\' = 18b0e098 (forward)'), ('eta', 'eta = h1 ^ h1\' = 830303cf (forward)'),
                   ('x_equal', 'equal round-0 state X for A and B'),
                   ('r0_fixed', 'round-0 states S, X equal to the first trial of the same outer step'),
                   ('w_fixed', 'message words w2..w15 equal to the first trial of the same outer step')):
        print(f'  {txt}: {cnt[k]}/{n}')
    print(f"  internal-word mismatches, construction vs forward trace (about 75 words per trial): {cnt['mism_int']}")
    print(f"  own compress vs organizer CV mismatches: {cnt['mism_state']}")
    print(f"  full CV equal (a full collision; expected 0): {cnt['full_cv_equal']}")
    ta = np.array(ts, dtype=np.float64)
    print(f"  counter t: zero {cnt['t_zero']}, min {int(ta.min())}, max {int(ta.max())}, mean log2 {np.log2(ta).mean():.2f}, "
          f"fraction < 2^20 {np.mean(ta < 2**20):.5f}, < 2^31 {np.mean(ta < 2**31):.3f}; v13 = {T_HI} in all")
    # ---------------- part 3: whole-cube scans and complete messages ----------------
    if n_scan:
        scan(outers[:n_scan], rng)


def np_rol(x, n):
    return ((x << np.uint32(n)) | (x >> np.uint32(32 - n))).astype(np.uint32)


def scan(outers, rng):
    free_cube = [i for i in range(32) if not CUBE_MASK >> i & 1]
    k = np.arange(1 << 21, dtype=np.uint32)
    c1 = np.full(1 << 21, CUBE_VAL, dtype=np.uint32)
    for j, i in enumerate(free_cube):
        c1 |= ((k >> np.uint32(j)) & np.uint32(1)) << np.uint32(i)
    assert np.all((c1 & np.uint32(CUBE_MASK)) == CUBE_VAL) and len(np.unique(c1)) == 1 << 21
    d1 = (c1 - np.uint32(Y11A)).astype(np.uint32)
    found = []
    print(f'part 3: whole T1 cube (2^21 values of c1) per outer step, {len(outers)} outer steps')
    for oi, o in enumerate(outers):
        u = lambda x: np.uint32(x)
        a1 = np_rol(d1, 16) ^ u(o['Y12'])
        Y6 = (a1 - u(o['Y1']) - u(o['w12'])).astype(np.uint32)
        Y10 = np_rol(Y6, 7) ^ u(o['C2b1'])
        Y14 = (Y10 - u(o['C2c1'])).astype(np.uint32)
        Y2 = np_rol(Y14, 8) ^ u(o['C2d1'])
        w0 = (Y2 - u(o['C2a1']) - u(o['C2b1'])).astype(np.uint32)
        t = (u(rol(o['K0d1'], 16)) ^ (u(IV[0]) + u(IV[4]) + w0)).astype(np.uint32)
        distinct = len(np.unique(t))
        j = int(np.argmin(t))
        print(f'  outer {oi}: distinct t over the cube {distinct}/{1 << 21}; min t {int(t[j])}; '
              f'count t < 2^16: {int(np.sum(t < 65536))}')
        if int(t[j]) < 4096 and int(t[j]) > 0:
            found.append((o, int(d1[j])))
    for o, dd in found[:4]:
        ii, words = inner(o, dd)
        t = ii['t']
        chunk = bytes(rng.getrandbits(8) for _ in range(1024))
        Pp = chunk * t
        A = struct.pack('<16I', *words)[:55]
        wb = list(words); wb[4] = W4B; wb[5] = (words[5] + DELTA) & M
        B = struct.pack('<16I', *wb)[:63]
        dA = V.blake3(Pp + A, 2); dB = V.blake3(Pp + B, 2)
        stack = O.stack_of_prefix([O.chunk_cv(chunk, i) for i in range(t)])
        cvA = O.chunk_cv(A, t); cvB = O.chunk_cv(B, t)
        ok_root = dA == O.root_from_stack(stack, cvA) and dB == O.root_from_stack(stack, cvB)
        print(f'  complete messages: t = {t}, |P||A| = {len(Pp + A)}, |P||B| = {len(Pp + B)}; organizer digests '
              f'= root(stack, CV_t): {ok_root}; CV words 0,2,5,7 equal: {all(cvA[i] == cvB[i] for i in (0, 2, 5, 7))}; '
              f'digests equal: {dA == dB} (expected False: half of the CV only)')
        print(f'    A = {(Pp + A)[-55:].hex()}')
        print(f'    B = {(Pp + B)[-63:].hex()}')


if __name__ == '__main__':
    main()
