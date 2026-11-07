from pathlib import Path
import sys
p=Path(__file__).parent
N=int(sys.argv[1]);T=list(map(int,sys.argv[2].split(',')));K=int(sys.argv[3])
s=[]
s+=['(define-fun s0 ((x (_ BitVec 32))) (_ BitVec 32) (bvxor (bvxor ((_ rotate_right 7) x) ((_ rotate_right 18) x)) (bvlshr x #x00000003)))','(define-fun s1 ((x (_ BitVec 32))) (_ BitVec 32) (bvxor (bvxor ((_ rotate_right 17) x) ((_ rotate_right 19) x)) (bvlshr x #x0000000a)))']
for i in range(N):
 for a in ('a','b'):s.append(f'(declare-fun {a}{i} () (_ BitVec 32))')
 if i>=16:s.append(f'(assert '+ ('(not ' if i in T else '')+f'(= a{i} b{i})'+(')' if i in T else '')+')')
for a in ('a','b'):
 for i in range(16,N):s.append(f'(assert (= {a}{i} (bvadd (bvadd (s1 {a}{i-2}) {a}{i-7}) (bvadd (s0 {a}{i-15}) {a}{i-16}))))')
bits=[]
for i in list(range(16))+T:
 for j in range(32):bits.append(f'(not (= ((_ extract {j} {j}) a{i}) ((_ extract {j} {j}) b{i})))')
s.append('(assert ((_ at-most '+str(K)+') '+' '.join(bits)+'))')
name=f'modbound_N{N}_T'+'_'.join(map(str,T))+f'_le{K}'
(p/(name+'.smt2')).write_text('\n'.join(s))
