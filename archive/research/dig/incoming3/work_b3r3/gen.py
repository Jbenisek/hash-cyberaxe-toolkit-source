
# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import json, math, os
r=json.load(open("analysis.json")); S=r["steps"]; V=r["validation"]
U={"R1D1":"U28","R1D2":"U29","R1D3":"U31","R2C0":"U33","R2C1":"U35"}
def unit(lab):
    c,q=lab.split("."); q=int(q[1]); base=U[c]
    if c=="R1D1": return "U28"
    n=int(base[1:]); return "U%d"%(n+(1 if q>=3 else 0))
OUT=_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming3')
EV="research/dig/incoming3/work_b3r3/analyze.py; research/dig/incoming3/work_b3r3/b3steps.py; research/dig/incoming3/work_b3r3/analysis.json; research/blake3_r3/candidate_blake3/experiments/rho.py"
valtxt=("validation first: filed scalar digest vs organizer verifier/blake3.py matched %d/300 random 64-byte messages at 7, 3, 2 and 1 rounds; verifier empty-input 7-round hash = af1349b9...3262 (spec vector) ok; numpy tracer vs scalar %d/200; filed packed circuit selftest True (595 ops)"
        %(V["rho_vs_verifier_matches_of_300"]["7"],V["numpy_vs_scalar_ok_of_200"]))
