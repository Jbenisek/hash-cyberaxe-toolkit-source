"""Replayable finite, local structural audits. No autonomous collision attack loop.
Run: python analyze.py. Outputs CSV/JSON for a row-interaction research atlas.
"""
from __future__ import annotations
import csv,json,math,time,random,hashlib,itertools,platform,os
from pathlib import Path
from collections import Counter,defaultdict
from poseidon_core import *
B=Path(__file__).resolve().parent
D=B/'data';D.mkdir(exist_ok=True)
R=random.Random(202610122035)
RC,M,MI=parameters()
STATS={}

def dump(name,ob):
    (D/name).write_text(json.dumps(ob,indent=2)+'\n')
def csvout(name,rows):
    if not rows:return
    with (D/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def det(a):
    if len(a)==1:return a[0][0]%P
    return sum((-1)**j*a[0][j]*det([r[:j]+r[j+1:] for r in a[1:]]) for j in range(len(a)))%P

def sub(x,y):return [(a-b)%P for a,b in zip(x,y)]
def add(x,y):return [(a+b)%P for a,b in zip(x,y)]
def scalar(a,x):return [a*t%P for t in x]

def independent_step(s,i):
    a,b,c=[(s[j]+RC[i][j])%P for j in range(3)]
    def s5(x):
        z=x*x%P;return (z*z%P)*x%P
    a=s5(a)
    if full(i):b,c=s5(b),s5(c)
    return [(M[j][0]*a+M[j][1]*b+M[j][2]*c)%P for j in range(3)]

# Reference/vector/domain verification.
t0=time.process_time();vector_rows=[]
for kind,file in [('hash','official_hash_vectors.json'),('permutation','official_permutation_vectors.json')]:
    for i,v in enumerate(json.loads((B/'source'/file).read_text())):
        if kind=='hash': actual=digest(bytes.fromhex(''.join(v['input']))).hex(); ok=actual==v['output']
        else:
            actual=permutation([int.from_bytes(bytes.fromhex(z),'little') for z in v['initial_state']])
            ok=actual==[int.from_bytes(bytes.fromhex(z),'little') for z in v['final_state']]
        assert ok;vector_rows.append(dict(kind=kind,index=i,result='PASS'))
STATS['official_vector_checks']=len(vector_rows)
for j in range(64):
    for k in range(16):
        s=[R.randrange(P) for _ in range(3)];y=step(s,j)
        assert y==independent_step(s,j)
        assert backstep(y,j)==s
STATS['native_round_inverse_tests']=64*16
STATS['native_independent_round_tests']=64*16
bad=[]
for n in [0,1,31,32,33,63,65,96,128]:bad.append(bytes(n))
for x in [P,P+1,2**256-1]:
    bad += [x.to_bytes(32,'little')+(1).to_bytes(32,'little'), (1).to_bytes(32,'little')+x.to_bytes(32,'little')]
for msg in bad:
    try:decode(msg)
    except ValueError:pass
    else:raise AssertionError('domain check missed')
STATS['invalid_encoding_cases']=len(bad)
# Mutated parameters are negative controls, not substitutions for the target.
base=permutation([0,1,2]);m_bad=[r[:] for r in M];m_bad[0][0]=(m_bad[0][0]+1)%P
r_bad=[r[:] for r in RC];r_bad[0][0]=(r_bad[0][0]+1)%P
for par in [(r_bad,M,MI),(RC,m_bad,MI)]:
    s=[0,1,2]
    for i in range(64):s=step(s,i,par)
    assert s!=base
assert digest(encode(0,1))!=permutation([0,1,0])[0].to_bytes(32,'little')
STATS['negative_controls']=3
STATS['reference_checks_cpu_seconds']=time.process_time()-t0
csvout('reference_checks.csv',vector_rows)

# Exact finite-field linear algebra.
minor_rows=[]
for size in range(1,4):
 for rr in itertools.combinations(range(3),size):
  for cc in itertools.combinations(range(3),size):
   z=det([[M[i][j] for j in cc] for i in rr]);assert z
   minor_rows.append(dict(rows=','.join(map(str,rr)),columns=','.join(map(str,cc)),size=size,determinant_hex=f'{z:064x}',nonzero=True))
assert mat_mul(M,MI)==[[int(i==j) for j in range(3)] for i in range(3)]
O=[[1,0,0],M[0][:],mat_mul(M,M)[0]]
oi=inverse_matrix(O)
# basis silent through two successive partial-round S-boxes, before their MDS.
v2=[0,M[0][2],-M[0][1]%P]
assert mat_vec([O[0],O[1]],v2)==[0,0]
assert sum(O[2][j]*v2[j] for j in range(3))%P!=0
cert=dict(modulus=str(P),modulus_hex=hex(P),exponent=5,inverse_exponent=str(ROOT5),gcd_exponent=math.gcd(5,P-1),MDS=[[hex(x) for x in r] for r in M],MDS_inverse=[[hex(x) for x in r] for r in MI],MDS_minor_count=len(minor_rows),MDS_determinant=hex(det(M)),branch_number=4,observability=[[hex(x) for x in r] for r in O],observability_inverse=[[hex(x) for x in r] for r in oi],observability_determinant=hex(det(O)),silent_ranks=[rank(O[:k]) for k in range(4)],silent_dimensions=[3-rank(O[:k]) for k in range(4)],two_round_silent_basis=[hex(x) for x in v2])
csvout('mds_minors.csv',minor_rows)
dump('linear_certificates.json',cert)

# An exact 3-active-coordinate chart for every all-partial length-3 window.
v=[M[i][0] for i in range(3)]
e0=[1,0,0]
def nonlinear(q):return (pow(q,5,P)-q)%P

def reconstruct_active(start,q):
    b0=mat_vec(M,RC[start]);b1=mat_vec(M,RC[start+1])
    n0=nonlinear((q[0]+RC[start][0])%P)
    n1=nonlinear((q[1]+RC[start+1][0])%P)
    k1=(b0[0]+v[0]*n0)%P
    k2=(mat_vec(M,b0)[0]+mat_vec(M,v)[0]*n0+b1[0]+v[0]*n1)%P
    return mat_vec(oi,[q[0],(q[1]-k1)%P,(q[2]-k2)%P])
chart_rows=[]
for start in range(4,58):
    for rep in range(8):
        q=[R.randrange(P) for _ in range(3)]
        s=reconstruct_active(start,q)
        s1=step(s,start);s2=step(s1,start+1)
        assert [s[0],s1[0],s2[0]]==q
        # Exact nonlinear bypass direction, verified on independently selected states.
        d=scalar(R.randrange(1,P),v2);s0b=add(s,d)
        t1=step(s0b,start);t2=step(t1,start+1)
        assert t1[0]==s1[0]
        assert sub(t1,s1)==mat_vec(M,d)
        assert sub(t2,s2)==mat_vec(M,mat_vec(M,d))
        assert t2[0]!=s2[0]
    chart_rows.append(dict(start_round=start,rounds=f'{start},{start+1},{start+2}',matrix_rank=3,all_field_active_triples='p^3',inputs_per_triple=1,native_checks=8,legality='unrestricted internal states; fixed-capacity reachability NOT proved',status='PROVED identity; COMPUTED replay'))
csvout('partial_window_charts.csv',chart_rows)
STATS['partial_chart_checks']=54*8;STATS['two_step_silent_checks']=54*8

# The S-box finite-difference equation reduces to two square-root tests.
def sqrt_mod(a,p=P):
    a%=p
    if a==0:return 0
    if pow(a,(p-1)//2,p)!=1:return None
    if p%4==3:return pow(a,(p+1)//4,p)
    q,s=p-1,0
    while q%2==0:q//=2;s+=1
    z=2
    while pow(z,(p-1)//2,p)!=p-1:z+=1
    c=pow(z,q,p);x=pow(a,(q+1)//2,p);t=pow(a,q,p);m=s
    while t!=1:
        i=1;tmp=t*t%p
        while tmp!=1:tmp=tmp*tmp%p;i+=1
        b=pow(c,1<<(m-i-1),p);x=x*b%p;t=t*b*b%p;c=b*b%p;m=i
    return x

def roots_differential(delta,eta,p=P):
    delta%=p;eta%=p
    if delta==0:
        raise ValueError('delta=0 is p solutions for eta=0; otherwise 0')
    b=eta*pow(pow(delta,5,p),-1,p)%p
    # z=x/delta + 1/2, y=z^2; 80 y^2+40 y+1-16b=0.
    disc=(1280+5120*b)%p;v=sqrt_mod(disc,p)
    if v is None:return []
    out=set()
    for dd in {v,-v%p}:
        y=(-40+dd)*pow(160,-1,p)%p;z=sqrt_mod(y,p)
        if z is not None:
            for zz in {z,-z%p}:out.add(delta*(zz-pow(2,-1,p))%p)
    return sorted(out)

smallp=257;ddt=Counter();toy_checks=0
for a in range(1,smallp):
    brute=defaultdict(list)
    for x in range(smallp):brute[(pow(x+a,5,smallp)-pow(x,5,smallp))%smallp].append(x)
    for b in range(smallp):
        roots=roots_differential(a,b,smallp);assert roots==brute[b]
        ddt[len(roots)]+=1;toy_checks+=1
native_ddt=[]
for i in range(256):
    a=R.randrange(1,P)
    # Half targets have a known root; half are independent targets.
    if i%2:
        x=R.randrange(P);b=(pow(x+a,5,P)-pow(x,5,P))%P
    else:b=R.randrange(P)
    roots=roots_differential(a,b)
    assert len(roots)<=4
    for x in roots:assert (pow(x+a,5,P)-pow(x,5,P))%P==b
    if i%2:assert len(roots)>=1
    native_ddt.append(dict(case=i,delta=hex(a),eta=hex(b),target_type='known-image' if i%2 else 'uniform',exact_preimages=len(roots),roots=';'.join(hex(x) for x in roots)))
csvout('sbox_native_exact_preimages.csv',native_ddt)
dump('sbox_counts.json',dict(toy_prime=smallp,exhaustive_delta_eta_cases=toy_checks,toy_ddt_count_histogram=dict(sorted(ddt.items())),native_cases=len(native_ddt),native_known_image_case_count=128,max_roots=4,all_native_roots_verified=True,zero_difference_for_nonzero_delta_impossible=True))

# Controlled arithmetic/finite-difference row study; legal message perturbations.
N=2048;features=8
round_counts=[dict(round_index=i,samples=N,changed_lane0=0,changed_lane1=0,changed_lane2=0,xor_popcount_sum=0,output_zero_count=0) for i in range(64)]
sig=[[[[0,0] for _ in range(2)] for f in range(features)] for i in range(64)]
# Predeclared binary signatures: four low-bit tests and four simple message classes.
def feature_vec(a,b):return [a&1,b&1,(a>>8)&1,(b>>8)&1,a.bit_count()&1,b.bit_count()&1,(a+b)&1,int(a<b)]
legal_traces=[];t1=time.process_time()
for sample in range(N):
    a,b=R.randrange(P),R.randrange(P);s=[a,b,CAP];t=[(a+1)%P,b,CAP]
    fs=feature_vec(a,b)
    for i in range(64):
        s=step(s,i);t=step(t,i)
        r=round_counts[i]
        for j in range(3):r[f'changed_lane{j}']+=s[j]!=t[j]
        r['xor_popcount_sum']+=sum((s[j]^t[j]).bit_count() for j in range(3))
        r['output_zero_count']+=s[0]==0
        for f,value in enumerate(fs):sig[i][f][value][0]+=1;sig[i][f][value][1]+=s[0]&1
    if sample<8:
        legal_traces.append(dict(message=encode(a,b).hex(),states=[[hex(x) for x in z] for z in permutation([a,b,CAP],trace=True)]))
STATS['legal_message_perturbations']=N;STATS['legal_native_round_transitions']=N*64*2
STATS['legal_native_sampling_cpu_seconds']=time.process_time()-t1
csvout('legal_message_sensitivity.csv',round_counts)
dump('native_trace_examples.json',legal_traces)
sigrows=[]
for i in range(64):
    for f,name in enumerate(['m0 bit0','m1 bit0','m0 bit8','m1 bit8','m0 popcount parity','m1 popcount parity','sum parity','m0 < m1']):
        n0,h0=sig[i][f][0];n1,h1=sig[i][f][1]
        p0=h0/n0;p1=h1/n1;pool=(h0+h1)/(n0+n1)
        se=math.sqrt(pool*(1-pool)*(1/n0+1/n1))
        z=(p1-p0)/se if se else 0.;pv=math.erfc(abs(z)/math.sqrt(2))
        sigrows.append(dict(round_index=i,signature=name,n0=n0,n1=n1,ones0=h0,ones1=h1,rate0=p0,rate1=p1,z=z,two_sided_normal_p=pv,bonferroni_p=min(1.,pv*64*features),status='SAMPLED; output parity only, not collision rate'))
csvout('signature_screen.csv',sigrows)

# Internal interventions: source is BEFORE round i, target is AFTER round j.
# This is not an assumption that those states are legal independently selectable inputs.
REPS=8;grid_acc={};t2=time.process_time()
for i in range(64):
    for lane in range(3):
        acc={j:[0,0,0,0] for j in range(i,64)}
        for rep in range(REPS):
            inp=[R.randrange(P),R.randrange(P),CAP]
            s=inp if i==0 else permutation(inp,i)
            t=s[:];t[lane]=(t[lane]+1)%P
            for j in range(i,64):
                s=step(s,j);t=step(t,j)
                for h in range(3):acc[j][h]+=s[h]!=t[h]
                acc[j][3]+=sum((s[h]^t[h]).bit_count() for h in range(3))
        for j,x in acc.items():grid_acc[i,j,lane]=x
rows=[]
for i in range(64):
    for j in range(64):
        if j<i:
            rows.append(dict(source_before_round=i,target_after_round=j,relation='NO_FORWARD_CAUSAL_PATH',sampled_interventions=0,changed0=None,changed1=None,changed2=None,mean_xor_popcount=None,exact_scope='future interventions do not alter stored past; inverse constraints are separate',bedrock_collision_necessity='OPEN'))
        else:
            a=[sum(grid_acc[i,j,l][k] for l in range(3)) for k in range(4)]
            rows.append(dict(source_before_round=i,target_after_round=j,relation='DIRECT_DENSE' if i==j else 'TRANSITIVE_DENSE',sampled_interventions=REPS*3,changed0=a[0],changed1=a[1],changed2=a[2],mean_xor_popcount=a[3]/(REPS*3),exact_scope='syntactic dependency; internal finite changes sampled; fixed-capacity legality not inferred',bedrock_collision_necessity='OPEN'))
csvout('round_pair_grid.csv',rows)
STATS['forward_grid_cells_sampled']=64*65//2;STATS['backward_noncausal_cells']=64*63//2
STATS['internal_intervention_start_states']=64*3*REPS;STATS['internal_intervention_cpu_seconds']=time.process_time()-t2

# Round-local rank constraints, nonlinear load and arithmetic counts.
rowcards=[];cumadd=cummul=sboxes=0
for i in range(64):
    f=full(i);ns=3 if f else 1;sboxes+=ns;addop=9;mulop=9+3*ns;cumadd+=addop;cummul+=mulop
    rowcards.append(dict(round_index=i,round_number=i+1,zone='leading_full' if i<4 else ('trailing_full' if i>=60 else 'partial'),active_sboxes=ns,sbox_lanes='0,1,2' if f else '0',round_constants=';'.join(f'{x:064x}' for x in RC[i]),input_dependency='all three input lanes; fresh message knobs=0',MDS_rank=3,MDS_branch_number=4,local_inverse='unique for full 3-word state',formal_degree_upper_bound=str(5**(i+1)),field_additions=addop,field_multiplications=mulop,field_ops_total=addop+mulop,cumulative_additions=cumadd,cumulative_multiplications=cummul,cumulative_ops=cumadd+cummul,cumulative_sboxes=sboxes,reachable_states='p^2 from canonical two-field messages',autonomous_input_dof=0,exact_scope='same 64-round deployment constants, prefix cut',status='SOURCE+PROVED structure; measured diagnostic below'))
csvout('round_cards.csv',rowcards)
assert (cumadd,cummul,sboxes)==(576,816,80)
# Field-encoding reference bit frequencies; prevents a false avalanche baseline.
bitrows=[]
for b in range(256):
    q,r=divmod(P,1<<(b+1));ones=q*(1<<b)+max(0,r-(1<<b));prob=ones/P
    bitrows.append(dict(bit=b,ones_count=str(ones),total_field_values=str(P),one_probability=prob,independent_xor_probability=2*prob*(1-prob),status='PROVED exact uniform-field encoding baseline'))
csvout('encoding_bit_baseline.csv',bitrows)

# Benchmark actual pure-Python reference, separate from contest operation units.
bench=[]
for n in [1,2,4,8,32,60,64]:
    x=[7,11,CAP];reps=512;t=time.process_time();wall=time.perf_counter()
    for k in range(reps):permutation(x,n)
    c=time.process_time()-t;w=time.perf_counter()-wall
    bench.append(dict(prefix_rounds=n,iterations=reps,cpu_seconds=c,wall_seconds=w,evals_per_cpu_second=reps/c,reference_field_ops=rowcards[n-1]['cumulative_ops'],language='Python integer modular arithmetic, one process',security_claim='none'))
csvout('benchmark.csv',bench)

STATS.update(dict(seed=202610122035,python=platform.python_version(),platform=platform.platform(),cpu_model=next((l.split(':',1)[1].strip() for l in Path('/proc/cpuinfo').read_text().splitlines() if l.startswith('model name')),'unknown'),nominal_input_space=str(P*P),nominal_output_space=str(P),field_modulus_bits=P.bit_length(),log2_output_space=math.log2(P),generic_birthday_exponent=math.log2(P)/2,round_count=64,field_additions_full=576,field_multiplies_full=816,scope='native checks and toy exhaustive counts; no production collision claim',sbox_toy_exhaustive_cases=toy_checks,significant_signature_tests=sum(x['bonferroni_p']<.05 for x in sigrows),signature_tests=len(sigrows)))
dump('results.json',STATS)
dump('parameters.json',dict(p=str(P),capacity=str(CAP),full_rounds=RF,partial_rounds=RP,round_constants=[[f'{x:064x}' for x in row] for row in RC],MDS=[[f'{x:064x}' for x in row] for row in M],MDS_inverse=[[f'{x:064x}' for x in row] for row in MI]))
print(json.dumps(STATS,indent=2))
