import lowm_w as L, math, json
w=0; rows={}
for k in 'AEW':
    for i in range(16,L.R):
        m,v,d,p=L.CELLS[k][i]
        n=sum(1 for x in (m,v,d) if x)+(1 if (k=='E' and p) else 0)
        w+=n
    # rows 0..15 also read in row_ok for the y/x checks of rare path? rows<16 are in step3b not re-checked (rows from 16)
print('nonzero cell words rows 16..36:',w)
x2=sum(1 for t in L.X2 if max(t[1],t[5])>=16); print('two-bit relations on rows >=16:',x2)
S=28; Lt=32*(8+8+3); mxy=32; lw=32
print('S words (SA,SE rows 0..13)',S,'Lt words (x/y rows 12..15 A,E + base,C16,dW16) x32',Lt,'MX,MY',mxy,'LW15',lw)
tot=w+x2*2+S+Lt+mxy+lw
print('total data words the model reads ~',tot,'bytes at 32 B/word',tot*32,'bound 1280 words =',1280*32)
for i,(nm,b) in enumerate([('perl_consts',4096),('SLstar_hold_bound',40960)]): pass
def Bstar(b,dT): return b/(2**dT-1)
r=json.load(open('perscal_results.json')); sc=json.load(open('scant_results.json'))
print('B* perl consts',Bstar(4096,r['perl_consts_recompute']['dT']))
print('B* SL* (bound 40960->2304)',Bstar(40960-2304,r['perl_SLstar_recompute']['dT']), 'exact-tally',Bstar(tot*32-2304,r['perl_SLstar_recompute']['dT']))
print('B* cvpre',Bstar(2048,r['scal_cvpre_per_group']['dT']))
tf16=[x for x in sc if x['kind']=='tablefree' and x['w']==16][0]
print('B* scan table vs best table-free(w16)',Bstar(65536,tf16['dT']))
t8=[x for x in sc if x['kind']=='table' and x['w']==8][0]
print('B* table w11 vs w8',Bstar(65536-8192,t8['dT']))
print('2^20=',1<<20,'headroom',(1<<20)-607744,'slope bit/B above 2^20',1/(math.log(2)*(1<<20)))
