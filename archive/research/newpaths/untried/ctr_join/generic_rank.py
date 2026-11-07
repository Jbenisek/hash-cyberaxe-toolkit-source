"""ctr x join, part R: generic (linearized) ranks of model.py's system.

Each equation of model.system() becomes a linear form with random nonzero coefficients mod a
61-bit prime (the generic rank of the sparsity pattern).  S = solution space.
Reports, per counter setting:
  dim S;  rank of key1-words (T1) and key3-words (T3) on S;  rank of (T1,T3) jointly;
  dim of the E3-fixed fibre and the rank T1 still has on it (algebraic E1-only freedom);
  dim of the E1-fixed fibre and the rank T3 still has on it (algebraic E3-only freedom).
This says whether one-sided freedom exists algebraically; struct_split.py says whether any
TRIANGULAR (forward-computable) parametrization reaches it.
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

import random
import sys

sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/counter_next/knobs'))
import model  # noqa: E402

P = (1 << 61) - 1
T1 = ['E1.a2', 'E1.b1', 'E1.d1']
T3 = ['E3.h1', 'E3.g1', 'E3.f1', 'E3.e2']


def rank(rows, ncols):
    rows = [r[:] for r in rows]
    rk = 0
    col = 0
    nr = len(rows)
    while rk < nr and col < ncols:
        piv = None
        for i in range(rk, nr):
            if rows[i][col] % P:
                piv = i
                break
        if piv is None:
            col += 1
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        inv = pow(rows[rk][col], P - 2, P)
        rows[rk] = [(x * inv) % P for x in rows[rk]]
        for i in range(nr):
            if i != rk and rows[i][col]:
                f = rows[i][col]
                rows[i] = [(a - f * b) % P for a, b in zip(rows[i], rows[rk])]
        rk += 1
        col += 1
    return rk


def main():
    rng = random.Random(61)
    out = []
    for w14free in (False, True):
        for counter in (0, 1, 2):
            eqs, words = model.system(counter, w14free)
            words = sorted(words)
            idx = {w: i for i, w in enumerate(words)}
            n = len(words)
            A = []
            for _, ws in eqs:
                r = [0] * n
                for w in ws:
                    r[idx[w]] = rng.randrange(1, P)
                A.append(r)

            def unit(ts):
                rr = []
                for t in ts:
                    r = [0] * n
                    r[idx[t]] = 1
                    rr.append(r)
                return rr
            rA = rank(A, n)
            dimS = n - rA
            r1 = rank(A + unit(T1), n) - rA
            r3 = rank(A + unit(T3), n) - rA
            r13 = rank(A + unit(T1) + unit(T3), n) - rA
            fib3 = n - rank(A + unit(T3), n)          # dim of {s in S : T3 fixed}
            k1_on_fib3 = rank(A + unit(T3) + unit(T1), n) - rank(A + unit(T3), n)
            fib1 = n - rank(A + unit(T1), n)
            k3_on_fib1 = rank(A + unit(T1) + unit(T3), n) - rank(A + unit(T1), n)
            line = ('counter=%d %s: words %d eqs %d rank %d dimS %d | rank T1 %d, T3 %d, (T1,T3) %d | '
                    'E3-fixed fibre dim %d, T1 rank on it %d | E1-fixed fibre dim %d, T3 rank on it %d'
                    % (counter, 'w14free' if w14free else 'w14pinned', n, len(eqs), rA, dimS,
                       r1, r3, r13, fib3, k1_on_fib3, fib1, k3_on_fib1))
            print(line, flush=True)
            out.append(line)
    open('generic_rank.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('WROTE generic_rank.txt')


if __name__ == '__main__':
    main()
