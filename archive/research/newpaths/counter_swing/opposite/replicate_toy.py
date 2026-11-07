"""replicate_toy.py: item (2), the family of colliding message pairs that ONE last-chunk collision gives.

Input (read only): the counter-arrangement HIT lines of research\\newpaths\\counter\\toy\\out\\*.txt (W = 8 toy,
real full-hash collisions found there with P = t all-zero chunks).
Referee: blake3_toy.B3 at W = 8, a line-by-line port of the organizer's verifier/blake3.py that equals the
organizer copy at W = 32 (blake3_toy.py selftest).

For each chosen hit (A, B, t):
  a  the found pair: zero prefix of t chunks, digests equal and equal to the printed digest
  b  R random prefixes of exactly t chunks (random toy bytes, chunks NOT identical): P||A, P||B equal digests;
     number of distinct digests over the R prefixes (a multicollision would show repeats)
  c  last-chunk CV of A and B at counter t: all 8 words equal (the collision is at the CV level)
  d  other prefix lengths t' (t-1, t+1, t+2, t+255, t+256): full digest equal? CV words 0,2,5,7 equal?
  e  suffixes S appended to both (1, 9, 961, 969, 2000 toy bytes): digests equal?
  f  crossed prefixes P||A vs P'||B (P != P'): digests equal?
  g  no prefix (t = 0, the pair as single-chunk root messages): digests equal?
usage: python -B replicate_toy.py NHITS R SEED
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

import glob
import os
import random
import sys

sys.dont_write_bytecode = True
from blake3_toy import toy8

OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/counter/toy/out')


def load_hits():
    hits = []
    for fn in sorted(glob.glob(os.path.join(OUT, '*.txt'))):
        if fn.endswith('progress.txt'):
            continue
        for line in open(fn):
            if not line.startswith('HIT '):
                continue
            f = line.split()
            kv = {f[i]: f[i + 1] for i in range(1, len(f) - 9) if f[i] in ('arr', 'set', 't', 'A', 'B', 'run', 'outer')}
            if kv['arr'] == 'filed':
                continue
            hits.append(dict(arr=kv['arr'], set=int(kv['set']), t=int(kv['t']),
                             A=[int(c) for c in kv['A']], B=[int(c) for c in kv['B']],
                             dig=tuple(int(x, 16) for x in f[-8:]), src=os.path.basename(fn).encode('ascii', 'replace').decode(), outer=kv['outer']))
    return hits


def main():
    nh, R, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    rng = random.Random(seed)
    T = toy8()
    hits = load_hits()
    hits.sort(key=lambda h: h['t'])
    chosen = hits[:nh // 2] + rng.sample(hits[nh // 2:], nh - nh // 2)
    print(f'counter-arrangement toy hits available: {len(hits)} (t from {hits[0]["t"]} to {hits[-1]["t"]}); '
          f'chosen {len(chosen)}: the {nh // 2} smallest t and {nh - nh // 2} at random; R = {R} random prefixes each')
    tot = dict(a=0, b=0, bpairs=0, bdist=0, c=0, d_full=0, d_half=0, d_n=0, e=0, e_n=0, f=0, f_n=0, g=0)
    rnd = lambda n: [rng.randrange(4) for _ in range(n)]
    for h in chosen:
        A, B, t = h['A'], h['B'], h['t']
        assert len(A) == 55 and len(B) == 63
        P0 = [0] * (1024 * t)
        dA, dB = T.blake3(P0 + A), T.blake3(P0 + B)
        a_ok = dA == dB == h['dig']
        # b: random prefixes of t chunks
        digs, b_ok = set(), 0
        prefixes = []
        for _ in range(R):
            P = rnd(1024 * t)
            prefixes.append(P)
            x, y = T.blake3(P + A), T.blake3(P + B)
            b_ok += x == y
            digs.add(x)
        # c: CV level
        cA, cB = T.last_chunk_cv(P0 + A), T.last_chunk_cv(P0 + B)
        c_ok = cA == cB
        # d: other prefix lengths
        dl = []
        for tp in (t - 1, t + 1, t + 2, t + 255, t + 256):
            if tp < 1:
                continue
            P = rnd(1024 * tp)
            x, y = T.blake3(P + A), T.blake3(P + B)
            cx, cy = T.last_chunk_cv(P + A), T.last_chunk_cv(P + B)
            half = all(cx[i] == cy[i] for i in (0, 2, 5, 7))
            full_cv = cx == cy
            dl.append((tp, x == y, half, full_cv))
            tot['d_n'] += 1; tot['d_full'] += x == y; tot['d_half'] += half
        # e: suffixes
        el = []
        for s in (1, 9, 961, 969, 2000):
            S = rnd(s)
            P = prefixes[0]
            eq = T.blake3(P + A + S) == T.blake3(P + B + S)
            el.append((s, eq)); tot['e_n'] += 1; tot['e'] += eq
        # f: crossed prefixes
        fl = 0
        for k in range(min(R - 1, 4)):
            eq = T.blake3(prefixes[k] + A) == T.blake3(prefixes[k + 1] + B)
            fl += eq; tot['f_n'] += 1
        tot['f'] += fl
        # g: no prefix (single-chunk root messages)
        g_eq = T.blake3(A) == T.blake3(B)
        tot['a'] += a_ok; tot['b'] += b_ok; tot['bpairs'] += R; tot['bdist'] += len(digs); tot['c'] += c_ok
        tot['g'] += g_eq
        print(f"hit {h['arr']} set {h['set']} t={t} ({h['src']} outer {h['outer']}): a found pair {a_ok}; "
              f"b random prefixes {b_ok}/{R} equal, {len(digs)} distinct digests; c CV equal {c_ok}; "
              f"d other t' (t', digest eq, CV half eq, CV eq) {dl}; e suffix (len, eq) {el}; "
              f"f crossed equal {fl}; g no prefix equal {g_eq}")
    n = len(chosen)
    print('\nTOTALS')
    print(f'  a  found pair (zero prefix) collides, digest as printed: {tot["a"]}/{n}')
    print(f'  b  random t-chunk prefixes (non-identical chunks) collide: {tot["b"]}/{tot["bpairs"]}; '
          f'distinct digests {tot["bdist"]}/{tot["bpairs"]} (no multicollision across prefixes)')
    print(f'  c  last-chunk CV equal in all 8 words: {tot["c"]}/{n}')
    print(f"  d  other prefix lengths t': full digest equal {tot['d_full']}/{tot['d_n']}; CV words 0,2,5,7 equal {tot['d_half']}/{tot['d_n']}")
    print(f'  e  suffix appended to both: digest equal {tot["e"]}/{tot["e_n"]}')
    print(f'  f  crossed prefixes P||A vs P\'||B: digest equal {tot["f"]}/{tot["f_n"]}')
    print(f'  g  pair without prefix (single-chunk root, flags 11): digest equal {tot["g"]}/{n}')


if __name__ == '__main__':
    main()
