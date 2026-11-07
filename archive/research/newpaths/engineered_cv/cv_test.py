r"""Engineered chaining value (research only).  Does a CHOSEN CV word (ground by preprocessing, about 2^32 per
word) change the free-half construction's class rate or residual?  Pin H8, lengths 55/63, last block of a
multi-block chunk: flags 10 (root, counter 0) or flags 2 (non-root, constant t).

Per pool we log, over many trials:
  half   : words 0,2,5,7 of the compression output equal (own code) + referee V._compress once per chosen value
  c3     : C3 outputs (Y3,Y7,Y11,Y15 of A and of B) identical to the cv = IV reference (exact)
  bits   : per-bit 1-frequency of 384 difference bits: other-half output XOR (words 1,3,4,6), E1 and E3 outputs XOR
  res    : per-bit 1-frequency of the residual words Y1,Y6,Y12,w12,Y9,Y14,w8 and w5 (256 bits)
  beta   : frequency of the top XOR difference of E1.c1 (the counted class's beta variable)
  low8   : rate of low-byte equality per other-half word
Each chosen-word pool is compared with the baseline pool (random chained CV, same flags) by the mean squared
z-score over the bit vectors (about 1 +- 0.07 if the distributions are the same).
usage: python -B cv_test.py FLAGS T VALUES TRIALS SEED      (T = counter, 0 for flags 10)
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

import sys, random, time, math
sys.dont_write_bytecode = True
HERE = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/engineered_cv')
sys.path.insert(0, HERE)
sys.path.insert(1, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
import blake3 as V
import b3own as O
import construct as C

M = 0xFFFFFFFF
H8 = (0x29D4FA98, 0xBEE3AF28, 0x44036000, 0x40C58500, 0x97475638, 0x0007C006)
HALF = (0, 2, 5, 7)
OTHER = (1, 3, 4, 6)


class Pool:
    def __init__(s):
        s.n = 0; s.half = 0; s.c3 = 0; s.ref = 0; s.refn = 0
        s.bits = [0] * 384; s.res = [0] * 256; s.beta = {}; s.low8 = [0] * 4

    def add(s, outA, outB, trA, trB, wa, c3ref):
        s.n += 1
        s.half += all(outA[i] == outB[i] for i in HALF)
        c3 = tuple(trA['C3'][k] for k in ('a2', 'b2', 'c2', 'd2')) + tuple(trB['C3'][k] for k in ('a2', 'b2', 'c2', 'd2'))
        s.c3 += c3 == c3ref
        dv = [outA[i] ^ outB[i] for i in OTHER]
        for j, x in enumerate(dv):
            s.low8[j] += (x & 0xFF) == 0
        for k in ('a2', 'b2', 'c2', 'd2'):
            dv.append(trA['E1'][k] ^ trB['E1'][k])
        for k in ('a2', 'b2', 'c2', 'd2'):
            dv.append(trA['E3'][k] ^ trB['E3'][k])
        for j, x in enumerate(dv):
            base = 32 * j
            while x:
                lb = x & -x; s.bits[base + lb.bit_length() - 1] += 1; x ^= lb
        res = [trA['C1']['a2'], trA['C2']['b2'], trA['C0']['d2'], wa[12], trA['C1']['c2'], trA['C2']['d2'], wa[8], wa[5]]
        for j, x in enumerate(res):
            base = 32 * j
            while x:
                lb = x & -x; s.res[base + lb.bit_length() - 1] += 1; x ^= lb
        b = trA['E1']['c1'] ^ trB['E1']['c1']
        s.beta[b] = s.beta.get(b, 0) + 1


def msz(p, q, vec):
    """mean squared two-sample z over a bit vector."""
    tot = 0.0; m = 0
    for a, b in zip(getattr(p, vec), getattr(q, vec)):
        pa, pb = a / p.n, b / q.n
        pp = (a + b) / (p.n + q.n)
        v = pp * (1 - pp) * (1 / p.n + 1 / q.n)
        if v <= 0:
            if pa != pb:
                tot += 1e6
            continue
        tot += (pa - pb) ** 2 / v; m += 1
    return tot / max(m, 1), m


def run_cv(pool, rng, cv, flags, t, ntr, c3ref, referee):
    P = C.transfer(H8, cv, 55, 63)
    assert P is not None
    for k in range(ntr):
        o = C.outer(P, cv, 55, flags, 0, *[rng.getrandbits(32) for _ in range(8)])
        wa, wb = C.inner_const(P, o, cv, t)
        _, okA = C.block_bytes(wa, 55); _, okB = C.block_bytes(wb, 63)
        assert okA and okB
        trA, trB = {}, {}
        outA, _ = O.compress_full(cv, wa, t, 55, flags, trace=trA)
        outB, _ = O.compress_full(cv, wb, t, 63, flags, trace=trB)
        pool.add(outA, outB, trA, trB, wa, c3ref)
        if referee and k == 0:
            vA = V._compress(tuple(cv), wa, t, 55, flags, 2)[:8]
            vB = V._compress(tuple(cv), wb, t, 63, flags, 2)[:8]
            pool.refn += 1; pool.ref += all(vA[i] == vB[i] for i in HALF)


def values(i, rng, base, nval):
    v = [0, M, O.IV[i], O.IV[i] ^ M]
    v += [1 << j for j in range(32)] + [(1 << j) - 1 for j in range(1, 32)]
    v += [M ^ (1 << j) for j in range(32)] + [O.IV[i] ^ (1 << j) for j in range(32)]
    if i in (2, 6):                       # KK = cv2 + cv6 set to 0, -1, 2^31 (the only cv term in the transfer rule)
        o = base[6 if i == 2 else 2]
        v += [(-o) & M, (M - o) & M, (0x80000000 - o) & M]
    out = list(dict.fromkeys(v))
    while len(out) < nval:
        out.append(rng.getrandbits(32))
    return out[:nval]


def main():
    flags, t, nval, ntr, seed = (int(a) for a in sys.argv[1:6])
    rng = random.Random(seed)
    t0 = time.time()
    # C3 reference with cv = IV
    P = C.transfer(H8, O.IV, 55, 63)
    o = C.outer(P, O.IV, 55, flags, 0, *[rng.getrandbits(32) for _ in range(8)])
    wa, wb = C.inner_const(P, o, O.IV, t)
    trA, trB = {}, {}
    O.compress_full(O.IV, wa, t, 55, flags, trace=trA); O.compress_full(O.IV, wb, t, 63, flags, trace=trB)
    c3ref = tuple(trA['C3'][k] for k in ('a2', 'b2', 'c2', 'd2')) + tuple(trB['C3'][k] for k in ('a2', 'b2', 'c2', 'd2'))
    nb = nval * ntr
    base = Pool()                          # baseline: random chained CV per value, nothing chosen
    for _ in range(2 * nval):
        run_cv(base, rng, [rng.getrandbits(32) for _ in range(8)], flags, t, ntr, c3ref, True)
    ivp = Pool()
    run_cv(ivp, rng, list(O.IV), flags, t, 2 * nb, c3ref, True)
    top = max(base.beta, key=base.beta.get)
    print(f'cv_test flags {flags} t {t}: {nval} chosen values x {ntr} trials per position; baseline {base.n} trials '
          f'(random CV), IV pool {ivp.n}; top E1.c1 beta {top:08x}')
    hdr = ('pool        n      half    c3same  referee  beta_top  low8(w1,w3,w4,w6)        msz_bits  msz_res  '
           'log2 P(two E1.c1 diffs equal)')
    print(hdr)

    def line(name, p):
        mb, _ = msz(p, base, 'bits'); mr, _ = msz(p, base, 'res')
        low = ' '.join(f'{x / p.n * 256:.2f}' for x in p.low8)
        cp = sum(x * (x - 1) for x in p.beta.values()) / (p.n * (p.n - 1))
        print(f'{name:<10} {p.n:6d} {p.half:6d} {p.c3:8d} {p.ref:4d}/{p.refn:<4d} {p.beta.get(top, 0) / p.n:.5f}  '
              f'{low:<24} {mb:7.3f}  {mr:7.3f}  {math.log2(cp) if cp > 0 else float("-inf"):6.2f}')
    line('baseline', base)
    line('cv=IV', ivp)
    null = len(sys.argv) > 6 and sys.argv[6] == 'null'   # null reference: same pools, nothing chosen
    for i in range(8):
        p = Pool()
        b0 = [rng.getrandbits(32) for _ in range(8)]
        for c in values(i, rng, b0, nval):
            cv = [rng.getrandbits(32) for _ in range(8)]
            if i in (2, 6):
                cv = list(b0)
            if not null:
                cv[i] = c
            else:
                cv = [rng.getrandbits(32) for _ in range(8)]
            run_cv(p, rng, cv, flags, t, ntr, c3ref, True)
        line(f'null{i}' if null else f'cv[{i}]', p)
    print(f'(low8 is x256: 1.00 = uniform; msz about 1 +- {math.sqrt(2 / 384):.2f} (bits) / {math.sqrt(2 / 256):.2f} (res) '
          f'if the pool matches the baseline)  time {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
