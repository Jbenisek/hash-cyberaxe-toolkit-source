import sys, importlib.util
sys.argv=['x']
spec=importlib.util.spec_from_file_location('lm','lowm_final.py'); lm=importlib.util.module_from_spec(spec); spec.loader.exec_module(lm)
rows=[l.split() for l in open('disc2.out')]
d={int(r[0],16):(int(r[1]),int(r[2],16),int(r[3],16)) for r in rows}
cl={c[0]:c for c in lm.CLASSES}
print(len(d),len(cl),set(d)==set(cl), len(lm.CLASSES))
bad=0
for c7,(n,first,orx) in d.items():
    C=cl[c7]; bad+= n!=C[3] or ((first^C[1])&~C[2]&0xffffffff)!=0 or (orx&~C[2])!=0
print('mismatch',bad, sum(v[0] for v in d.values()))
