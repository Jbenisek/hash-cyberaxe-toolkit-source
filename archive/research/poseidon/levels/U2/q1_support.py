import time, sys
from u2lib import *
t0 = time.time()
for k in (1, 2, 3):
    L, D = lanes_after(k)
    print(f"R{k}: (A,B) degree {D}; support in (A,B) per lane:", [support_AB(x) for x in L], f"[triangle {(D+1)*(D+2)//2}]", f"t={time.time()-t0:.1f}s", flush=True)
    U = 5 * D
    law = law_set(D, U)
    for lane in range(3):
        R = expand_nk_rho(L[lane][:D+1, :D+1], D)
        nz = {(u, v) for u in range(U+1) for v in range(U+1) if R[u, v] != 0}
        tri = (U+1)*(U+2)//2
        outside = nz - law; missing = law - nz
        zero_in_tri = sum(1 for u in range(U+1) for v in range(U+1-u) if R[u, v] == 0)
        print(f"  lane {lane}: nonzero monomials = {len(nz)} ; law set size = {len(law)} ; nonzero outside law = {len(outside)} ; law monomials that are zero = {len(missing)} ; triangle (deg<={U}) size {tri}, zero coefficients inside triangle {zero_in_tri} ; max total degree seen {max(u+v for u,v in nz)} ; t={time.time()-t0:.1f}s", flush=True)
        if missing: print("    first missing:", sorted(missing)[:8])
        if outside: print("    first outside:", sorted(outside)[:8])
