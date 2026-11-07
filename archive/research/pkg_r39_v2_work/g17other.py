import sys, importlib.util
sp = importlib.util.spec_from_file_location("j", sys.argv[1]); J = importlib.util.module_from_spec(sp); sp.loader.exec_module(J)
M=J.M; BA,BE,CA,CE,MP,MM=J.BA,J.BE,J.CA,J.CE,J.MP_PUB,J.M_PUB
A0,E0,W0=BA[:20],BE[:20],MP[:16]; A1,E1,W1=CA[:20],CE[:20],MM[:16]
dsch16=((J.s1(MM[14])+MM[9]+J.s0(MM[1]))-(J.s1(MP[14])+MP[9]+J.s0(MP[1])))&M
g16,_=J.solve_row_exact(A0,E0,W0,A1,E1,W1,16); out=[]
for g in g16:
  w0,w1=g,(g+dsch16)&M
  t10=(E0[16]+J.S1(E0[19])+J.CH(E0[19],E0[18],E0[17])+J.K[16]+w0)&M;t20=(J.S0(A0[19])+J.MAJ(A0[19],A0[18],A0[17]))&M
  t11=(E1[16]+J.S1(E1[19])+J.CH(E1[19],E1[18],E1[17])+J.K[16]+w1)&M;t21=(J.S0(A1[19])+J.MAJ(A1[19],A1[18],A1[17]))&M
  g17,_=J.solve_row_exact(A0+[(t10+t20)&M],E0+[(A0[16]+t10)&M],W0+[w0],A1+[(t11+t21)&M],E1+[(A1[16]+t11)&M],W1+[w1],17)
  out.append("%08x:%s"%(g,[hex(x) for x in g17]))
print(sys.argv[1][-40:], out)
