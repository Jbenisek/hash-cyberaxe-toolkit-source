"""Cross-check q3gpu's C/CUDA logic against the base package's reference Python (vt38.py), read-only.
usage: python check_dumps.py valid_dump.bin smc_dump.bin V smc_hits.bin [gpu_hits.bin ...]"""

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

import sys, struct, importlib.util
sys.dont_write_bytecode = True
BASE = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38a/base')
spec = importlib.util.spec_from_file_location('vt38', BASE + r'\experiments\vt38.py')
vt = importlib.util.module_from_spec(spec); spec.loader.exec_module(vt)
M = vt.M; R = vt.R; EMB = vt.emb(); A0L, A2L = EMB['A0'], EMB['A2']
PART = 58 * 4; VREC = 8 * 4

def check_valid(fn):
    b = open(fn, 'rb').read(); n = len(b) // 16; bad = nv = 0
    for t in range(n):
        a0, a1, a2, v = struct.unpack_from('<4I', b, 16 * t)
        ref = vt.valid(vt.variant(a0, a1, a2)[0])
        nv += ref; bad += (ref != bool(v))
    print('validity: %d candidates, %d valid by vt38.valid, %d disagreements' % (n, nv, bad))
    return bad

def part(b, o):
    w = struct.unpack_from('<58I', b, o)
    a = [w[0:11], w[11:22]]; e = [w[22:33], w[33:44]]; ww = [w[44:51], w[51:58]]
    p = vt._base()
    for m in (0, 1):
        A, E, W = p[3 * m], p[3 * m + 1], p[3 * m + 2]
        for r in range(12, 23): A[r], E[r] = a[m][r - 12], e[m][r - 12]
        for r in range(16, 23): W[r] = ww[m][r - 16]
    return p

def vrec(b, o):
    jk, a1, w8x, w8y, w9x, w9y, w10x, w10y = struct.unpack_from('<8I', b, o)
    return jk & 0xffff, a1, jk >> 16, (w8x, w9x, w10x), (w8y, w9y, w10y)

def check_vpool(b, V):
    bad = 0; cnt = {}
    for v in range(V):
        j, a1, k, wx, wy = vrec(b, VREC * v)
        var = vt.variant(A0L[j], a1, A2L[k])[0]; (_, _, Wx), (_, _, Wy) = var
        if not vt.valid(var) or (Wx[8], Wx[9], Wx[10]) != wx or (Wy[8], Wy[9], Wy[10]) != wy: bad += 1
        cnt[j] = cnt.get(j, 0) + 1
    print('variant pool: %d records, %d bad (validity or W8..W10), %d distinct A0' % (V, bad, len(cnt)))
    return bad

def check_smc(fn, V):
    b = open(fn, 'rb').read(); bad = check_vpool(b, V); o = VREC * V
    stats = {}; tbad = 0
    m23, v23 = vt.CELL['W'][23][0], vt.CELL['W'][23][1]
    while o < len(b):
        I, tid, r, flag = struct.unpack_from('<4I', b, o); o += 16
        if I < 23:
            par = part(b, o); q = part(b, o + PART); o += 2 * PART
            p = [x[:] for x in par]; Ax, Ex, Wx, Ay, Ey, Wy = p
            m, v, _, _ = vt.CELL['E'][I]; pq = vt.PLUS[I]
            e = (r & ~m & M) | v
            if pq: e = (e & ~pq & M) | (Ex[I - 1] & pq)
            Wx[I] = (e - (Ax[I-4] + Ex[I-4] + vt.S1(Ex[I-1]) + vt.CH(Ex[I-1], Ex[I-2], Ex[I-3]) + vt.K[I])) & M
            dw = (vt.s1(Wx[I-2]) - vt.s1(Wy[I-2]) + Wx[I-7] - Wy[I-7] - (vt.T7 if I == 22 else 0)) & M
            Wy[I] = (Wx[I] - dw) & M
            vt._step(Ax, Ex, Wx, I); vt._step(Ay, Ey, Wy, I)
            ok = vt._rowok(p, I)
            s = stats.setdefault(I, [0, 0, 0]); s[0] += 1; s[1] += ok
            if ok != bool(flag): s[2] += 1
            elif ok:
                for k in range(6):
                    if p[k][I] != q[k][I]: s[2] += 1; break
        else:
            p = part(b, o); j, a1, k, wvx, wvy = vrec(b, o + PART); o += PART + VREC
            st, deep = flag & 0xff, flag >> 8
            Ax, Ex, Wx, Ay, Ey, Wy = p
            for i in (8, 9, 10): Wx[i], Wy[i] = wvx[i - 8], wvy[i - 8]
            w = (r & ~m23 & M) | v23
            w7 = (w - vt.s1(Wx[21]) - Wx[16] - vt.s0(Wx[8])) & M
            if not vt.inF7(w7): rs, rd = 0, 22
            else:
                Wx[23] = w; Wy[23] = (vt.s1(Wy[21]) + Wy[16] + vt.s0(Wy[8]) + w7 + vt.D7) & M; rs, rd = 2, 37
                for i in range(23, R):
                    if i > 23: Wx[i] = vt._sched(Wx, i); Wy[i] = vt._sched(Wy, i)
                    vt._step(Ax, Ex, Wx, i); vt._step(Ay, Ey, Wy, i)
                    if not vt._rowok(p, i): rs, rd = 1, i - 1; break
            s = stats.setdefault(23, [0, 0, 0]); s[0] += 1; s[1] += (rs == 2)
            if (rs, rd) != (st, deep): s[2] += 1
    for I in sorted(stats):
        print('row %s: %d proposals re-run by vt38 code, %d survivors/successes, %d disagreements' % (I if I < 23 else '23..37 (tail)', *stats[I]))
        tbad += stats[I][2]
    return bad + tbad

def check_hits(fn):
    b = open(fn, 'rb').read(); n = len(b) // 172; bad = 0
    for t in range(n):
        w = struct.unpack_from('<43I', b, 172 * t)
        j, a1, k = w[0], w[1], w[2]; cv = list(w[3:11]); mx = list(w[11:27]); my = list(w[27:43])
        a0, a2 = A0L[j], A2L[k]; var = vt.variant(a0, a1, a2)[0]
        r16, f7, deep, (tx, ty, wx, wy) = vt.outcome(cv, a0, a1, a2)
        ok = vt.valid(var) and r16 and f7 and deep == 37 and wx == mx and wy == my and mx != my and vt.compress(cv, mx) == vt.compress(cv, my)
        for i in range(0, R):
            for kk in 'AE':
                mm, v, d, _ = vt.CELL[kk][i]; X = tx['AE'.index(kk)][i]; Y = ty['AE'.index(kk)][i]
                if X & mm != v or X ^ Y != d: ok = False
            if (tx[1][i] ^ tx[1][i - 1]) & vt.PLUS[i]: ok = False
        bad += not ok
    print('%s: %d successes re-verified with vt38 (outcome/compress/cells): %d failures' % (fn, n, bad))
    return bad

if __name__ == '__main__':
    if sys.argv[1] == '--hits': tot = 0; files = sys.argv[2:]
    else: tot = check_valid(sys.argv[1]) + check_smc(sys.argv[2], int(sys.argv[3])); files = sys.argv[4:]
    for fn in files: tot += check_hits(fn)
    print('TOTAL disagreements/failures: %d' % tot)
