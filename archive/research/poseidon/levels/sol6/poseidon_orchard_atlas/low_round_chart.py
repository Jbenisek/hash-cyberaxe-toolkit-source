"""Exact algebraic coordinate audit of only the proposed 1/2-round prefixes.
Creates coefficients and verifies evaluation identities. Does not implement a
collision-search engine or extrapolate to full deployed Orchard Poseidon.
"""
import csv,json,random,math,time
from pathlib import Path
from poseidon_core import *
B=Path(__file__).resolve().parent;D=B/'data'
rc,m,mi=parameters();rng=random.Random(202610122036)
Z=pow((CAP+rc[0][2])%P,5,P)
k=[(m[j][2]*Z+rc[1][j])%P for j in range(3)]
coef={}
for i in range(6):
 for j in range(6-i):
    h=5-i-j;n=math.factorial(5)//(math.factorial(i)*math.factorial(j)*math.factorial(h))
    coef[i,j]=sum(m[0][a]*n*pow(m[a][0],i,P)*pow(m[a][1],j,P)*pow(k[a],h,P) for a in range(3))%P
assert coef[5,0] and coef[0,5]
def peval(x,y):return sum(v*pow(x,i,P)*pow(y,j,P) for (i,j),v in coef.items())%P
for _ in range(2048):
    a,b=rng.randrange(P),rng.randrange(P)
    x=pow((a+rc[0][0])%P,5,P);y=pow((b+rc[0][1])%P,5,P)
    s1=permutation([a,b,CAP],1)
    assert mat_vec(mi,s1)[2]==Z
    assert peval(x,y)==permutation([a,b,CAP],2)[0]
    # Specialized digest-only evaluation with precomputed constants.
    h1=(m[0][0]*x+m[0][1]*y+m[0][2]*Z)%P
    assert h1==s1[0]
    h2=sum(m[0][j]*pow((m[j][0]*x+m[j][1]*y+k[j])%P,5,P) for j in range(3))%P
    assert h2==peval(x,y)
rows=[dict(X_degree=i,Y_degree=j,coefficient_hex=f'{v:064x}',nonzero=bool(v)) for (i,j),v in sorted(coef.items())]
with (D/'two_round_quintic_coefficients.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
results=dict(source='derived from the exact pinned first two full rounds',tests=2048,one_round_plane_normal=[hex(x) for x in mi[2]],one_round_plane_constant=hex(Z),one_round_per_digest_preimages=str(P),one_round_distinct_ordered_pair_probability=f'1/{P+1}',two_round_degree_in_transformed_coordinates=5,coefficient_count=21,nonzero_coefficient_count=sum(bool(x) for x in coef.values()),leading_Y5=hex(coef[0,5]),leading_X5=hex(coef[5,0]),two_round_fixed_X_target_roots_max=5,two_round_all_digest_mean_preimages=str(P),exact_two_round_full_fibre_counts='OPEN',coordinate_conversion='X=(m0+c00)^5, Y=(m1+c01)^5; inverse uses exponent d=5^-1 mod(p-1)',optimized_digest_only_field_ops={'r1':{'online_additions':4,'online_multiplications':8,'total':12,'one_time_precomputation_ops':5},'r2':{'online_additions':10,'online_multiplications':24,'total':34,'one_time_precomputation_ops':10}},pricing_scope='field arithmetic only; excludes loads, serialization, loop/control, and contest qualification; not submitted scores')
(D/'low_round_chart_results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
