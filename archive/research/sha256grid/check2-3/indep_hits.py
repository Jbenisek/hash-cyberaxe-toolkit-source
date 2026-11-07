"""check2-3: independent re-verification of dumped tail successes (43-word records: j a1 k cv[8] Mx[16] My[16]).
Own numpy SHA-256 step function with the FIPS 180-4 constants (validated on full SHA-256 of 'abc' against hashlib);
checks per record: Mx != My, equal 38-step compression outputs (with feed-forward), every A/E cell of rows 0..37 and
W cell of rows 0..37 from vt38.CELL, '+' conditions, all vt38.TWOBIT conditions, W7 in F7 with dW7 = D7, and that the
trace reproduces the variant (A_0, A_1, A_2) = (A0L[j], a1, A2L[k]) and the dense part's A_3..A_15, E_7..E_15, W_11..W_15
(member x and y); vt38.valid(variant) on a random subsample.  usage: python indep_hits.py file.hits [...]"""

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

import sys, hashlib, struct, importlib.util, random
sys.dont_write_bytecode = True
import numpy as np
BASE = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38a/base')
spec = importlib.util.spec_from_file_location('vt38', BASE + r'\experiments\vt38.py')
vt = importlib.util.module_from_spec(spec); spec.loader.exec_module(vt)

K = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01,
     0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
     0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
     0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
     0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08,
     0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
     0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]
IV = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
U = np.uint32
def ror(x, n): return (x >> U(n)) | (x << U(32 - n))
def S0(x): return ror(x, 2) ^ ror(x, 13) ^ ror(x, 22)
def S1(x): return ror(x, 6) ^ ror(x, 11) ^ ror(x, 25)
def s0(x): return ror(x, 7) ^ ror(x, 18) ^ (x >> U(3))
def s1(x): return ror(x, 17) ^ ror(x, 19) ^ (x >> U(10))
def Ch(x, y, z): return (x & y) ^ (~x & z)
def Mj(x, y, z): return (x & y) ^ (x & z) ^ (y & z)

def trace(cv, M, R):
    """cv: (n,8) = (a,b,c,d,e,f,g,h); M: (n,16). Returns A, E (index i+4, i = -4..R-1), W (0..R-1), output (n,8)."""
    n = cv.shape[0]
    W = [M[:, i] for i in range(16)]
    for i in range(16, R): W.append(s1(W[i - 2]) + W[i - 7] + s0(W[i - 15]) + W[i - 16])
    A = [cv[:, 3], cv[:, 2], cv[:, 1], cv[:, 0]]; E = [cv[:, 7], cv[:, 6], cv[:, 5], cv[:, 4]]
    for i in range(R):
        e = A[i] + E[i] + S1(E[i + 3]) + Ch(E[i + 3], E[i + 2], E[i + 1]) + U(K[i]) + W[i]
        a = e - A[i] + S0(A[i + 3]) + Mj(A[i + 3], A[i + 2], A[i + 1])
        E.append(e); A.append(a)
    st = [A[R + 3], A[R + 2], A[R + 1], A[R], E[R + 3], E[R + 2], E[R + 1], E[R]]
    out = np.stack([cv[:, q] + st[q] for q in range(8)], axis=1)
    return A, E, W, out

def selftest():
    assert list(vt.K[:38]) == K[:38], 'vt38.K differs from FIPS 180-4'
    blk = b'abc' + b'\x80' + b'\x00' * 52 + struct.pack('>Q', 24)
    M = np.array([struct.unpack('>16I', blk)], dtype=U); cv = np.array([IV], dtype=U)
    with np.errstate(over='ignore'):
        _, _, _, out = trace(cv, M, 64)
    assert b''.join(struct.pack('>I', int(x)) for x in out[0]) == hashlib.sha256(b'abc').digest(), 'SHA-256 step function wrong'
    return 'own SHA-256 step function = hashlib on "abc" (64 rounds); vt38.K[:38] = FIPS K'

def check(fn):
    b = np.fromfile(fn, dtype='<u4'); n = b.size // 43; r = b[:n * 43].reshape(n, 43).astype(U)
    j, a1, k = r[:, 0], r[:, 1], r[:, 2]; cv = r[:, 3:11]; Mx = r[:, 11:27]; My = r[:, 27:43]
    A0L = np.array(vt.emb()['A0'], dtype=U); A2L = np.array(vt.emb()['A2'], dtype=U)
    fails = {}
    def flag(name, ok):
        fails[name] = fails.get(name, 0) + int((~ok).sum())
    with np.errstate(over='ignore'):
        Ax, Ex, Wx, ox = trace(cv, Mx, 38); Ay, Ey, Wy, oy = trace(cv, My, 38)
        flag('messages distinct', (Mx != My).any(axis=1))
        flag('equal 38-step outputs', (ox == oy).all(axis=1))
        for i in range(38):
            for nm, X, Y in (('A', Ax[i + 4], Ay[i + 4]), ('E', Ex[i + 4], Ey[i + 4]), ('W', Wx[i], Wy[i])):
                m, v, d = (U(c) for c in vt.CELL[nm][i][:3])
                flag('%s cells rows %s' % (nm, '0..15' if i < 16 else '16..37'), ((X & m) == v) & ((X ^ Y) == d))
            if vt.PLUS[i]:
                flag("'+' conditions", ((Ex[i + 4] ^ Ex[i + 3]) & U(vt.PLUS[i])) == 0)
        G = {'A': lambda i: Ax[i + 4], 'E': lambda i: Ex[i + 4], 'W': lambda i: Wx[i]}
        for (k1, i1, b1, ne, k2, i2, b2) in vt.TWOBIT:
            flag('two-bit conditions', (((G[k1](i1) >> U(b1)) ^ (G[k2](i2) >> U(b2))) & U(1)) == U(ne))
        flag('W7 in F7 and dW7 = D7', ((s0(Wx[7] + U(vt.D7)) - s0(Wx[7])) == U(vt.T7)) & ((Wy[7] - Wx[7]) == U(vt.D7)))
        TX, TY = vt.TX, vt.TY
        okv = (Ax[4] == A0L[j]) & (Ax[5] == a1) & (Ax[6] == A2L[k]) & (Ay[4] == A0L[j]) & (Ay[5] == a1) & (Ay[6] == A2L[k])
        for i in range(3, 16): okv &= (Ax[i + 4] == U(TX[0][i])) & (Ay[i + 4] == U(TY[0][i]))
        for i in range(7, 16): okv &= (Ex[i + 4] == U(TX[1][i])) & (Ey[i + 4] == U(TY[1][i]))
        for i in range(11, 16): okv &= (Wx[i] == U(TX[2][i])) & (Wy[i] == U(TY[2][i]))
        flag('trace = variant (A0,A1,A2) + dense part', okv)
    rng = random.Random(20261010); idx = rng.sample(range(n), min(n, 3000)); badv = 0
    for t in idx:
        badv += not vt.valid(vt.variant(int(A0L[j[t]]), int(a1[t]), int(A2L[k[t]]))[0])
    print('%s: %d records; failures by check: %s; vt38.valid on %d sampled variants: %d invalid; distinct (j,a1,k): %d; distinct A0: %d'
          % (fn.split('\\')[-1], n, ', '.join('%s %d' % kv for kv in fails.items()), len(idx), badv,
             len(set(zip(j.tolist(), a1.tolist(), k.tolist()))), len(set(j.tolist()))))
    return sum(fails.values()) + badv

if __name__ == '__main__':
    print(selftest())
    tot = 0
    for fn in sys.argv[1:]: tot += check(fn)
    print('TOTAL failures: %d' % tot)
