from common import *
import random
random.seed(1)
used=[0,1,2,3,4,5,60,61,62,63]
def report(name,vals,labels=None):
    t=time.time()
    rel=lll_relations(vals)
    k=len(vals)
    if not rel: print(f'{name}: k={k} no zero-last-coord vector (W too small?)'); return
    n=norm(rel[0])
    print(f'{name}: k={k} shortest relation norm 2^{l2(n):.2f}  GH(expected) 2^{l2(gh(k)):.2f}  ratio {n/gh(k):.2f}  max|coef| 2^{l2(max(abs(x) for x in rel[0])):.1f}  ({time.time()-t:.1f}s)')
    return rel
# sanity: planted relation
def planted():
    v=[random.randrange(P) for _ in range(12)]
    v.append((3*v[0]-7*v[5]+2*v[9])%P)  # 13th = planted
    r=lll_relations(v)
    print('PLANTED relation test (3,-7,2 + -1): found',r[0],'norm',norm(r[0]))
planted()
print('--- calibration: random elements of F_p')
for k in (6,10,20,30,40):
    report(f'random k={k}',[random.randrange(P) for _ in range(k)])
print('--- real: per-round triple + 1')
for r in range(64):
    if r in used:
        report(f'R{r} lanes+1',list(RC[r])+[1])
print('--- real: 10 used rounds x 3 = 30 constants')
flat=[RC[r][l] for r in used for l in range(3)]
report('used30',flat)
report('used30+1+2^65',flat+[1,1<<65])
mds=[M[i][j] for i in range(3) for j in range(3)]
report('MDS9',mds)
report('MDS9+1',mds+[1])
report('used30+MDS9+1+2^65 (41)',flat+mds+[1,1<<65])
print('--- all 192 constants (k=192 too big) -> 4 blocks of 48 via 16-round windows')
for w in range(0,64,16):
    report(f'rounds {w}..{w+15}',[RC[r][l] for r in range(w,w+16) for l in range(3)])
print('--- lane columns across used rounds')
for l in range(3):
    report(f'lane {l} used rounds',[RC[r][l] for r in used]+[1])
print('--- c0 lanes with 2^65')
report('R0 lanes + 2^65 + 1',list(RC[0])+[1<<65,1])
