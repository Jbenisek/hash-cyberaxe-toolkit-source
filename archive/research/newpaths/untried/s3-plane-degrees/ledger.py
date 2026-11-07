"""Ledger effect of lowering the FES degree of chi6-input planes (D19 section 5 formula; section 9 total).
Per plane per Gray step the FES cost is 3L+1 with L = min(D, popcount(step)), so lowering D from 8 to 7 (or 6) saves
3 * #{i in [1, 2^40-1] : popcount(i) >= 8}  (plus #{popcount >= 7} for 6) ops per plane per 256-coset group.
Candidates per group = 256 cosets x 2^40 points = 2^48 (assumption, consistent with Fv/2^48 = 16.785 ops/candidate).
Measured result (this folder): 0 planes qualify, so the saving is 0; the rows below are the CEILING if planes had qualified."""
from math import comb, log2
n = 40
S = lambda L: sum(comb(n, j) * min(L, j) for j in range(n + 1))
S8, S7, S6 = S(8), S(7), S(6)
assert S8 == 8796064307936                      # D19 section 5 constant
Nv = 19621183271953275558043014167496083929897  # D19 section 9
per_cand = 57.946279567138                      # D19 section 9
cand = Nv / per_cand
Fv = 175 * (3 * S8 + (2 ** 40 - 1)) - 78 * (2 ** 40 - 1)
assert Fv == 4724586389560575
print(f'S8={S8} S7={S7} S6={S6}; S8-S7={S8 - S7} S8-S6={S8 - S6}')
print(f'candidates = Nv/charge = 2^{log2(cand):.6f}; Fv per candidate = {Fv / 2**48:.6f}')
for name, d in (('8->7', S8 - S7), ('8->6', S8 - S6)):
    per_plane = 3 * d / 2 ** 48                 # ops per candidate saved per plane
    for planes, label in ((1, 'one plane'), (5, 'one z (5 planes)'), (175, 'all 175 key-cone planes')):
        new = per_cand - planes * per_plane
        print(f'{name} {label:26s}: saves {planes * per_plane:.6f} ops/candidate -> '
              f'{log2(per_cand / new):.6f} bit -> time_log2 {123.18243 - log2(per_cand / new):.5f}')
print('measured: qualifying planes = 0, qualifying z = 0 -> saving 0 ops/candidate, 0 bit, time_log2 stays 123.18243')
