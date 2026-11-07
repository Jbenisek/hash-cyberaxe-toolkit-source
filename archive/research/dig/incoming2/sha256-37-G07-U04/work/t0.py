import sys,time
sys.dont_write_bytecode=True
import lowm as lw
t=time.time(); env=lw.Env(); print('env',time.time()-t)
rng=lw.Shake('scanonce-wave2|G07U04|timing'); t=time.time(); n=0; tot=0
while time.time()-t<20:
    w=lw.first_block(lw.Mach(),rng); cv=lw.compress(lw.IV,w); mc=lw.Mc(); st={}
    lw.process_cv(mc,cv,env,st); tot+=mc.n+46; n+=1
print(n,'blocks',tot/n)
