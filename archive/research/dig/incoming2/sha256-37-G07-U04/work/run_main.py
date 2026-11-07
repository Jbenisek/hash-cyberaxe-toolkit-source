import sys,time,csv
sys.dont_write_bytecode=True
import lowm as lw
tmax=float(sys.argv[1]); out=sys.argv[2]; seed=sys.argv[3]; nmax=int(sys.argv[4]); mut=len(sys.argv)>5
if mut: lw.GROUP_BODY=32
env=lw.Env(); rng=lw.Shake(seed); t0=time.time(); n=0
f=open(out,'w',newline=''); w=csv.writer(f)
w.writerow('classes pairs groups survl survlanes r16 total ct scan_etc cprep sweep w6 spill runs member pad group probe surv rare nonpassfixed'.split())
while n<nmax and time.time()-t0<tmax:
    wd=lw.first_block(lw.Mach(),rng); cv=lw.compress(lw.IV,wd); mc=lw.Mc(); st={}
    lw.process_cv(mc,cv,env,st)
    c=mc.cat; cn=mc.cnt
    pad=lw.PAD_OPS if cn.get('pad') else 0
    w.writerow([st.get('classes',0),st.get('pairs',0),cn.get('groups',0),cn.get('survl',0),cn.get('survlanes',0),st.get('r16',0),mc.n+46,
      c.get('ct',0),c.get('scan',0),c.get('cprep',0),c.get('sweep',0),c.get('w6',0),c.get('spill',0),c.get('runs',0),c.get('member',0),pad,c.get('group',0),c.get('probe',0),c.get('surv',0),c.get('rare',0),
      (mc.n+46)-sum(c.get(k,0) for k in c)  ])
    n+=1
f.close(); print(n,'blocks',round(time.time()-t0),'s')
