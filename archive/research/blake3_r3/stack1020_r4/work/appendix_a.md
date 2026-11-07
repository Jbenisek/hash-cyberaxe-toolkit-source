The ledger was recomputed by a separate program in integers and fractions, with the constants of Sections 3 and 7 (the gate count 23479, the packed circuit 845, the generator calls 344,207 per pass and the key-choice charge are taken from `python3 bsrho.py --ledger` and `--choose-key`); it reproduces the program's N exactly:
```
code bytes = 135582  tmax = 126121  key bits = 51  Tp = 1936  B = 1324569435497000000000000000000000000
c = 54926776685327102186107729763650603  c_r = 34054601544902803355386792453463374  D = 4157055852649267987718114313167
e2max = 157900981366276741027832031314  pmax = 80339480069056697871027175870700129
memory bytes (search phase) = 1048516
main loop: (B + 3000) * 23492                                               31116785178695524000000000000000070476000
stage-1 rest: pmax * 23                                                     1847808041588304051033625045026102967
slice checks: ceil((B + 3000) / 2^48) * 1300                                6117560737614624599701400
stage-1 hits: e2max * 2800                                                  442122747825574874877929687679200
finished trails: tmax * (3800 + 64 (tmax + 1))                              1018503756568
cut trails: 1 * 4200                                                        4200
recovery: c_r (845 + 38) + 8192 * 80 + 17 D (845 + 39) + 16 * 100 + 600    30132685399502788562125965558307090478
setup and generator                                                         143192200
choice of the prefix key                                                    17750836600
N = 31148766114259369035748772084194088839613
certificate: 2^12479178 * 846^100000 <= N^100000 < 2^12479179 * 846^100000
time_log2 = 124.79179
```
The power certificate is checkable in integer arithmetic: 2^12479178 * 846^100000 <= N^100000 < 2^12479179 * 846^100000 gives 124.79178 <= log2(N / 846) < 124.79179, and the claim is the upper end.
Success bound. The terms of Lemma 2 were evaluated in exact rationals for every rational quantity and in 60-digit decimal arithmetic for every exp and ln, each result moved outward by a relative 1e-40 (upper bounds rounded up, Pi_m enclosed from both sides, the bins of P_delay as in Step 5); the asserted conditions are 0.108 Q / 2^32 > 1000, 240 M <= Q, 2^-22 mu3 / 3 > 1000, 2 M / 2^12 + 3001 P12 <= 2^-11 mu3 and 0.386 M / 2^12 > 1000:
```
P_coll 6.086563658178e-01   P_delay 1.256881284858e-03   P_own 8.042478763939e-06   P_long 4.101950208152e-08
P_age 2.149068015238e-08   P_rec 5.480292293053e-05   P_dist 3.993102209192e-06   N1 >= k: 9.094947017729e-13
P_cut: Bin 3.390650340685e-08 + E_S 8.042478763939e-06 + E_X 2.952349551436e-08 + E_J2a 7.986204418384e-06 + E_J2b 2.149068015238e-08 + E_Y 1.023365721542e-09
P_key 3.736252274619e-06   P_table 1.835583886528e-12   P_tiny 8.077947124836e-28
k = 126096, n2 = 126353, q = 123469.7523, PP = H = 0.4965014, mu3 = 8.0261e+34, M = c + 2^48 + 3000
P_F >= 0.39000000100097 >= 0.39
```
