from pathlib import Path
import json
p=Path(__file__).parent
R=json.loads((p/'linear_min_infosets.json').read_text())
for r in R:
 N=r['N'];T=r['T'];D=[int(w,16)for w in r['words']]
 out=[]
 out+=['(define-fun s0 ((x (_ BitVec 32))) (_ BitVec 32) (bvxor (bvxor ((_ rotate_right 7) x) ((_ rotate_right 18) x)) (bvlshr x #x00000003)))','(define-fun s1 ((x (_ BitVec 32))) (_ BitVec 32) (bvxor (bvxor ((_ rotate_right 17) x) ((_ rotate_right 19) x)) (bvlshr x #x0000000a)))']
 for t,d in enumerate(D):
  out.append(f'(declare-fun a{t} () (_ BitVec 32))')
  out.append(f'(define-fun b{t} () (_ BitVec 32) (bvxor a{t} #x{d:08x}))')
 for pref in ('a','b'):
  for t in range(16,N):
   out.append(f'(assert (= {pref}{t} (bvadd (bvadd (s1 {pref}{t-2}) {pref}{t-7}) (bvadd (s0 {pref}{t-15}) {pref}{t-16}))))')
 name=f'lift_N{N}_T'+ '_'.join(map(str,T))
 (p/(name+'.smt2')).write_text('\n'.join(out))
