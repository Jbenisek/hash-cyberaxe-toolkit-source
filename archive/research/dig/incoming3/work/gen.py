"""write the 72 cell records for blake3-r3-U01..U09 from scan_out.json / scan2_out.json / scan3_out.json"""
import json, os, sys
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.abspath(os.path.join(HERE,".."))
S=json.load(open(os.path.join(HERE,"scan_out.json"))); S2=json.load(open(os.path.join(HERE,"scan2_out.json"))); S3=json.load(open(os.path.join(HERE,"scan3_out.json")))
GC=((0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14))
READER={w:i for i,g in enumerate(GC[4:]) for w in g}
UNITS={"U01":("C0",(1,2)),"U02":("C0",(3,4)),"U03":("C1",(1,2)),"U04":("C1",(3,4)),"U05":("C2",(1,2)),"U06":("C2",(3,4)),"U07":("C3",(1,2)),"U08":("C3",(3,4)),"U09":("D0",(1,2))}
QN={1:"(a1,d1)",2:"(c1,b1)",3:"(a2,d2)",4:"(c2,b2)"}
EV=("research/dig/incoming3/work/b3steps.py; research/dig/incoming3/work/scan.py; research/dig/incoming3/work/scan_out.json; "
    "research/dig/incoming3/work/validate_out.txt; research/blake3_r3/candidate_blake3/experiments/rho.py")
EV2=EV+"; research/dig/incoming3/work/scan2.py; research/dig/incoming3/work/scan2_out.json"
EV3=EV2+"; research/dig/incoming3/work/scan3.py; research/dig/incoming3/work/scan3_out.json"
QTXT={"Q1":"Q1 value/count as used: operations this quarter-step costs in the filed 595-op circuit, and the value it carries.",
 "Q2":"Q2 necessity: change it (no build-time folding / other prefix constants / prefix words free), recount the exact op total.",
 "Q3":"Q3 degrees of freedom: which message words reach this step, how many free bits, and whether any constant choice changes the count.",
 "Q4":"Q4 alternatives: other lane pitch, no immediate merging, other lane counts; recount."}
VALID=("Validation first (research/dig/incoming3/work/validate_out.txt): scalar 7-round digest equals the organizer verifier on 50 random 64-byte blocks and the official empty-input vector; "
       "the packed circuit equals scalar and verifier at 7 rounds (1532 ops) and at 3 rounds (595 ops = the filed count).")
BASE="blake3-r3 filed circuit: 7 lanes x 36 bits, 595 ops/batch, prefix 0^32, m8..m15 free"
def key(c,q): return f"{c}.q{q}"
def writes(call,q):
    return {1:"a,d",2:"c,b",3:"a,d",4:"c,b"}[q]
def words(call,q):
    j=int(call[1]) if call[0]=="C" else None
    a,b,c,d=GC[j] if call[0]=="C" else GC[4]
    return {1:(a,d),2:(c,b),3:(a,d),4:(c,b)}[q]
def final_words(call,q):
    # state words whose FINAL round-0 value is written by this step (a,d final at q3, c,b final at q4)
    w=words(call,q)
    if q==3: return list(w)
    if q==4: return list(w)
    return []
def msgword(call,q):
    j=["C0","C1","C2","C3","D0"].index(call)
    return {1:2*j,3:2*j+1}.get(q)
def rec(unit,call,q,Q,labels,status,number,notes,evidence,held,reopen,topic):
    return {"hash":"blake3-r3","row_i":None,"row_j":None,
     "object":f"R0{call}.q{q} {QN[q]}: 3-round BLAKE3 generic-birthday circuit, round 0 {'column' if call[0]=='C' else 'diagonal'} call {call}, quarter-step {q}",
     "question":QTXT[Q],"labels":labels,"status":status,"number":number,"source":"our workflow: dig-scan-b3r3","own_test":True,
     "evidence":evidence,"date":"2026-10-12","lever":False,"gain_bits":None,"notes":notes,"held_fixed":held,"reopen_if":reopen,"topic":topic,
     "_unit":unit}
