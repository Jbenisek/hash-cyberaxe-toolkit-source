from grain import *
inv=lambda a:pow(a,P-2,P)
M=pr.MDS
g=G(mk())
for _ in range(192): g.fe()
# no-rejection: 255 bits mod p
raw=[]
for _ in range(12):
    bs=[g.bit() for _ in range(255)]
    raw.append(int(''.join(map(str,bs)),2))
print([hex(v)[:10] for v in raw])
for xs_ in [raw[0:3],raw[3:6]]: pass
for xi in range(0,7):
    xs=[v%P for v in raw[xi:xi+3]]; ys=[v%P for v in raw[xi+3:xi+6]]
    Mm=[[inv((xs[i]+ys[j])%P) for j in range(3)] for i in range(3)]
    print(xi,sum(Mm[i][j]==M[i][j] for i in range(3) for j in range(3)))
