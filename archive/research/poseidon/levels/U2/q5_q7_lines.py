"""Q5 + Q7 on the real field: exact line polynomials  nk = a+u t, rho = b+v t  through R1..R3.
   Q7: compare exact top coefficient (t^(5^(k+1))) with the leading-coefficient tracker; count zero coefficients inside the exact polynomials.
   Q5: follow the direction families (roots of the top forms F_{k,j}) and special offsets; record every family, empty ones included."""
import json, time, sys
from u2lib import *
random.seed(11)
D5 = pow(5, -1, P - 1)
t0 = time.time()
def degs(L):
    return [len(x) - 1 for x in L]
def nzcount(poly, deg): return sum(1 for c in poly[:deg + 1] if c)
def report_line(tag, a, b, u, v, kmax=3, show_zero=True):
    L = line_state_R0(a, b, u, v)
    res = []
    for k in range(1, kmax + 1):
        L = line_round(L, k)
        ds = degs(L); tr = tracker(u, v, k)
        top = [(L[i][5**(k+1)] if len(L[i]) > 5**(k+1) else 0) for i in range(3)]
        match = [top[i] == tr[i] for i in range(3)]
        zeros = [5**(k+1) + 1 - sum(1 for c in L[i] if c) - 0 for i in range(3)]   # zero coefficients among exponents 0..5^(k+1)
        res.append((k, ds, match, zeros, L))
        print(f"  {tag} R{k}: degrees {ds} (generic {5**(k+1)}); tracker==exact top coeff {match}; zero coefficients among 0..{5**(k+1)} per lane {zeros}", flush=True)
    return res
print("=== Q7: 20 random lines, tracker vs exact ===")
allmatch = True; totalzero = 0; maxdeg_ok = True
for n in range(20):
    a, b, u, v = [random.randrange(P) for _ in range(4)]
    L = line_state_R0(a, b, u, v)
    for k in range(1, 4):
        L = line_round(L, k)
        tr = tracker(u, v, k)
        for i in range(3):
            top = L[i][5**(k+1)] if len(L[i]) > 5**(k+1) else 0
            if len(L[i]) - 1 != 5**(k+1): maxdeg_ok = False
            if top != tr[i]: allmatch = False
            z = 5**(k+1) + 1 - sum(1 for c in L[i] if c)
            totalzero += z
            if z: print(f"   line {n} R{k} lane {i}: {z} zero coefficients!")
print(f"  20 lines x 3 rounds x 3 lanes = 180 exact polynomials: tracker == exact top coefficient everywhere: {allmatch}; every degree exactly 5^(k+1): {maxdeg_ok}; zero coefficients (exponents 0..deg) in total: {totalzero}; t={time.time()-t0:.1f}s", flush=True)

print("=== Q5: direction families ===")
forms = json.load(open('q2_forms.json'))
fam = {}
for key, info in forms.items():
    for h in info.get('roots', []):
        fam.setdefault(key, []).append(int(h, 16))
print("F_p roots tau=U/V of the top forms:", {k: len(v) for k, v in fam.items()})
print("(R3 lane0: none; R3 lane1: none; R3 lane2: 1; R2 lanes 1,1,2 ... see q2_forms_output.txt)")
for key, rts in fam.items():
    kk = int(key[1]); jj = int(key[-1])
    for tau in rts:
        u = pow(tau, D5, P); v = 1
        assert pow(u, 5, P) == tau
        a, b = random.randrange(P), random.randrange(P)
        print(f"-- direction from root of form {key}: tau={hex(tau)[:14]}..., lane {jj} should lose its top coefficient after round {kk}")
        L = line_state_R0(a, b, u, v)
        for k in range(1, 4):
            L = line_round(L, k)
            print(f"   after R{k}: degrees {degs(L)} (generic {5**(k+1)})   [exact; offsets random]")
        if kk == 0:
            print(f"   after R0 only: degrees {degs(line_state_R0(a,b,u,v))}")
# lines v=0, u=0
for tag, (u, v) in {'v=0 (horizontal)': (1, 0), 'u=0 (vertical)': (0, 1), 'U=V (tau=1)': (1, 1), 'U=-V (tau=-1)': (pow(-1, D5, P), 1)}.items():
    a, b = random.randrange(P), random.randrange(P)
    print(f"-- direction {tag}")
    report_line(tag, a, b, u, v)
# special offsets: line through a point where S-box input of R0 lane 0 is 0 / fixed point
print("-- special offsets (generic direction): sparsity of exact polynomials")
u, v = random.randrange(P), random.randrange(P)
SQ = pow(2, (P - 1) // 4, P)   # find sqrt(-1)
for g in range(2, 50):
    SQ = pow(g, (P - 1) // 4, P)
    if SQ * SQ % P == P - 1: break
offs = {'a=0 (nk=-c00), b random': ((-a0) % P, random.randrange(P)),
        'a=0 and b=0 (through the (0,0) of the S-box inputs)': ((-a0) % P, (-b0) % P),
        'a=1,b=1 (fixed-point inputs)': ((1 - a0) % P, (1 - b0) % P),
        'a=i,b=-i': ((SQ - a0) % P, (-SQ - b0) % P)}
for tag, (a, b) in offs.items():
    print(f"  offset {tag}")
    L = line_state_R0(a, b, u, v)
    for k in range(1, 4):
        L = line_round(L, k)
        ds = degs(L)
        nzs = [sum(1 for c in L[i] if c) for i in range(3)]
        resid = [sorted({e % 5 for e, c in enumerate(L[i]) if c}) for i in range(3)]
        print(f"   R{k}: degrees {ds}; nonzero coeffs {nzs} of {5**(k+1)+1}; exponent residues mod 5 present {resid}", flush=True)
print(f"done t={time.time()-t0:.1f}s")
