import pickle, math, json, re, time
import a0lean38 as A
lg = math.log2
cal = pickle.load(open('cal.pkl','rb'))
rows, info = A.ledger(cal=cal, show=False)
N = sum(int(v) for _, v in rows); T0 = lg(N/2728)
parts, B0 = A.memory(cal)
print('KAT T0', T0, 'B0', B0, lg(B0))
assert abs(T0-87.90373595441501) < 1e-9 and B0 == 1045792
S = lambda t, b: t + max(0, lg(b)-20)
terms = A.pre_terms(); print(terms)
PRE = sum(v for _, v in terms)
worst = int(re.search(r'x (\d+) operations', terms[0][0]).group(1))
v = [bin(c[2]).count('1') for c in A.CLASSES]
cands = sum(2**x for x in v); cand_max = 2**max(v)
print('cands', cands, 'max', cand_max, 'v range', min(v), max(v), 'worst member op', worst)
# generator DAG sizes
gen = {}
for g in sorted(cal['prog']):
    sh, cb = A.shape_of(g); t0 = time.time()
    P, ok = A.build_e16(A.CLASSES[A.GRP.index(g)][2], cb, sh)
    nn = len(P.nodes); ins, res = P.schedule([ok])
    gen[g] = dict(nodes=nn, instrs=len(ins), spill_slots=None)
    print(g, nn, len(ins), time.time()-t0)
json.dump(dict(T0=T0, B0=B0, PRE=PRE, terms=[(a, int(b)) for a, b in terms], cands=cands, cand_max=cand_max, v=v, worst=worst, gen=gen, N=N), open('base.json','w'), default=str)
