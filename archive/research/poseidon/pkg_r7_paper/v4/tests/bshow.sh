export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
yukon benchmark show --json ac95110a-2f91-4f59-b4e2-03249e19fc2d 2>&1 | python3 -c "
import sys,json
s=sys.stdin.read(); i=s.find('{')
d=json.loads(s[i:])
def walk(o,path=''):
    if isinstance(o,dict):
        for k,v in o.items():
            if k in('acceptedRoundCounts','status','closesAt','bestScore'): print(path+'/'+k, str(v)[:200])
            walk(v,path+'/'+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,path+'[%d]'%i)
walk(d)
" | head -20
