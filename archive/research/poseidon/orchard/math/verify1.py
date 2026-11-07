from attack import *
random.seed(20261012)
out = []
def P(*a):
    print(*a); out.append(' '.join(str(x) for x in a))
P('p =', hex(p)); P('K = (2^65+c0[2])^5 =', hex(K))
# minors of MDS (cols 0,1) nonzero?
for j in range(3):
    I=[k for k in range(3) if k!=j]
    det=(MDS[I[0]][0]*MDS[I[1]][1]-MDS[I[0]][1]*MDS[I[1]][0])%p
    P('j',j,'2x2 minor rows',I,'cols 0,1 nonzero:',det!=0)
for j in range(3):
    L = Line(j)
    P('--- j =', j, 'I =', L.I)
    P(' Q=(U,V)', hex(L.UQ), hex(L.VQ))
    P(' direction (a,b)', hex(L.a), hex(L.b))
    P(' d =', [hex(x) for x in L.d], ' d_j==0:', L.d[j]==0, ' other d nonzero:', all(L.d[k]!=0 for k in L.I))
    P(' x(Q) =', [hex(x) for x in L.xQ], ' x_i(Q)==0 for i!=j:', all(L.xQ[k]==0 for k in L.I), ' x_j(Q) nonzero', L.xQ[j]!=0)
    good = 0
    for t in range(20):
        tau = random.randrange(1, p)
        nk, rho = L.inputs(tau)
        assert 0 <= nk < p and 0 <= rho < p
        W = pow(tau, 5, p)
        # genuine run of rounds 0 and 1
        s = [nk, rho, CAP]
        s = rnd(s, 0, True)                         # full round 0
        x = [(s[k] + RC[1][k]) % p for k in range(3)]  # round-1 S-box input
        U, V = L.UV(tau)
        assert pow((nk + RC[0][0]) % p, 5, p) == U and pow((rho + RC[0][1]) % p, 5, p) == V
        assert x[j] == L.xQ[j]
        assert all(x[k] == (L.d[k] * tau) % p for k in L.I)
        y = [pow(v, 5, p) for v in x]
        assert y == L.state_after_r1_sbox(W), 'affine in W failed'
        # full genuine digests for r=0,1,2
        for r in (0, 1, 2):
            assert digest(nk, rho, r) == L.F(W, r), ('digest mismatch', r)
        good += 1
    P(' random tau checked (exact equality, canonical nk,rho, digest r=0,1,2 = F(tau^5)):', good, '/ 20')
    # round-2 inputs affine in W : l_k = alpha_k + beta_k W
    alpha = mds(L.v0); beta = mds(L.v1)
    alpha = [(alpha[k] + RC[2][k]) % p for k in range(3)]
    P(' round-2 S-box input l_k(W)=alpha_k+beta_k*W; beta_k nonzero:', [b != 0 for b in beta])
    roots = [(-alpha[k] * pow(beta[k], -1, p)) % p for k in range(3)]
    P(' zero of l_k pairwise equal? ', [(roots[a] == roots[b]) for a, b in ((0, 1), (0, 2), (1, 2))])
open('verify1_out.txt', 'w').write('\n'.join(out))
