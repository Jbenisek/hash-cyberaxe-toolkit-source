"""Scoped exact structure checks, including the derivative-versus-finite-change trap."""
from pathlib import Path
import csv,json,random,time
from poseidon_core import *
B=Path(__file__).resolve().parent;D=B/'data';rc,m,mi=parameters();r=random.Random(202610122037)
t=time.process_time();out=[]
for i in range(64):
    # Force exactly the active lane-0 S-box input to zero. This is an internal
    # state diagnostic, not a proof that this state is a cheap legal hash input.
    s=[(-rc[i][0])%P,r.randrange(P),r.randrange(P)]
    for j in (1,2):
        if (s[j]+rc[i][j])%P==0:s[j]=(s[j]+1)%P
    diag=[5*pow((s[j]+rc[i][j])%P,4,P)%P if full(i) or j==0 else 1 for j in range(3)]
    jac=[[m[a][b]*diag[b]%P for b in range(3)] for a in range(3)]
    assert rank(jac)==2
    d=r.randrange(1,P);s2=s[:];s2[0]=(s2[0]+d)%P
    x,y=step(s,i),step(s2,i)
    diff=[(y[j]-x[j])%P for j in range(3)]
    expected=[m[j][0]*pow(d,5,P)%P for j in range(3)]
    assert diff==expected and all(diff)
    out.append({'round_index':i,'derivative_rank':2,'derivative_kernel_dim':1,'finite_move_delta':hex(d),'finite_change_in_all_three_outputs':True,'meaning':'zero derivative is NOT an exact neutral finite move','scope':'internal state; not an asserted reachable input','status':'PROVED identity + COMPUTED native replay'})
with (D/'derivative_trap.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
q=257;mm=json.loads((D/'toy_config.json').read_text())['MDS']
import itertools
def det(a,p):
    if len(a)==1:return a[0][0]%p
    return sum((-1)**j*a[0][j]*det([row[:j]+row[j+1:] for row in a[1:]],p) for j in range(len(a)))%p
nm=0
for k in range(1,4):
 for rr in itertools.combinations(range(3),k):
  for cc in itertools.combinations(range(3),k):
   assert det([[mm[a][b] for b in cc] for a in rr],q)!=0;nm+=1
with (D/'toy_full_input_counts.csv').open() as f:
    toy=list(csv.DictReader(f))
for row in toy:
    assert int(row['distinct_full_states'])==q*q
    assert int(row['unordered_collisions'])+int(row['unordered_noncollisions'])==int(row['unordered_pairs'])==q*q*(q*q-1)//2
res={'derivative_trap_native_checks':64,'toy_mds_nonzero_minors':nm,'toy_exact_bookkeeping_rows':64,'partial_chart_legal_active_triples_exact':'p^2','partial_chart_all_active_triples_exact':'p^3','legal_fraction_of_uniform_unrestricted_active_triples_exact':'1/p','proof':'Every prefix is a permutation of Fp^3. The canonical input plane has p^2 elements. The three-active-input partial-window chart is a bijection on Fp^3, so the image of the legal plane has exactly p^2 triples.','cpu_seconds':time.process_time()-t}
(D/'extra_results.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
