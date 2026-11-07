import sys,pickle,math,os
sys.path.insert(0,'.')
import a0l_var as A
cal=pickle.load(open('cal.pkl','rb'))
def T(c):
    rows,info=A.ledger(cal=c,show=False); return math.log2(sum(int(v) for _,v in rows))-math.log2(2728)
T0=T(cal)
c=dict(cal); c['prog']={g:400000 for g in cal['prog']}
print('LB all 7 programs at 400000 instr:',T(c)-T0)
c=dict(cal); c['prog']={g:(400000 if g>=2 else v) for g,v in cal['prog'].items()}
print('LB progs 2-6 only (14 slots):',T(c)-T0)
