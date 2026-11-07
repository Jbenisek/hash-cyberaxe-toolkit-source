import json
exec(open('testB.py').read().split("res['r0_n2^14']")[0])
res=json.load(open('testB.json'))
for key,args in [('r2_n2^19',(2,0,19)),('r2_n2^18_control',(2,0,18)),('r2_n2^19_line1',(2,1,19))]:
    res[key]=zs(*args); print(key,res[key],flush=True)
json.dump(res,open('testB.json','w'),indent=1)
