from common import *
random.seed(5)
allc=[RC[r][l] for r in range(64) for l in range(3)]
for desc,coefs in (('3 terms coef<=7',{3:5,50:-7,100:2}),('4 terms coef<=20',{3:17,50:-9,100:20,150:-3}),('2 terms coef 2^10',{10:1000,20:-1023})):
    v=list(allc); v.append(sum(c*allc[i] for i,c in coefs.items())%P)
    r=lll_relations(v)
    print(desc,'-> shortest relation norm 2^%.2f (generic floor 2^5.6), found vector nonzero entries:',[(i,x) for i,x in enumerate(r[0]) if x][:8] if norm(r[0])<64 else 'NOT SEEN',)
