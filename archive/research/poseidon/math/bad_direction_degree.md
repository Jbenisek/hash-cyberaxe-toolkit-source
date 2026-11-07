# Bad-direction degree test (toy, q=1,000,003)
Script: bad_direction_degree.py (exact mod-q polynomial arithmetic, numpy convolution). Bad alpha* from Luna3 P3_19 results (n.alpha*=0, slopes 30903/182900/270361). z(T)=alpha*T^e + random lower terms, coordinate 2 fixed by n.z=B (checked per coefficient). s2=M z^[5]; then round 2 full, rounds 3,4 partial (lane 0), round 5 full; digest = lane 0. g0 = lane-0 input to round 3 sbox, g1 = lane-0 input to round 4 sbox.

| slope | e | delta | deg g0 | deg g1 | deg digest | 625*delta |
|---|---|---|---|---|---|---|
| 30903 | 1,2,3 | 5,10,15 | 25,50,75 | 125,250,375 | 3125,6250,9375 | equal |
| 182900 | 1,2,3 | 5,10,15 | 25,50,75 | 125,250,375 | 3125,6250,9375 | equal |
| 270361 | 1,2,3 | 5,10,15 | 25,50,75 | 125,250,375 | 3125,6250,9375 | equal |

Result: digest degree = 625*delta exactly in all 9 cases; none below. The bad direction only zeroes lane 0 of the leading form of s2 (C^1(alpha)_0), which is not the lane that is S-boxed in the partial round: g0 = lane 0 of M*(s2+c2)^5, whose top coefficient is C^2(alpha)_0 = Q(alpha) != 0 (Q rootless, gcd 1), and it depends on alpha only, so no choice of lower-order terms can lower deg g0 (step 2: nothing to solve; minimum = 625*delta). g1, digest follow with M[0,0]!=0, E_J!=0.
Pallas: not run (condition "toy shows digest below 625*delta" not met).
Not tested: the three lines L_h(T)=v_h T+w_h (not in Luna's files), z with leading coordinates of unequal degree, extension-field directions.
