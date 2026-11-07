# minpoly (Wiedemann + GPU Berlekamp-Massey) status, 2026-10-13

Method: mp.cu (built on certb_fast engine). g = F' made monic, Fr = F mod g + random constant, s_k = <w, Fr^k mod g> for k < 2D
(one NTT mulmod with fixed multiplier spectrum per step), then division-free Berlekamp-Massey on the GPU. Degree L of the
generator = deg of minpoly of Fr in A (w.h.p.); L = D proves the D critical values are pairwise distinct
(L is a lower bound for deg minpoly <= D, so L = D is deterministic given correct s_k).

## Validation vs python-flint (t_mp.py, t_mp.log)
Reference: R(T) = Res_W(F'(W), T - F(W)) by evaluation + Lagrange interpolation, radical degree = number of distinct values.
All 8 cases, two seeds each, GPU degree == reference distinct count, generator annihilates Fr mod F' (compose_mod == 0),
and s_k spot-checked against flint pow_mod:
- random n=26/126/626: degree 25/125/625 (distinct)
- planted one collision (t solved linearly) n=26/126/626: 24/124/624 (D-1)
- even F (many collisions) n=26/126: 13/63

## Real F (tests/data/F_j0.bin, D = 78124)
Run seed 1 (completed, GPU shared, 3-4.4 ms per mulmod step): sequence 2D = 156248 terms in about 630 s, BM 16 s, total 645.7 s.
Result: minpoly degree 78124 = D, collisions 0 -> critical values DISTINCT.
Run seed 2: started, killed by coordinator (GPU VRAM pressure on owner's PC). Not completed, not relaunched.
Not done: flint spot-check of s_k at full size (only tested at n <= 626).
Files: real_s1.log, data/real_s1_{w,fr,s,C}.bin.
