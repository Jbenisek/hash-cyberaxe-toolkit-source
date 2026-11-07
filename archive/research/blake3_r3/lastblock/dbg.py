exec(open("sites.py").read().split("rng=random.Random(5)")[0])
rng=random.Random(5)
h=[rng.getrandbits(32) for _ in range(8)]
b=trace(h,10)
for z in [("add",0),("add",6)]:
    t=trace(h,10,[z])
    print(z,t.ops,b.by,t.by)
    # diff lines
    import difflib
    d=[l for l in difflib.unified_diff(b.lines,t.lines,lineterm="",n=0) if l[0] in "+-" and l[:3] not in("+++","---")]
    print(len(d)); print("\n".join(d[:12]))
