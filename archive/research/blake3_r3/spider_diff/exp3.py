import pickle,math
from exp2 import *
rows=pickle.load(open('exp2.pkl','rb'))
cand=[(t[0],t[1]) for t in rows if t[2]>=2**-2.5]
print(len(cand))
out=[]
for w,b in cand:
    p0,p1,p2,pd,n1,n2=analyze({w:1<<b},1<<19)
    out.append((w,b,p0,p1,p2,pd,n1,n2))
    print(w,b,"p0=2^%.1f p1|0=2^%.1f p2|01=2^%.1f n1=%d n2=%d"%(math.log2(p0),math.log2(max(p1,1e-9)),math.log2(max(p2,1e-9)),n1,n2),flush=True)
pickle.dump(out,open('exp3.pkl','wb'))
