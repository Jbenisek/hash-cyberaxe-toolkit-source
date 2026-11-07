import itertools, random
import swar_count as S
best=[]
res={}
for F in itertools.combinations(range(16),8):
    m,ok=S.run(36,3,set(F))
    res[F]=(m.ops,ok)
    assert ok
xs=sorted(res.items(), key=lambda kv: kv[1][0])
print("best 8 subsets:")
for F,(o,ok) in xs[:8]: print(F,o,o/7)
print("worst:",xs[-1])
print("m8..m15:",res[tuple(range(8,16))])
