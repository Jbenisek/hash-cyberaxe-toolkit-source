import random,math,sys
def mk(q,seed):
    rnd=random.Random(seed*1000003+q)
    while True:
        xs=rnd.sample(range(q),3); ys=rnd.sample(range(q),3)
        if all((x+y)%q for x in xs for y in ys): break
    return [[pow(x+y,-1,q) for y in ys] for x in xs]
def det3(m,q):
    return (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))%q
def d(M,q):
    e0=[1,0,0]
    e1=[sum(e0[k]*M[k][j] for k in range(3))%q for j in range(3)]  # e0 M
    e2=[sum(e1[k]*M[k][j] for k in range(3))%q for j in range(3)]
    return det3([e0,e1,e2],q)
for q in [23,29,37,43]:
    print(q,[(s,d(mk(q,s),q)) for s in range(1,40) if d(mk(q,s),q)==0][:8])