cells=[]
for unit,(call,qs) in UNITS.items():
    for q in qs:
        k=key(call,q); loc=f"R0{call}.q{q}"
        bs=S["base_step"][k]; ops=bs[0]; by=bs[1]; vals=S["base_vals"][k]; dep=S["dep"][k]
        unf=S["unfold"][k]; mw=msgword(call,q)
        udep=sorted(set(dep[0])|set(dep[1]))
        pitch_own=[S["pitch"][p]["step"][k] for p in ("33","34","35","36")]
        nm=S["nomerge_step"][k]
        fin=final_words(call,q); readers=sorted({READER[w] for w in fin}) if call[0]=="C" else []
        cid=lambda Q: f"Universe cell blake3-r3|{loc}|step|{Q}."
        topic=f"blake3-r3 {loc} step op count"
        if call[0]=="C":
            # ---- Q1
            num=(f"0 operations (of 595) in the filed circuit; {ops} measured. All inputs are build-time constants (IV, counter 0, length 64, flags 11, message "
                 f"{'word m%d = 0'%mw if mw is not None else 'no message word at this quarter-step'}), so the step folds into immediates. "
                 f"Carried constants ({writes(call,q)}) = {vals[0]}, {vals[1]}; equal to the scalar reference state after this step (20 random x, zero prefix). "
                 f"Round 0 as a whole costs 116 ops, all in D0..D3 (29 each).")
            nt=(cid("Q1")+" "+VALID+" "+("Final round-0 value of word(s) %s, read as an immediate by diagonal call(s) %s."%(",".join("v%d"%w for w in fin),",".join("D%d"%r for r in readers)) if fin else "Intermediate value inside the call; no diagonal call reads it directly."))
            cells.append(rec(unit,call,q,"Q1",["0"],"COMPUTED",num,nt,EV,BASE+"; zero prefix; pitch 36",
              "a different target prefix is not possible (0^32 fixed by blake3-r3-prefix-v1); reopen only if the circuit or the cost model changes",topic))
            # ---- Q2
            num=(f"Demoting this step's constant inputs to run-time registers (no build-time folding from here on): circuit {unf[0]} ops (+{unf[0]-595}), this step itself {unf[1]} ops ({', '.join('%s %d'%(a,b) for a,b in unf[2].items())}). "
                 f"Folding is therefore worth {unf[0]-595} ops per batch. "
                 f"Other prefix constants: step stays {S['rand_step_sets'][k]} ops for 300 random nonzero prefixes, but the circuit total is {S['rand_total_set']} instead of 595 (rounds 1-2 reuse m0..m7; "
                 f"one nonzero word costs +2, all eight +16/17; zero words are skipped). Prefix words free (all 16 variable): circuit {S['allfree_total']}, this step {S['allfree_step'][k]} ops.")
            nt=(cid("Q2")+" Recount by the same tracer with the change applied; the circuit with the change is not run when words are demoted (count only). The prefix is fixed to 0^32 by the target, so the nonzero-prefix and free-prefix rows are what-ifs, not options.")
            cells.append(rec(unit,call,q,"Q2",["N"],"COMPUTED",num,nt,EV2,BASE,
              "a counting rule that charges build-time folding differently (e.g. an organizer rule that charges precomputed immediates)",topic))
            # ---- Q3
            zero_note=""
            if fin:
                zi={0:"v0",5:"v5",10:"v10",15:"v15"}
                hit=[w for w in fin if w in zi]
                if hit:
                    w=hit[0]; nmz={"v0":"v0 via m1","v5":"v5 via m3","v10":"v10 via m5","v15":"v15 via m7"}[zi[w]]
                    zero_note=(f" Zero-immediate construction (closed-form solve of one prefix word so that {zi[w]} = 0, which would delete a D0 immediate op): circuit {S3['totals'][nmz]} ops (net {S3['totals'][nmz]-595:+d}); "
                               f"all four D0 immediates zeroed together: {S3['totals']['all_four_zero']} ops (net +{S3['totals']['all_four_zero']-595}), circuit verified correct. Not available for the target (prefix fixed), and a net loss anyway.")
            num=(f"Reaches this step: message words {udep} (all fixed zeros, 0 free bits); the step's output takes exactly 1 value (constants {vals[0]}, {vals[1]}). "
                 f"Op count over 300 random nonzero prefixes: {S['rand_step_sets'][k]} for this step (invariant); the constant values change nothing in round 0.{zero_note} "
                 f"Score-optimal prefix: the target's own 0^32 (595 ops; any random nonzero prefix 611/612, any single nonzero word 597).")
            nt=cid("Q3")+" Degrees of freedom were taken from data flow (taint sets through the scalar structure) and from 300 random prefixes with the same tracer; no degree of freedom exists for this step in the target."
            cells.append(rec(unit,call,q,"Q3",["Z"],"COMPUTED",num,nt,EV3,BASE,
              "a variant target with a free or chosen prefix (not blake3-r3-prefix-v1)",topic))
            # ---- Q4
            num=(f"Alternatives, this step / circuit total: pitch 33: {pitch_own[0]}/{S['pitch']['33']['total']}; 34: {pitch_own[1]}/{S['pitch']['34']['total']}; 35: {pitch_own[2]}/{S['pitch']['35']['total']}; 36 (filed): {pitch_own[3]}/{S['pitch']['36']['total']} ops (7 lanes each). "
                 f"No immediate merging (one op per constant operand): this step {nm}, circuit {S['nomerge_total']} (merging saves {S['nomerge_total']-595}). "
                 f"8 lanes at pitch 32 has no guard bit and is not modelled by this tracer (OPEN). Best alternative equals the filed circuit; no saving.")
            nt=cid("Q4")+" Alternatives re-traced with the same Tracer (pitch/lane parameters) and a no-merge add rule; every variant circuit with guard bits checked only for count except the filed pitch 36 (checked correct)."
            cells.append(rec(unit,call,q,"Q4",["Z"],"COMPUTED",num,nt,EV,BASE,
              "a lane layout with 8+ lanes or a cheaper rotation form is shown correct and cheaper per instance (595/7 = 85 ops/instance)",topic))
        else:
            kinds=", ".join("%s %d"%(a,b) for a,b in by.items())
            if q==1:
                desc=("add: (v0+v5 merged into one immediate K = %s) + m8, xor: v15 immediate ^ a1, ror16 = shr, and, shl, and, or"%S["zero"]["K_D0q1"])
            else:
                desc=("add: v10 immediate + d1 (variable), xor: v5 immediate ^ c1, ror12 = shr, and, shl, and, or")
            num=(f"{ops} operations per 7-lane batch ({kinds}) = {100*ops/595:.2f} percent of the 595; D0 total 29 (7+7+8+7). {desc}. "
                 f"Outputs are variable (depend on m8{'' if q==1 else ' through d1'}); lane bound after the step 2^32 (masked by the rotation). Immediates after the columns: v0 {S['zero']['v0_after_cols']}, v5 {S['zero']['v5_after_cols']}, v10 {S['zero']['v10_after_cols']}, v15 {S['zero']['v15_after_cols']}.")
            nt=cid("Q1")+" "+VALID+" Counts from the per-quarter-step accounting of the same Tracer; the immediates equal the scalar state after the four column calls."
            cells.append(rec(unit,call,q,"Q1",["N"],"COMPUTED",num,nt,EV,BASE,"the cost model charges immediates or rotations differently",topic))
            num=(f"Demoting this step's constant inputs to run-time registers: circuit {unf[0]} ops ({unf[0]-595:+d}), step {unf[1]} ({', '.join('%s %d'%(a,b) for a,b in unf[2].items())}). "
                 f"Prefix words free: circuit {S['allfree_total']}, step {S['allfree_step'][k]}. Random nonzero prefixes: step stays {S['rand_step_sets'][k]}, circuit {S['rand_total_set']}. "
                 f"Fewer free chain words (m8 pinned, 7 free): circuit {S2['fewer_free']['7']} ops (-18) but the chain domain falls to 2^224 < 2^256, so the memoryless rho no longer returns a full-digest collision cheaply "
                 f"(structural argument, not a tested cost; a 224-bit rho gives only truncated collisions, 2^32 of them needed).")
            nt=cid("Q2")+" Recount with the same tracer. The 577 figure counts operations only; the domain argument is structural and was not run as a search."
            cells.append(rec(unit,call,q,"Q2",["N"],"COMPUTED",num,nt,EV2,BASE,"a non-rho collision method that needs fewer than 8 free chain words",topic))
            im={1:"K = v0+v5 (add) and v15 (xor)",2:"v10 (add) and v5 (xor)"}[q]
            zt=S3["totals"]
            num=(f"Reaches this step: message words {udep}; one of them is free (m8 = 32 free bits); the other words are fixed zeros. "
                 f"The step is a bijection in m8: {S2['inject_sample']['N']} distinct m8 values gave {S2['inject_sample']['distinct_q1' if q==1 else 'distinct_q2']} distinct outputs (structural: add, xor and rotate by constants are bijections). "
                 f"Ops invariant over 300 random prefixes: {S['rand_step_sets'][k]}. Zero-immediate constructions for this step's immediates ({im}): closed-form solves of m1/m3/m5/m7 make them vanish "
                 f"(each alone: {zt['v0 via m1']}/{zt['v5 via m3']}/{zt['v10 via m5']}/{zt['v15 via m7']} ops for v0/v5/v10/v15 = 0; all four: {zt['all_four_zero']}, circuit verified correct) - "
                 f"every variant is worse than 595 because a nonzero prefix word costs +2 in rounds 1-2 while deleting one immediate saves 1. Prefix is fixed by the target anyway.")
            nt=cid("Q3")+" Dependency sets from taint propagation; injectivity checked on a 2^20 sample; zero-immediate prefixes solved in closed form (scan3.py) and re-counted."
            cells.append(rec(unit,call,q,"Q3",["I","Z"],"COMPUTED",num,nt,EV3,BASE,"a target with a chosen prefix, or a cost rule that charges nonzero constants less",topic))
            num=(f"Alternatives, this step / circuit total: pitch 33: {pitch_own[0]}/{S['pitch']['33']['total']}; 34: {pitch_own[1]}/{S['pitch']['34']['total']}; 35: {pitch_own[2]}/{S['pitch']['35']['total']}; 36 (filed): {pitch_own[3]}/{S['pitch']['36']['total']} ops. "
                 f"No immediate merging: step {nm}, circuit {S['nomerge_total']} (+{S['nomerge_total']-595}). Earlier counter swar_count.py gives 612 for the circuit. 8 lanes at pitch 32 not modelled (no guard bit; OPEN). No variant beats the filed step.")
            nt=cid("Q4")+" Same tracer with pitch/lane and merge parameters; only the filed pitch-36 circuit was executed and checked."
            cells.append(rec(unit,call,q,"Q4",["Z"],"COMPUTED",num,nt,EV,BASE,"an 8-lane or cheaper-rotation layout shown correct",topic))
n=0
for c in cells:
    unit="blake3-r3-"+c.pop("_unit")
    # cell id from object/loc
    loc=c["object"].split(" ")[0]; Q=c["question"][:2]
    cid=f"blake3-r3|{loc}|step|{Q}"
    d=os.path.join(OUT,unit); os.makedirs(d,exist_ok=True)
    json.dump(c,open(os.path.join(d,cid.replace("|","_")+".json"),"w"),indent=1)
    n+=1
print("wrote",n)
