import json,sys
sys.path.insert(0,'/home/'+__import__('os').environ.get('USER','x')+'/hashsmash/yukon')
import importlib.util,os
p=os.path.expanduser('~/hashsmash/yukon/hashsmash/verifier/blake3.py')
spec=importlib.util.spec_from_file_location('ob3',p); ob=importlib.util.module_from_spec(spec); spec.loader.exec_module(ob)
cases=json.load(open('cases.json')); mine=json.load(open('mine.json'))
ok=0
for c,mm in zip(cases,mine):
    h,m,tlo,thi,b,d,r=c
    try:
        o=ob._compress(h,m,tlo|(thi<<32),b,d,r)
    except Exception as e:
        print('ERR',e); break
    o=list(o)
    ok+= (o==mm) or (o[:16]==mm) 
print('match',ok,'of',len(cases), 'sample len',len(o))
