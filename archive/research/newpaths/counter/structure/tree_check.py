"""Part 1: the tree-mode claim on real messages, organizer verifier (2 rounds).
M = P||X, M' = P||X', P = t identical full chunks, X of 55 bytes, X' of 63 bytes.
Checks per t:
 (a) organizer digest(P||X) == own root_from_stack(own stack(P), own CV_t(X))  [digest is a function of CV_t(X)]
 (b) the organizer's own last-chunk descriptor is (IV, words(X), counter t, len, flags 3) and its
     _compress gives the same CV as the own code; the v12/v13 it feeds are t & mask, t >> 32
 (c) planted CV collision: patch the organizer _compress so that ONLY the last-chunk compression of X'
     returns the CV of X; the organizer then outputs equal digests for P||X and P||X'  (equal CV => equal digest)
 (d) unpatched digests of P||X and P||X' differ (different CVs give different digests here)
 (e) C program tree64 (own, SIMD + threads) equals the organizer digest (validation for the large-t run)
usage: python -B tree_check.py [nx]
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

import os, sys, random, struct, subprocess, time
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
import blake3 as V
import b3own as O

HERE = os.path.dirname(os.path.abspath(__file__))
WSLDIR = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/counter/structure')
R = 2


def org_last_cv(x, t):
    out = V._chunk_output(x, t, R)
    return out, tuple(V._compress(*out, R)[:8])


def run_c(t, chunk, xs):
    cmd = ['wsl', '-d', 'Ubuntu', '--', WSLDIR + '/tree64', str(t), chunk.hex()] + [x.hex() for x in xs]
    txt = subprocess.run(cmd, capture_output=True, text=True, timeout=600).stdout
    digs = [struct.pack('<8I', *[int(h, 16) for h in ln.split()[1:]]) for ln in txt.splitlines()
            if ln.startswith('digest_words')]
    stack = [tuple(int(h, 16) for h in ln.split()[1:]) for ln in txt.splitlines() if ln.startswith('stack')
             and not ln.startswith('stack ')]
    return digs, stack, txt


def main():
    nx = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    rng = random.Random(20261008)
    ts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 16, 17, 31, 32, 33, 63, 64, 65, 100, 255, 256, 257, 1000, 1024, 1025]
    tot = dict(a=0, b=0, c=0, d=0, e=0, n=0, nc=0)
    t0 = time.time()
    for t in ts:
        chunk = bytes(rng.randrange(256) for _ in range(1024))
        P = chunk * t
        own_stack = O.stack_of_prefix([O.chunk_cv(chunk, i) for i in range(t)])
        xs = []
        for _ in range(nx):
            xa = bytes(rng.randrange(256) for _ in range(55))
            xb = bytes(rng.randrange(256) for _ in range(55)) + bytes(8)   # 63 bytes ending in 8 zero bytes
            xs += [xa, xb]
        digs = {}
        for x in xs:
            d_org = V.blake3(P + x, R)
            digs[x] = d_org
            own_cv = O.chunk_cv(x, t)
            d_own = O.root_from_stack(own_stack, own_cv)
            tot['a'] += d_org == d_own
            (cv_in, words, ctr, blen, flags), cv_org = org_last_cv(x, t)
            ok_b = (cv_in == V.IV and ctr == t and blen == len(x) and flags == 3 and cv_org == own_cv
                    and tuple(words) == struct.unpack('<16I', x.ljust(64, b'\0')))
            tot['b'] += ok_b
            tot['n'] += 1
        # (c) planted: for each pair (xa, xb) make the organizer believe CV_t(xb) = CV_t(xa)
        for i in range(0, len(xs), 2):
            xa, xb = xs[i], xs[i + 1]
            out_a, cv_a = org_last_cv(xa, t)
            out_b, _ = org_last_cv(xb, t)
            real = V._compress

            def patched(cv, words, counter, block_len, flags, rounds, _ob=out_b, _oa=out_a):
                if (tuple(cv), tuple(words), counter, block_len, flags) == tuple(map(lambda z: tuple(z) if isinstance(z, (list, tuple)) else z, _ob)):
                    return real(*_oa, rounds)
                return real(cv, words, counter, block_len, flags, rounds)
            V._compress = patched
            try:
                db_patched = V.blake3(P + xb, R)
            finally:
                V._compress = real
            tot['c'] += db_patched == digs[xa]
            tot['d'] += digs[xa] != digs[xb]
        # (e) C program
        cd, cstack, _ = run_c(t, chunk, xs)
        okc = len(cd) == len(xs) and all(cd[k] == digs[x] for k, x in enumerate(xs)) and \
            [tuple(s) for s in cstack] == [tuple(s) for s in own_stack]
        tot['e'] += okc
        tot['nc'] += 1
        print(f't={t:5d} len(M)={1024 * t + 55}/{1024 * t + 63}  a,b ok {sum(1 for _ in xs)}  C ok {okc}  '
              f'stack {len(own_stack)}  {time.time() - t0:.0f}s', flush=True)
    npairs = tot['n'] // 2
    print(f"(a) organizer digest == own root(stack, CV_t(X)): {tot['a']}/{tot['n']}")
    print(f"(b) organizer last-chunk descriptor = (IV, words, t, len, 3) and same CV: {tot['b']}/{tot['n']}")
    print(f"(c) planted CV collision -> organizer digests equal: {tot['c']}/{npairs}")
    print(f"(d) unpatched pairs have different digests: {tot['d']}/{npairs}")
    print(f"(e) C tree64 == organizer digests and stack (all X of the t): {tot['e']}/{tot['nc']} values of t")
    # (f) 64-bit counter split, direct: organizer _chunk_output/_compress vs own for t >= 2^32
    rng2 = random.Random(5)
    okf = 0
    big = [2 ** 32, 2 ** 32 + 5, 2 ** 33 + 12345, 2 ** 51 - 1, rng2.randrange(2 ** 32, 2 ** 51)]
    for t in big:
        for L in (55, 63):
            x = bytes(rng2.randrange(256) for _ in range(L))
            (cv_in, words, ctr, blen, flags), cv_org = org_last_cv(x, t)
            out, st = O.compress_full(O.IV, struct.unpack('<16I', x.ljust(64, b'\0')), t, L, 3)
            okf += (cv_org == tuple(out[:8]) and ctr == t and flags == 3)
    print(f"(f) t >= 2^32 last-chunk CV, organizer == own (v12 = t & mask, v13 = t >> 32): {okf}/{2 * len(big)}")
    print(f"shortest pair: t = 1, lengths 1079 and 1087 bytes; counter words v12 = 1, v13 = 0, v14 = 55/63, v15 = 3")
    print(f"length bound: verifier rejects len >= 2^61 bytes -> t <= 2^51 - 1, v13 < 2^19")


if __name__ == '__main__':
    main()
