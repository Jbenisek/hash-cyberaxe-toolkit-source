# exact dependency table: where does each round-0 message word get read in round 1 (PERM), per cancel channel
PERM=(2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8)
names=['C0','C1','C2','C3','E0','E1','E2','E3']
def where(m):
    i=PERM.index(m); return names[i//2]+('.x' if i%2==0 else '.y')
ch={'t_lo(K0: m0,m1)':(0,1),'t_hi(K1: m2,m3)':(2,3),'b(K2: m4,m5)':(4,5),'flags(K3: m6,m7)':(6,7)}
for k,(x,y) in ch.items(): print(k,'->',where(x),where(y))
for k in range(4): print('h%d a-slot diff, cancelled by m%d alone ->'%(k,2*k),where(2*k))
