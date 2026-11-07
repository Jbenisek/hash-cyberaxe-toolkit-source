import json,sys
d=json.load(open(sys.argv[1])); lane=sys.argv[2]; n=int(sys.argv[3])
for k,(c,e) in sorted(d['cells'].items()):
    l,s=k.split('|')
    if l==lane and s.count(',')+1==n and (e>=1 and abs(c-e)>4*e**.5 or e<1 and c>=2 or (c==0 and e>20)): print(s,c,round(e,2))
