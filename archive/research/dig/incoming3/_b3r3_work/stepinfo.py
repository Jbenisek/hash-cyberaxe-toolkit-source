import sys,json; sys.path.insert(0,'.')
import b3core as B
from b3core import *
import q3_plan as P
tr=B.Tr()
v=[('c',w) for w in IV]+[('c',w) for w in IV[:4]]+[('c',0),('c',0),('c',64),('c',11)]
m=[('c',0)]*8+[('v','i%d'%i,M32) for i in range(8,16)]
midx=list(range(16)); info={}
def bs(x): return 'const' if x[0]=='c' else round(x[2]/2**32,3)
for rd in range(3):
    for j,(a,b,c,d) in enumerate(GC):
        xi,yi=midx[2*j],midx[2*j+1]; x,y=m[2*j],m[2*j+1]
        steps=[]
        n0=len(tr.prog)
        tr.tag=(rd,j,1); ia=[bs(v[a]),bs(v[b]),bs(x)]; vin=[v[a],v[b],x]
        v[a]=tr.add(v[a],v[b],x); v[d]=tr.ror(tr.xor(v[d],v[a]),16)
        o1=len(tr.prog)
        tr.tag=(rd,j,2); ic=[bs(v[c]),bs(v[d])]; v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),12)
        o2=len(tr.prog)
        tr.tag=(rd,j,3); ia3=[bs(v[a]),bs(v[b]),bs(y)]; v[a]=tr.add(v[a],v[b],y); v[d]=tr.ror(tr.xor(v[d],v[a]),8)
        o3=len(tr.prog)
        tr.tag=(rd,j,4); ic4=[bs(v[c]),bs(v[d])]; v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),7)
        o4=len(tr.prog)
        if rd==2:
            name='R2%s%d'%('C' if j<4 else 'D',j%4)
            info[name]=dict(q1=dict(msg_word=xi,msg_const_zero=(x[0]=='c'),a_in=ia,ops=o1-n0),q2=dict(c_in=ic,ops=o2-o1),
                            q3=dict(msg_word=yi,msg_const_zero=(y[0]=='c'),a_in=ia3,ops=o3-o2),q4=dict(c_in=ic4,ops=o4-o3),
                            a_out=bs(v[a]),c_out=bs(v[c]),first_op=n0,last_op=o4-1)
    m=[m[i] for i in B.PERM]; midx=[midx[i] for i in B.PERM]
json.dump(info,open('stepinfo.json','w'),indent=0)
for k in ('R2C2','R2C3','R2D0','R2D1','R2D2'): print(k,json.dumps(info[k]))
