# U8: toy cubic Frobenius re-check (fixes the omega label in exp2 toy output)
for q in (1000003, 86017, 147457, 270337, 331777):
    cubes=set(pow(v,3,q) for v in range(1,q)) if q<400000 else None
    if cubes is None: continue
    a=next(a for a in range(2,q) if a not in cubes)
    fr=pow(a,(q-1)//3,q)
    om=fr; ok=pow(om,3,q)==1 and om!=1
    # roots of x^3-a in F_q: none
    nroots=sum(1 for v in range(q) if pow(v,3,q)==a)
    print(q,"a=",a,"theta^q/theta =",fr,"is a primitive cube root of 1:",ok,"; roots of x^3-a in F_q:",nroots)
