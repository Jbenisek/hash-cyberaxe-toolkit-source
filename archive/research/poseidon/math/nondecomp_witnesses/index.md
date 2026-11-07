# Non-decomposition witnesses, Orchard line polynomial F_j (r=1, degree 5^7 = 78125), 2026-10-12

For each j and inner degree m: H = candidate right component (monic, H(0)=0, degree m; unique since p > n), computed by the
validated method (levels/decomp/decomp.py: top-m coefficients -> m-th root series -> B_from_top). F = sum c_i H^i (H-adic digits,
deg c_i < m, unique). F = G(H) for some G iff every c_i is constant. Each file stores H and ONE nonconstant digit c_idx
(lowest index; idx 0 means c_0 = F mod H has positive degree), which proves F_j != G(H) for every G. Digit counts equal the
earlier recorded results (RESULT.md, decomp_625_3125.md, d15625.log). Each witness was re-verified by peeling F by H idx+1 times with divmod.

Files: nd_j{j}_m{m}.json (metadata, hashes, runtimes; H and digit inline for m<=625); for m=3125, 15625 the coefficients are in
nd_j{j}_m{m}_H.hex and _digit.hex (ascending degree, one 64-hex field element per line). Scripts: make_witnesses.py, chk_same_poly.py (log: same_poly_check.log).

| j | m | digit idx | digit degree | nonconstant digits | H sha256 (of hex list) | runtime s (H / digits / total) |
|---|---|---|---|---|---|---|
| 0 | 5 | 0 | 4 | 15624 | 8840f75ffdc024bc.. | 0.0 / 3.4 / 3.5 |
| 0 | 25 | 0 | 24 | 3121 | c9553028674f6ef3.. | 0.1 / 3.4 / 3.5 |
| 0 | 125 | 0 | 124 | 624 | cd73efecd2a4c9a3.. | 0.1 / 3.3 / 3.7 |
| 0 | 625 | 0 | 624 | 124 | d72656b6173cfb62.. | 0.2 / 2.8 / 3.5 |
| 0 | 3125 | 0 | 3124 | 24 | bf47a0287b093b15.. | 4.4 / 2.2 / 7.1 |
| 0 | 15625 | 0 | 15624 | 4 | 63a7deaaa8a4716c.. | 105.9 / 1.1 / 107.3 |
| 1 | 5 | 0 | 4 | 15624 | a53a17625d68ad54.. | 0.0 / 3.7 / 3.8 |
| 1 | 25 | 0 | 24 | 3121 | cd8b4b8e56f69e54.. | 0.0 / 3.4 / 3.5 |
| 1 | 125 | 0 | 124 | 624 | b059c6b17df8a4b5.. | 0.1 / 3.5 / 3.9 |
| 1 | 625 | 0 | 624 | 124 | fe8f6808f4e6ed48.. | 0.2 / 2.8 / 3.4 |
| 1 | 3125 | 0 | 3124 | 24 | 19d7deac9ea56b91.. | 4.5 / 2.0 / 6.9 |
| 1 | 15625 | 0 | 15624 | 4 | debc684e465887ab.. | 105.0 / 1.1 / 106.5 |
| 2 | 5 | 0 | 4 | 15624 | 62da941a3fe67022.. | 0.0 / 3.1 / 3.2 |
| 2 | 25 | 0 | 24 | 3121 | 604237b9a0a95528.. | 0.0 / 3.1 / 3.3 |
| 2 | 125 | 0 | 124 | 624 | efca7737a838fddb.. | 0.1 / 2.9 / 3.3 |
| 2 | 625 | 0 | 624 | 124 | efae1e1cd0848ecd.. | 0.2 / 2.5 / 3.1 |
| 2 | 3125 | 0 | 3124 | 24 | 23c449706390bf24.. | 4.1 / 2.0 / 6.5 |
| 2 | 15625 | 0 | 15624 | 4 | 3954d382c5ce696d.. | 104.0 / 1.1 / 105.5 |