n=0
for lab,s in S.items():
    call,qq=lab.split("."); q=int(qq[1]); un=unit(lab)
    words=["m%d"%(8+w) for w in s["infl_words"]]
    ops=s["ops"]; by=s["ops_by"]; byt=", ".join("%d %s"%(v,k) for k,v in by.items())
    msgw=s["msg"][0] if q<=2 else s["msg"][1]; msgv=s["msg"][2] if q<=2 else s["msg"][3]
    if q in (1,3): msgtxt="adds message word %s (%s)"%(msgw,"zero constant, add folded away" if msgv=="const0" else "variable input word")
    else: msgtxt="no message word"
    cone=len(s["infl_words"])
    exp=(2**32*(1-math.exp(-s["N"]/2**32)) if cone==1 else s["N"]*(1-s["N"]/2**65))
    pre="/".join(s["pre"]); post="/".join(s["post"])
    loc=lab
    common=dict(hash="blake3-r3",row_i=None,row_j=None,source="our workflow: dig-scan-b3r3",own_test=True,evidence=EV,date="2026-10-12",lever=False,gain_bits=None)
    alt=s["alts"]
    # Q1
    recs={}
    recs["Q1"]=dict(question="Q1 value/count as used: what does the filed 595-operation circuit spend on %s and on what inputs?"%loc,labels=["N"],status="COMPUTED",
      number="%d operations per 7-lane batch (%s) = %.2f%% of 595 = %.3f ops per instance; %s; state words (a,b,c,d) entering the step are %s (c = constant, vN = lane bound below 2^N), leaving %s; masks inserted at this step: %d"%(ops,byt,100*ops/595,ops/7,msgtxt,pre,post,s["masks"]),
      notes=valtxt+". Counting uses the filed Tracer (subclass with step tags); totals reproduce 595 = 100 add + 88 xor + 80 shr + 80 shl + 80 or + 167 and. Round 1 = first round; call Dk = diagonal k, Ck = column k; q1=(a,d) with message x, q2=(c,b), q3=(a,d) with message y, q4=(c,b).",
      held_fixed="filed circuit: 7 lanes x 36 bits, add order as filed, rotation = shr/and/shl/and/or, constants folded, target 0^32||x, flags 11, 3 rounds",
      reopen_if="the filed circuit changes (pitch, rotation recipe or constant folding) so that the per-step count differs from %d"%ops)
    # Q2
    recs["Q2"]=dict(question="Q2 necessity: if %s were removed or free, what changes?"%loc,labels=["N"],status="COMPUTED",
      number="free-step ceiling: %d of 599.19 ops per main-loop batch (599 + 3/16 loop) x 0.9944 main share = %.4f bit of time_log2 (125.1087 would become %.4f) if the step cost nothing - impossible, because it is part of the function; replacing the step by the identity changed the digest for %d of 1024 random x (mean Hamming distance %.1f of 256), so it cannot be dropped without changing the target"%(ops,s["gain_ceiling_bits"],125.1087-s["gain_ceiling_bits"],s["skip_changed_of_1024"],s["skip_mean_hd"]),
      notes=valtxt+". Ceiling only; no cheaper equivalent computation is claimed. gain_bits left null: no real saving.",
      held_fixed="all other steps and the ledger (main loop 99.44%% of total); 1024 random x for the identity-replacement test",
      reopen_if="a cheaper exact computation of this step's outputs is found (then the ceiling %.4f bit is the most it could be worth)"%s["gain_ceiling_bits"])
    # Q3
    if cone==1:
        dof="the step outputs depend on exactly one input word (%s, %d bits); (a,d) outputs of %d random x gave %d distinct pairs against %.0f expected for an injective function of one 32-bit word (birthday duplicates of the input only): the step is a bijection of that word, 32 degrees of freedom, no collision structure"%(words[0],s["infl_bits"],s["N"],s["distinct"],exp); lab3=["I"]
    else:
        dof="the step outputs depend on %d input words (%s; %d of 256 input bits change an output in 128 samples each) and image size is full: %d distinct output pairs of %d random x against %.0f expected for uniform 64 bits; mean flipped output bits per influencing input bit flip %.1f (word 1) / %.1f (word 2)"%(cone,", ".join(words),s["infl_bits"],s["distinct"],s["N"],exp,s["mean_flip_out0"],s["mean_flip_out1"]); lab3=["N"]
    recs["Q3"]=dict(question="Q3 degrees of freedom or score-optimal value at %s"%loc,labels=lab3,status="SAMPLED",
      number=dof+". Score-optimal formulation at this step: the filed one (see Q4: no tested variant is cheaper)",
      notes=valtxt+". Cone measured by flipping each of the 256 input bits on 128 random x (sampled, a silent bit would need more samples to rule out a rare dependence); distinct count over 2^21 random x.",
      held_fixed="random x over all 256 bits, constant key 0^32, flags 11",
      reopen_if="a pair of inputs is found whose step outputs coincide although the inputs differ in the cone (collision structure), or a dependence outside the listed words")
    # Q4
    a=alt
    recs["Q4"]=dict(question="Q4 alternatives: does any other formulation of %s cost fewer operations?"%loc,labels=["Z"],status="COMPUTED",
      number="tested with the filed tracer: add operands sorted ascending or descending by bound: total 595 and 595 (no change, step stays %d ops); lane pitch 36 (filed) 595, pitch 35 603, 34 622, 33 684 total (%d/%d/%d/%d ops at this step, masks %d/%d/%d/%d): a smaller guard width only adds masks, 7 lanes x 36 is the maximum for 256-bit words. Hand check: folding a constant xor through the rotation (ror(d)^ror(a) for constant d) and fusing or into add give the same count. The 3 masks of the filed circuit sit at R3D1.q3, R3D2.q3, R3D3.q3 (round 3), not here, so no mask at this step is removable"%(ops,a["lim36" if "lim36" in a else "asc"]["here"] if False else ops,a["lim35"]["here"],a["lim34"]["here"],a["lim33"]["here"],s["masks"],a["lim35"]["masks_here"],a["lim34"]["masks_here"],a["lim33"]["masks_here"]),
      notes=valtxt+". Alternatives are a small family (operand order, pitch, rotation distribution), not a search over all circuits; 'no cheaper' is for this family only.",
      held_fixed="rotation recipe 5 ops, 7 lanes, constants folded, digest masks 4",
      reopen_if="a rotation or mask recipe below 5 ops per rotation or a lane layout above 7 lanes is found")
    for Q,rec in recs.items():
        d=dict(common); d.update(rec); d["object"]="step %s (G call %s quarter-step q%d)"%(loc,call,q)
        d["id"]=None; del d["id"]
        d["cell"]="blake3-r3|%s|step|%s"%(loc,Q)
        d["notes"]=d["notes"]
        fn=os.path.join(OUT,"blake3-r3-%s"%un); os.makedirs(fn,exist_ok=True)
        json.dump(d,open(os.path.join(fn,(d["cell"].replace("|","_"))+".json"),"w"),indent=1); n+=1
print(n)
