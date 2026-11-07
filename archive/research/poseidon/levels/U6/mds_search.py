from grain import *
inv=lambda a:pow(a,P-2,P)
M=pr.MDS
N=[[inv(M[i][j]) for j in range(3)] for i in range(3)]
# x_i - x_0 = N[i][j]-N[0][j]; y_j-y_0 = N[i][j]-N[i][0]
dx=[0]+[(N[i][0]-N[0][0])%P for i in (1,2)]
dy=[0]+[(N[0][j]-N[0][0])%P for j in (1,2)]
print('dx',[hex(v) for v in dx]);print('dy',[hex(v) for v in dy])
g=G(mk()); 
for _ in range(192): g.fe()
seq=[g.fe()[0] for _ in range(40)]
diffs=set()
for i,a in enumerate(seq):
    for j,b in enumerate(seq):
        if i!=j: diffs.add((b-a)%P)
for name,v in (('dx1',dx[1]),('dx2',dx[2]),('dy1',dy[1]),('dy2',dy[2])):
    for sgn in (1,-1):
        if (sgn*v)%P in diffs: print('found',name,sgn)
# explicit pair positions
for i,a in enumerate(seq):
    for j,b in enumerate(seq):
        if (b-a)%P in (dx[1],dx[2],dy[1],dy[2]): print('pair',i,j,'diff',hex((b-a)%P))
print('first 8 stream after RC:',[hex(v)[:12] for v in seq[:8]])
