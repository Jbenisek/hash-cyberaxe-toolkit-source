import json, time
from eng import *
def nnz(f):
    return sum(1 for c in f.coeffs() if int(c) != 0)
out = {}
for j in range(3):
    a,b,U0,V0,d,base = setup(MDS, round_opts(0,{}), j)
    xj = (MDS[j][0]*U0 + MDS[j][1]*V0 + base[j]) % P
    rec = {'d': [hex(x) for x in d], 'xj': hex(xj), 'd_nonzero': [x != 0 for x in d]}
    st = [PC(pow(xj,5,P)) if i==j else PC(pow(d[i],5,P))*Wp for i in range(3)]
    st = mat_apply(MDS, st)
    rec['after_R1'] = [dict(deg=f.degree(), nnz=nnz(f), c0_nonzero=int(f[0])!=0) for f in st]
    for idx in [2,3,4,60,61,62,63]:
        o = round_opts(idx, {})
        st = [st[i] + RC[idx][i] for i in range(3)]
        rec['R%d_sbox_in'%idx] = [dict(deg=f.degree(), nnz=nnz(f)) for f in st]
        st = [p5(st[i]) if o['sb'][i] else st[i] for i in range(3)]
        st = mat_apply(MDS, st)
        rec['R%d_after_M'%idx] = [dict(deg=f.degree(), nnz=nnz(f)) for f in st]
    out[j] = rec
    print(j, 'done', flush=True)
json.dump(out, open('support.json','w'), indent=1)
