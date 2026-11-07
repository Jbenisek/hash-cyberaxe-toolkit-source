from b3ctr import *
R=random.Random(7)
ok=0;N=2000;pin=0;dig=0;xeq=0
for _ in range(N):
    f=rnd_free(R); w,t,_=build(f)
    wa,wb=messages(w,t)
    oa,Xa,Va=comp(wa,t,55,trace=True); ob,Xb,Vb=comp(wb,t,63,trace=True)
    if (Xa[3],Xa[7],Xa[11],Xa[15])==(X3,X7,X11,X15): pin+=1
    if Xa==Xb: xeq+=1
    if all(oa[i]==ob[i] for i in (0,2,5,7)): dig+=1
print("N",N,"pinned X ok",pin,"X equal A/B",xeq,"digest words 0,2,5,7 equal",dig)
