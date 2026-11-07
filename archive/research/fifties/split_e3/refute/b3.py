'''Own BLAKE3 compression written from the spec (no team code), with a full named trace of every G intermediate.
Self-tests: 7 rounds against the published BLAKE3("") digest; 2 rounds against the team compress2 (only as a cross-check).
Names: G call "R{r}{C|D}{i}" (round r, column/diagonal i), words .a1 .d1 .c1 .b1 .a2 .d2 .c2 .b2; message m0..m15; T0, T1.'''

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

import struct
M = 0xFFFFFFFF
IV = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
CALLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15), (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]
def rotr(x, n): return ((x >> n) | (x << (32 - n))) & M
def rotl(x, n): return rotr(x, (32 - n) % 32)
def gname(r, i): return 'R%d%s%d' % (r, 'C' if i < 4 else 'D', i % 4)
def schedule(rounds):
    '''message index used as (x, y) by every G call of every round'''
    s = list(range(16)); out = []
    for r in range(rounds):
        out.append([(s[2 * i], s[2 * i + 1]) for i in range(8)]); s = [s[p] for p in PERM]
    return out
def compress(m, T0, T1, blen, flags, rounds=7, cv=IV, trace=None):
    v = list(cv) + IV[:4] + [T0 & M, T1 & M, blen, flags]
    for r, sch in enumerate(schedule(rounds)):
        for i, (a, b, c, d) in enumerate(CALLS):
            x, y = m[sch[i][0]], m[sch[i][1]]
            a1 = (v[a] + v[b] + x) & M; d1 = rotr(v[d] ^ a1, 16); c1 = (v[c] + d1) & M; b1 = rotr(v[b] ^ c1, 12)
            a2 = (a1 + b1 + y) & M; d2 = rotr(d1 ^ a2, 8); c2 = (c1 + d2) & M; b2 = rotr(b1 ^ c2, 7)
            if trace is not None:
                n = gname(r, i)
                for k, val in zip(('a1', 'd1', 'c1', 'b1', 'a2', 'd2', 'c2', 'b2'), (a1, d1, c1, b1, a2, d2, c2, b2)):
                    trace[n + '.' + k] = val
            v[a], v[b], v[c], v[d] = a2, b2, c2, d2
    return [v[i] ^ v[i + 8] for i in range(8)], v
W4, W13, LEN_A, FLAGS = 0x97475638, 0x7c006, 55, 3     # pinned m4, m13 (A side), block length, flags (team constants)
PINS = {'R0D3.a2': 0x29d4fa98, 'R0D2.b2': 0xbee3af28, 'R0D1.c2': 0x44036000, 'R0D0.d2': 0x40c58500}  # X3 X7 X11 X15
# round-1 column outputs: Y_a = R1C?.a2, Y_b = .b2, Y_c = .c2, Y_d = .d2 (state index from CALLS)
E3IN = {'Y3': 'R1C3.a2', 'Y4': 'R1C0.b2', 'Y9': 'R1C1.c2', 'Y14': 'R1C2.d2'}            # + m15 (=0), m8
E1IN = {'Y1': 'R1C1.a2', 'Y6': 'R1C2.b2', 'Y11': 'R1C3.c2', 'Y12': 'R1C0.d2'}           # + m12, m5
def point(m, T0, T1):
    tr = {}; compress(m, T0, T1, LEN_A, FLAGS, rounds=2, trace=tr)
    for i in range(16): tr['m%d' % i] = m[i]
    tr['T0'], tr['T1'] = T0, T1
    return tr
if __name__ == '__main__':
    # published BLAKE3("") = af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262 (flags CHUNK_START|CHUNK_END|ROOT)
    h, _ = compress([0] * 16, 0, 0, 0, 1 | 2 | 8, rounds=7)
    hx = b''.join(struct.pack('<I', w) for w in h).hex()
    print('BLAKE3("") 7 rounds:', hx, 'OK' if hx == 'af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262' else 'MISMATCH')
    import sys, random
    sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/pkg12b/pkg/blake3-r2/experiments'))
    import halfsearch as hs
    rnd = random.Random(1); bad = 0
    for _ in range(300):
        n = rnd.randrange(1, 65); msg = bytes(rnd.getrandbits(8) for _ in range(n)); t = rnd.getrandbits(51)
        w, dg, y = hs.compress2(msg, t, 3)
        mm = list(struct.unpack('<16I', msg + bytes(64 - n)))
        tr = {}; mine, _ = compress(mm, t & M, t >> 32, n, 3, rounds=2, trace=tr)
        ymine = [None] * 16
        for i, (a, b, c, d) in enumerate(CALLS[:4]):
            ymine[a], ymine[b], ymine[c], ymine[d] = (tr['R1C%d.%s' % (i, k)] for k in ('a2', 'b2', 'c2', 'd2'))
        bad += (mine != dg) or (ymine != y)
    print('2-round digest and Y state vs team compress2: %d/300 mismatches' % bad)
