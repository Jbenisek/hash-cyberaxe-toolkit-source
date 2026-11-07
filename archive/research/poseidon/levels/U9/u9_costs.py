"""U9 Q8: S-box count, multiplication count and degree/monomial count per round (exact bookkeeping, no measurement beyond the ones cited)."""
from u9lib import schedule, kind
def tri(d): return (d+1)*(d+2)//2
def nk_count(N): return 1 + 10*N + 25*N*(N-1)//2
for r in (1, 2):
    print('=== r=%d ===' % r)
    print('round  kind     Sbox(non-const)  mults(S)  mults(M)  cum.mults  AB-degree  nk-degree  #monomials AB(triangle)  #monomials nk(law)  log2(nk-degree)')
    cum = 0; N = 1; tot_s = 0
    for n, idx in enumerate(schedule(r)):
        kd = kind(idx)
        if idx == 0:
            sb, ms, mm = 2, 6, 6   # lane 2 S-box is a constant (precomputed); M column 2 times a constant
            N = 1
        else:
            sb = 3 if kd == 'full' else 1
            ms = 3*sb
            mm = 3 if idx == 63 else 9
            N = 5*N if idx != 0 else N
        cum += ms + mm; tot_s += sb
        nkdeg = 5*N if idx == 0 else 5*N    # nk-degree is 5 x AB-degree
        if idx == 0: nkdeg = 5; Nab = 1
        else: Nab = N
        import math
        print('R%-2d   %-7s  %d                %d         %d         %-4d       %-8d   %-8d   %-22s  %-18s  %.1f' % (idx, kd, sb, ms, mm, cum, Nab, 5*Nab, tri(Nab) if Nab < 10**6 else '%.3e' % tri(Nab), nk_count(Nab) if Nab < 10**6 else '%.3e' % nk_count(Nab), math.log2(5*Nab)))
    print('totals: S-box evaluations on non-constant values: %d ; multiplications %d (naive count with lane-2 constant S-box and full M in R0 and R63: %d) ; degree 5^%d = %d' % (tot_s, cum, cum+3+3+6, len(schedule(r)), 5**len(schedule(r))))
